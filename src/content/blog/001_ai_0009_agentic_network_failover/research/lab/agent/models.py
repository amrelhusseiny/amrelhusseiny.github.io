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
import time
import warnings
from typing import Any, Dict, List, Optional

import httpx
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

warnings.simplefilter("ignore")  # lab: proxy MITM, verification off by request

ZEN = os.environ.get("ZEN_BASE", "https://opencode.ai/zen/v1").rstrip("/")
JEV_MODEL = os.environ.get("JEV_MODEL", "jev-1.13")
BUNNY_MODEL = os.environ.get("BUNNY_MODEL", "space-bunny-free")

# space-bunny-free is a reasoning model: at max_tokens=3000 it spends the whole
# budget on reasoning_content and returns an EMPTY content field.
BUNNY_MAX_TOKENS = 12000

RETRY_307 = 14
RETRY_SLEEP = 3.0


class ModelError(RuntimeError):
    pass


class Retry307Transport(httpx.HTTPTransport):
    """The egress path intermittently answers 307 from the filtering proxy.
    Neither httpx nor the openai client retries a 3xx, so it is retried here."""

    def __init__(self, tries=14, sleep=3.0, **kw):
        super().__init__(**kw)
        self.tries = tries
        self.sleep = sleep

    def handle_request(self, request):
        last = None
        for _ in range(self.tries):
            resp = super().handle_request(request)
            if resp.status_code != 307:
                return resp
            last = resp
            try:
                resp.read()
            except Exception:
                pass
            resp.close()
            time.sleep(self.sleep)
        return last


_JEV_CLIENT = None


def _jev_client():
    """One persistent client for the whole run. Opening a new TLS connection
    per request is what the filtering proxy answers with 307."""
    global _JEV_CLIENT
    if _JEV_CLIENT is None or _JEV_CLIENT.is_closed:
        _JEV_CLIENT = _http_client(tries_307=RETRY_307)
    return _JEV_CLIENT


def _http_client(tries_307=14):
    """Cert validation off and the corporate https-proxy bypassed, per operator
    instruction. Direct egress to opencode.ai works; the proxy is an https proxy
    whose own certificate httpx refuses to verify."""
    # NB: supplying an explicit transport makes httpx ignore the client-level
    # verify= argument, so the transport itself has to be built with it.
    return httpx.Client(
        timeout=180.0,
        transport=Retry307Transport(tries=tries_307, verify=False),
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

        data, latency, attempts = None, 0.0, 0
        for attempt in range(1, RETRY_307 + 1):
            t0 = time.time()
            try:
                c = _jev_client()
                r = c.post(ZEN + "/systemone", json=payload,
                           headers=headers)
            except Exception:
                time.sleep(RETRY_SLEEP)
                continue
            if r.status_code == 307:
                time.sleep(RETRY_SLEEP)
                continue
            if r.status_code >= 400:
                raise ModelError("Jev HTTP %d: %s" % (r.status_code, r.text[:300]))
            try:
                data = r.json()
            except Exception as e:
                raise ModelError("Jev JSON decode failed: %s" % e)
            latency = round(time.time() - t0, 3)
            attempts = attempt
            break

        if data is None:
            raise ModelError("Jev unreachable after %d attempts" % RETRY_307)

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


def build_jev() -> JevChatModel:
    return JevChatModel()


def build_bunny_model() -> ChatOpenAI:
    key = os.environ.get("OPENCODE_API_KEY", "").strip()
    if not key:
        raise ModelError("OPENCODE_API_KEY not set")
    return ChatOpenAI(
        model=BUNNY_MODEL,
        base_url=ZEN,
        api_key=key,
        max_tokens=BUNNY_MAX_TOKENS,
        temperature=0.1,
        streaming=False,
        max_retries=8,
        http_client=_http_client(),
        timeout=180.0,
    )
