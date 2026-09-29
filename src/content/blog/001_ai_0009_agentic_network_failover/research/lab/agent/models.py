#!/usr/bin/env python3
"""
models.py - the two LangChain chat models.

JevChatModel      TypeSafe Jev over POST /zen/v1/systemone. That endpoint is not
                  a chat API, so it is wrapped here as a real langchain_core
                  BaseChatModel and can be used anywhere in the graph.

build_bunny_model Space Bunny over the OpenAI-compatible /chat/completions,
                  with tool calling bound in.

NO FALLBACK. Every failure raises.
"""
import json
import os
import random
import time
import warnings
from typing import Any, Dict, List, Optional

import httpx
from langchain_core.callbacks import BaseCallbackHandler, CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

warnings.simplefilter("ignore")  # lab: proxy MITM, verification off by request

# Two different products sit behind two different paths. Do not merge these.
#
#   ZEN    is OpenCode Console (pay-as-you-go). Jev lives here:
#          POST /zen/v1/systemone with jev-1.13 returns 200.
#   ZEN_GO is OpenCode Go (subscription). The free models live here:
#          the identical space-bunny-free call that returns 403 on
#          /zen/v1/chat/completions returns 200 on /zen/go/v1/chat/completions.
#          Same key, same model ID, same body. The path is the only difference.
ZEN = os.environ.get("ZEN_BASE", "https://opencode.ai/zen/v1").rstrip("/")
ZEN_GO = os.environ.get("ZEN_GO_BASE", "https://opencode.ai/zen/go/v1").rstrip("/")

# The Go gateway refuses to route anything without this header and answers
# 400 {"type":"MissingSessionID"}. Keep it stable for the life of one
# conversation so the provider can route and cache correctly.
BUNNY_SESSION = os.environ.get("BUNNY_SESSION", "jevshowcase-lab")
JEV_MODEL = os.environ.get("JEV_MODEL", "jev-1.13")
BUNNY_MODEL = os.environ.get("BUNNY_MODEL", "space-bunny-free")

# space-bunny-free is a reasoning model: at max_tokens=3000 it spends the whole
# budget on reasoning_content and returns an EMPTY content field.
BUNNY_MAX_TOKENS = 12000

# Status codes worth retrying. 4xx other than 408/425/429 are real errors:
# a 400 from the gateway (we hit one with a bad parameter) will never succeed
# on a retry, and 401/403 will never be fixed by waiting.
RETRYABLE = {301, 302, 307, 308, 408, 425, 429, 500, 502, 503, 504}

RETRY_TRIES = int(os.environ.get("API_RETRY_TRIES", "10"))
RETRY_BASE = float(os.environ.get("API_RETRY_BASE", "2.0"))
RETRY_MAX_SLEEP = float(os.environ.get("API_RETRY_MAX_SLEEP", "20.0"))


class ModelError(RuntimeError):
    """Every model failure raises. The lab has no fallback path: if a model
    cannot be reached or cannot be parsed, the run aborts rather than
    inventing an answer."""

class RetryTransport(httpx.HTTPTransport):
    """Retries the transient failures this egress path actually produces.

    The filtering proxy answers 3xx (307 Authentication Required) and
    occasionally 429/5xx. Neither httpx nor the openai client retries a 3xx, so
    it is handled here, with exponential backoff and jitter so parallel calls do
    not resynchronise into a thundering herd.

    It also records what it retried, so the decision trail shows the flakiness
    instead of hiding it behind a longer wall clock.
    """

    def __init__(self, tries=None, **kw):
        super().__init__(**kw)
        self.tries = tries if tries is not None else RETRY_TRIES
        self.stats = {"calls": 0, "retries": 0, "by_status": {}}

    def _backoff(self, attempt):
        delay = min(RETRY_BASE * (2 ** attempt), RETRY_MAX_SLEEP)
        return delay * (0.5 + random.random() * 0.5)   # jitter

    def handle_request(self, request):
        self.stats["calls"] += 1
        last = None
        for attempt in range(self.tries):
            try:
                resp = super().handle_request(request)
            except (httpx.ConnectError, httpx.ReadError,
                    httpx.RemoteProtocolError) as e:
                # connection level flakiness: back off and try again
                self.stats["retries"] += 1
                key = type(e).__name__
                self.stats["by_status"][key] = \
                    self.stats["by_status"].get(key, 0) + 1
                last = e
                if attempt == self.tries - 1:
                    raise
                time.sleep(self._backoff(attempt))
                continue

            if resp.status_code not in RETRYABLE:
                return resp

            self.stats["retries"] += 1
            key = str(resp.status_code)
            self.stats["by_status"][key] = self.stats["by_status"].get(key, 0) + 1
            last = resp
            try:
                resp.read()
            except Exception:
                pass
            resp.close()
            if attempt < self.tries - 1:
                time.sleep(self._backoff(attempt))
        if isinstance(last, Exception):
            raise last
        return last


_JEV_CLIENT = None


def _jev_client():
    """One persistent client for the whole run. Opening a new TLS connection
    per request is what the filtering proxy answers with 307."""
    global _JEV_CLIENT
    if _JEV_CLIENT is None or _JEV_CLIENT.is_closed:
        _JEV_CLIENT = _http_client()
    return _JEV_CLIENT


def _http_client(tries=None):
    """Cert validation off, and the corporate proxy actually used.

    This used to bypass the proxy on purpose, because direct egress
    to opencode.ai used to work. It no longer does. Measured from
    inside the agent container:

        direct   -> 302 to 10.122.106.86:15871/.../blockpage.cgi
                     (the web filter) and 307 to sheua017-wcg:8080/auth/
                     (the proxy login portal), after 85-107s of retries
        via proxy -> 200 in about one second, same body, same key

    Handing httpx an explicit transport makes it ignore the client-level
    proxy= and verify= arguments, so both have to be given to the
    transport itself rather than to the Client.
    """
    proxy = (os.environ.get("HTTPS_PROXY")
             or os.environ.get("https_proxy") or "")
    return httpx.Client(
        timeout=60.0,
        transport=RetryTransport(tries=tries, verify=False,
                                 proxy=proxy or None),
    )

class JevChatModel(BaseChatModel):
    """One log line in, one verdict out. Jev names the state, so there is no
    numeric threshold to tune."""

    model_name: str = JEV_MODEL
    instructions: str = "Classify this single log line as normal or failed."
    criteria: Dict[str, str] = {
        "normal": "the line reports normal, healthy, routine operation",
        "failed": "the line reports a failure, error, fault or unreachability",
    }

    @property
    def _llm_type(self) -> str:
        return "typesafe-jev"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model_name}

    def _generate(self, messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None,
                  **kwargs: Any) -> ChatResult:
        state = messages[-1].content
        if isinstance(state, list):
            state = "".join(
                p.get("text", "") for p in state if isinstance(p, dict))

        key = os.environ.get("OPENCODE_API_KEY", "").strip()
        if not key:
            raise ModelError("OPENCODE_API_KEY not set")

        questions = {
            "verdict": {
                "type": "choice",
                "criteria": self.criteria,
                "instructions": self.instructions,
            }
        }
        payload = {"model": self.model_name, "state": state,
                   "questions": questions}
        headers = {"Authorization": "Bearer " + key,
                   "Content-Type": "application/json"}

        # RetryTransport does the real work: it retries the transient statuses
        # with exponential backoff. This outer loop is only a safety net for
        # failures the transport cannot see, such as a client that never got a
        # response at all. A 4xx that is genuinely wrong raises immediately:
        # waiting cannot fix a bad request.
        outer = 3
        data, latency, attempts = None, 0.0, 0
        last_status = None
        for attempt in range(1, outer + 1):
            t0 = time.time()
            try:
                c = _jev_client()
                r = c.post(ZEN + "/systemone", json=payload,
                           headers=headers)
            except Exception as e:
                last_status = type(e).__name__
                if attempt < outer:
                    time.sleep(RETRY_BASE * attempt)
                continue
            if r.status_code in RETRYABLE:
                # the transport already exhausted its tries on this status
                last_status = str(r.status_code)
                if attempt < outer:
                    time.sleep(RETRY_BASE * attempt)
                continue
            if r.status_code >= 400:
                raise ModelError("Jev HTTP %d: %s"
                                 % (r.status_code, r.text[:300]))
            try:
                data = r.json()
            except Exception as e:
                raise ModelError("Jev JSON decode failed: %s" % e)
            latency = round(time.time() - t0, 3)
            attempts = attempt
            break

        if data is None:
            tr = _JEV_CLIENT
            stats = getattr(getattr(tr, "_transport", None), "stats", None) if tr else None
            raise ModelError(
                "Jev unreachable: %d outer attempts x %d transport retries, last=%s, stats=%s"
                % (outer, RETRY_TRIES, last_status, stats))


        answers = data.get("answers")
        if not isinstance(answers, dict) or "verdict" not in answers:
            raise ModelError("Jev returned no verdict: %s" %
                             json.dumps(data)[:250])
        v = answers["verdict"]
        if not isinstance(v, dict) or "choice" not in v:
            raise ModelError("Jev verdict malformed: %r" % (v,))
        choice = v.get("choice")
        if choice not in self.criteria:
            raise ModelError("Jev chose unknown verdict %r" % (choice,))

        content = json.dumps({
            "choice": choice,
            "confidence": v.get("confidence"),
            "probabilities": v.get("probabilities", {}),
            "latency_s": latency,
            "attempts": attempts,
        })
        msg = AIMessage(content=content)
        return ChatResult(
            generations=[ChatGeneration(message=msg)],
            llm_output={"model": data.get("model", self.model_name),
                        "usage": data.get("usage", {})})


def _fmt_state(rows):
    """Render path_state() rows for the prompt. Absent routes are stated
    explicitly rather than omitted, so Jev can see that a path has no route at
    all instead of assuming it was simply not mentioned."""
    out = []
    for st in rows or []:
        if not st["installed"]:
            out.append("    %-7s next hop %-13s  NO ROUTE INSTALLED"
                       % (st["path"], st["next_hop"]))
            continue
        out.append("    %-7s next hop %-13s  distance %-4d %s"
                   % (st["path"], st["next_hop"], st["distance"],
                      "ACTIVE NOW" if st["active"] else "installed, standby"))
    return chr(10).join(out)


def judge_path(faulty, rc1_rows, rc2_rows, diagram):
    """Ask Jev which path should carry traffic now. Returns a path id or raises.

    Deliberately not a fallback: if Jev cannot be reached, or answers with
    anything that is not one of the known path ids, this raises ModelError and
    the run aborts. A wrong guess here is worse than no answer at all.
    """
    from topology import PATHS

    # A path is only usable if BOTH directions have a route for it.
    # Using "either router" here is a trap: a healthy rc2 keeps a
    # route installed for a path whose forward half is dead, and that
    # resurrects a path that cannot carry traffic. Caught by a test
    # where rc1 was cut off entirely.
    def _installed(rows, pid):
        return any(r["path"] == pid and r["installed"]
                   for r in (rows or []))

    usable = [pid for pid in PATHS
              if _installed(rc1_rows, pid)
              and _installed(rc2_rows, pid)]
    if not usable:
        raise ModelError("neither path has a route installed: %s" % faulty)

    criteria = {pid: PATHS[pid]["label"] for pid in usable}

    state = chr(10).join([
        "A failover has just been detected.",
        "",
        "Routers the first pass judged FAILED: %s" % (", ".join(faulty) or "none"),
        "",
        "Routing state read from the devices themselves:",
        "",
        "  rc1 to the server network:",
        _fmt_state(rc1_rows),
        "",
        "  rc2 back to the client network:",
        _fmt_state(rc2_rows),
        "",
        "Topology:",
        diagram,
        "",
        "A path carrying traffic cannot include a router that has failed.",
        "Choose the one path from the list that should carry traffic now.",
    ])

    instructions = ("Which single path should carry the traffic right now? "
                    "Answer with exactly one path id.")

    model = JevChatModel(criteria=criteria, instructions=instructions)
    resp = model.invoke(state)
    v = json.loads(resp.content)
    choice = v["choice"]

    if choice not in PATHS:
        raise ModelError("Jev chose unknown path %r, expected one of %s"
                         % (choice, sorted(PATHS)))
    if choice not in usable:
        raise ModelError("Jev chose path %s which has no installed route, "
                         "usable were %s" % (choice, usable))

    return {"path": choice,
            "label": PATHS[choice]["label"],
            "confidence": v["confidence"],
            "probabilities": v.get("probabilities"),
            "latency_s": v.get("latency_s"),
            "usable": usable,
            "state": state}


def build_jev() -> JevChatModel:
    return JevChatModel()


def build_bunny_model() -> ChatOpenAI:
    key = os.environ.get("OPENCODE_API_KEY", "").strip()
    if not key:
        raise ModelError("OPENCODE_API_KEY not set")
    return ChatOpenAI(
        model=BUNNY_MODEL,
        # Go, not Console. See ZEN_GO above.
        base_url=ZEN_GO,
        # Mandatory for the Go gateway; without it every call is a 400.
        default_headers={"x-opencode-session": BUNNY_SESSION},
        api_key=key,
        max_tokens=BUNNY_MAX_TOKENS,
        temperature=0.1,
        streaming=False,
        max_retries=RETRY_TRIES,
        extra_body=BUNNY_EXTRA or None,
        http_client=_http_client(),
        timeout=60.0,
    )


# ---- reasoning suppression ---------------------------------------------
#
# Measured against the live Go endpoint: BUNNY_EXTRA has NO effect.
#
# An earlier comment here claimed a median drop from 1831 reasoning tokens
# to 674 over 8 samples. Those samples were taken against /zen/v1, where
# the request never reached the model at all, so they measured a failed
# call rather than a thinking one. Measured properly on /zen/go/v1:
#
#   reasoning_effort: none                        -> HTTP 400, breaks every call
#   chat_template_kwargs: enable_thinking=false   -> 200, reasoning unchanged
#
# 21 versus 26 tokens on the same arithmetic prompt, i.e. noise.
#
# It is kept because an OpenAI-compatible gateway ignores body fields it
# does not recognise, so it is inert rather than harmful. But it is not
# doing anything and must not be described as if it were.
#
# What actually costs wall clock is round trips, not thinking. A real run
# was 23 calls and 1979 reasoning tokens total, about 86 per call.
#
_NO_REASONING = os.environ.get("BUNNY_NO_REASONING", "1") != "0"

BUNNY_EXTRA = ({
    "chat_template_kwargs": {"enable_thinking": False},
} if _NO_REASONING else {})

class UsageCallback(BaseCallbackHandler):
    """Records reasoning_tokens per call so we can prove whether the
    suppression above actually took effect."""

    def __init__(self):
        self.calls = 0
        self.reasoning_tokens = 0
        self.content_tokens = 0

    def on_llm_end(self, response, **kwargs):
        try:
            out = response.llm_output or {}
            usage = out.get("token_usage") or out.get("usage") or {}
            if not usage:
                gens = getattr(response, "generations", None) or []
                if gens:
                    usage = (gens[0][0].message.usage_metadata or {})
            det = usage.get("completion_tokens_details") or {}
            self.calls += 1
            self.reasoning_tokens += int(det.get("reasoning_tokens") or 0)
            self.content_tokens += int(usage.get("completion_tokens") or 0)
        except Exception:
            pass

    def report(self):
        return {"calls": self.calls,
                "completion_tokens": self.content_tokens,
                "reasoning_tokens": self.reasoning_tokens,
                "reasoning_suppressed": (self.reasoning_tokens == 0)}


def retry_stats():
    """What the transport had to retry, for the decision trail. Hiding this
    behind a longer wall clock would misrepresent how flaky the egress is."""
    out = {}
    for name, client in (("jev", _JEV_CLIENT),):
        tr = getattr(client, "_transport", None) if client else None
        if tr is not None and hasattr(tr, "stats"):
            out[name] = dict(tr.stats)
    return out
