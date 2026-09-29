# SCRATCHPAD - agentic dual-path failover lab

Working notes for the article author. Design decisions, what broke, and what
the measurements actually mean. Updated through the two-lab comparison build.

---

## 0. Where things stand

| | status |
|---|---|
| agent lab (static + LangGraph) | built, healthy, 0% loss both directions |
| OSPF lab | built, healthy, 0% loss both directions |
| both running concurrently | yes, 13 containers |
| comparison harness | written (recorder.py, run-comparison.py), rep 1 aborted |
| matched comparison numbers | **not yet obtained** |

Rep 1 got as far as the fault and produced one real number: OSPF restored
traffic **+0.18s** after r1 was killed. The agent side died before it could act
(section 8).

---

## 1. The two agents

Both run on **LangGraph** (langgraph 1.2.12, langchain-core 1.6.5,
langchain-openai 1.6.6), inside a container, SSHing to the routers.

```
START -> capture -> judge -> (healthy -> END)
                          (faulty  -> bunny -> capture_after
                                     -> judge_after -> END)
```

**Jev** is reached at POST /zen/v1/systemone, which is not a chat API. It is
wrapped as a subclass of langchain_core BaseChatModel, so _generate() does the
HTTP call and returns an AIMessage, and it is usable anywhere in the graph.

**Space Bunny** is a real ReAct agent via create_react_agent with two tools:
ssh(node, command) and vtysh(node, command). Verified before building that the
Zen endpoint supports native OpenAI tool calling, and it immediately emitted
parallel ssh(...) calls unprompted.

Gotcha: _identifying_params must be a @property. As a plain method LangChain
raises TypeError: method object is not iterable.

---

## 2. How a decision is made

- **One API call per log line**, never one call per blob. A single real error
  cannot be diluted by surrounding noise.
- **Incremental.** A per-router cursor means only *new* lines are judged. A quiet
  cycle costs zero calls. If a log shrinks the cursor resets.
- **No threshold.** Jev answers a categorical question and *names* the state:
  normal or failed. One failed triggers failover. Nothing to tune.
- **No debounce, no cooldown, no waiting.**
- **Unreachable routers count.** A router that will not answer SSH produces the
  item "r1 10.90.10.12 did not respond to SSH: ...", judged by Jev like any
  other line, so a dead router is a decision and not a hardcoded branch.

### The noul polarity trap

noul is P(yes to the question asked). "Is router X operating normally?" gives
0.85 for healthy. "Does this log line report a failure?" gives **0.98 for a
failure**. Same model, opposite reading. The categorical choice question type
avoids the ambiguity and returns {choice, confidence, probabilities}.
Validated 7/7 against hand-labelled lines.

---

## 3. Topology - and why it was rebuilt twice

The topology went through three versions and the reasons matter, because both
earlier versions produced a **comparison that was quietly invalid**.

### v1: one flat bridge, all six routers

Worked, and the first agent run on it was valid. But it cannot be compared to
OSPF: rc1 and rc2 sit on the same broadcast domain, so OSPF routes *directly*
between them and never uses r1 or r2. Killing r1 changed nothing at all in the
OSPF lab. The agent lab only used r1 because its static route explicitly named
r1 as the next hop. The two labs were not doing the same thing.

### v2: two segments, rc1 and rc2 dual-homed onto each

Fixed the adjacency problem but not the equivalence one: OSPF still preferred
the direct rc1-to-rc2 adjacency over the r1/r2 chain, because a direct
neighbour on the same subnet is always one hop cheaper.

### v3 (current): four segments, rc1 and rc2 meet only on standby

```
  10.90.10.0/24  PA : rc1 - r1          primary, OSPF cost 10
  10.90.11.0/24  PB : r1 - r2           primary, OSPF cost 10
  10.90.12.0/24  PC : r2 - rc2          primary, OSPF cost 10
  10.90.20.0/24  ST : rc1 - r3, r4 - rc2 standby, OSPF cost 100

  primary path :  rc1 -> r1 -> r2 -> rc2     (4 hops)
  standby path :  rc1 -> r3 -> rc2          (2 hops, but cost 100)
```

Now the primary path is a genuine multi-hop chain that no shortcut can bypass,
and both labs start equally redundant. Verified:

```
  AGENT rc1 -> 10.90.8.1   S>*  [1/0]    via 10.90.10.12  (r1)  + [200/0] via r3
  OSPF  rc1 -> 10.91.8.1   O*>  [110/30] via 10.91.10.12  (r1)
```

Agent lab uses the 10.90.x family with static routes, OSPF lab the 10.91.x
family with OSPF. Identical physical layout, different routing mechanism. r4 is
spare capacity on the standby segment.

---

## 4. Measurement design

Nothing trusts the agents to report their own success. Reachability is measured
by ICMP from inside the edge routers, on a shared wall-clock time base.

- ping -i 0.2 -D -W 1 -I <edge loopback> <far loopback>, four streams: both
  labs, both directions.
- **Source must be the edge loopback** (-I 10.90.1.1), not the interface
  address. See section 8.
- A probe counts OK only if the *target itself* replied. A redirect or an
  unreachable counts as a failure.
- downtime = T0 -> first successful probe after the outage.
- Light telemetry every 5s: rc1/rc2 route tables in both labs, plus OSPF
  neighbour state. Full snapshots at phase boundaries only.

Per repetition the run directory holds ping.csv, telemetry.log, T0, events.log,
downtime.json, rep.json, plus the agent run bundle.

---

## 5. Results so far

### Healthy baseline (earlier single-segment run)
```
capture[before]: 0 item(s) to judge
JEV[before] verdict: faulty=none
CONCLUSION : healthy_no_action      3.04s, 0 API calls
```

### Earlier agent fault run (single-segment topology)
```
jev r1   failed conf=1     r1 did not respond to SSH
JEV[before] verdict: faulty=[r1]
... 68 messages, 43 tool calls (28 ssh, 15 vtysh), 324s ...
faulty before : [r1]      faulty after : [r1, rc1]
```

Bunny proved r1 was hard-down (no ARP, a /24 port scan that found everything
*except* .12, unreachable loopback), identified the real flaw - rc1 had no
alternate at all - and applied nine config writes, all rc=0:

```
no ip route 10.90.8.1/32 10.90.10.12     drop the dead primary
ip  route 10.90.8.1/32 10.90.20.12     point at r3 instead
... plus the same for two more prefixes ...
ip  route 10.90.8.1/32 10.90.10.12 200  re-add primary at distance 200, as fallback
```

**Traffic restored**, verified from outside the agent: rc1 -> 10.90.8.1 went from
No route to host to REACHABLE. The last group is the interesting part: it did not
delete the dead path, it *demoted* it, so traffic returns to primary on its own
if r1 comes back.

r1 stayed down. The agent rerouted around it; it could not revive it. That is the
honest ceiling of a configuration agent.

---

## 6. Findings

**F1 - the monitor flags its own repair as a new fault.** After the fix the
post-change re-read returned faulty_after = [r1, rc1]. rc1 was judged failed at
**confidence 1.0** on this line, which Bunny own config burst had produced:
```
MGMTD: Locking for DS 2 failed, Err: Lock already taken on DS by another session!
```
Routine FRR config-lock contention from issuing several vtysh writes in quick
succession. The agent repaired the network and the instrumentation immediately
reported the repair as a new problem. This gets *worse* the more autonomous the
agent is, because the agent is what generates the log traffic.

**F2 - the same line can get opposite verdicts.** On a healthy lab,
MGMTD: XXX txn in progress, retry init came back normal on rc1 (confidence 0.02)
and failed on r2 (confidence 0.06). Same text, same model, both effectively
coin-flips.

**F3 - low confidence is a usable signal the code ignores.** Every F2 verdict
carried confidence under 0.11. A single failed at confidence 1.0 is trustworthy;
a single failed at 0.06 is not. The design deliberately has no threshold, which
is right for a dead router and wrong for ambiguous chatter.

**F4 - noise filtering is a blunt instrument and the obvious version is unsafe.**
Only libyang Invalid ... /frr-vrf:.../state boot lines are filtered. A broader
filter on the word "invalid" was explicitly rejected, because the lab very first
genuine fault was an FRR config rejection containing that word:
`invalid address 127.0.0.1/8`. Filtering on the token would hide exactly the class
of failure the lab exists to catch.

**F5 - the cursor hides F2 in steady state.** Boot-chatter false positives fire
once after a restart and never again. A clean baseline is clean only because a
prior run already consumed those lines. Any write-up must disclose that the first
cycle after a restart is not representative.

**F6 - autonomous means slow.** 324s and 43 tool calls to restore one path, with
several turns spent rediscovering that the routers have no ping and that
`show interfaces` is not valid in this FRR build. All correct, none of it fast.

---

## 7. An important caveat about the OSPF number

**OSPF restored traffic +0.18s, and is still serving 26 minutes after r1 died.**
That number is real but it is not measuring protocol convergence.

`docker stop -t 0` destroys r1 veth pair. The peer interface on rc1 goes down
immediately, so OSPF loses the interface at once and never waits its 40 second
dead interval. What we measured is **interface-down detection**, which is a
physical event, not a routing decision.

A real failure where the link stays up - a fibre cut, a remote router reboot -
leaves the interface UP and OSPF must wait the full dead interval. That is the
honest convergence number and it has not been measured yet.

Planned: a second fault variant that sets r1 interface down from *inside* r1
(container stays alive, link stays up from rc1 point of view), forcing OSPF
through the real dead-interval path. Both numbers belong in the article, with the
distinction stated plainly, because quoting 0.18s as "OSPF converges in 0.18s"
would be wrong.

---

## 8. Everything that broke

### The environment

| symptom | cause | fix |
|---|---|---|
| apt-get exit 100, image build failed | corporate proxy returns **401 on Debian InRelease** and truncates package indexes | retry loop (20 attempts) plus a build assertion that FAILS the build if frr/sshd/ping are missing |
| trusted=yes did not help | the proxy blocks the signed-repo metadata specifically | abandoned; the retry loop is enough |
| alpine apk unusable | TLS interception | avoided alpine entirely |
| intermittent 307 from the API | filtering proxy; neither httpx nor the openai client retries a 3xx | Retry307Transport(httpx.HTTPTransport) |
| verify=False appeared to be ignored | **passing an explicit transport makes httpx ignore the client-level verify=** | build the transport with verify=False itself |
| space-bunny-free returned empty content | reasoning consumed the whole max_tokens budget | max_tokens=12000 |
| Jev unreachable after 14 attempts | transient 307 burst | persistent httpx client, wider retry window |

### The lab

| symptom | cause | fix |
|---|---|---|
| config lost on every restart | routes were poked in with vtysh at runtime | persist ip route in frr.conf |
| no ip redirects in frr.conf had no effect | it is a **kernel** sysctl, not just an FRR setting | set send_redirects=0 and accept_redirects=0 in the entrypoint |
| every config command returned rc=1 | FRR 10 refuses config lines via a bare vtysh -c | wrap non-read-only commands in -c "conf t" ... -c end |
| AIMessage object is not subscriptable | used m["tool_calls"] on a message object | m.tool_calls |
| method object is not iterable | _identifying_params defined as a method | make it a @property |
| rc1 had **both** addresses on **both** interfaces | **Docker does not attach networks in a guaranteed order**, and the order differed between the two projects | entrypoint resolves each interface by the address Docker assigned, via IF_PA/IF_PB/IF_PC/IF_ST env vars, substituting __PA__ etc. into frr.conf |
| all interface costs silently ignored | the sed that substituted the placeholders ran **before** cp /config/frr.conf /etc/frr/frr.conf | moved the substitution after the copy |
| OSPF picked the standby path with no explanation | same bug - interface costs were never applied, so all paths tied at cost 10 | same fix |
| r2 could not reach the client net | a static route used r1 PA address, which is not on r2 subnets, so it resolved recursively through the Docker default route | every next hop must sit on one of the device own segments |
| end-to-end ping 100% loss with correct routes | ping used rc1 **interface** address as source, and rc2 has no route back to the transit subnet | ping -I <edge loopback> - traffic really originates on the client/server network |
| Subnet overlaps with other one on this address space | leftover networks from the previous topology | docker network rm the old ones |

### The measurement

| symptom | cause | fix |
|---|---|---|
| static lab showed 40s of healthy probes after the kill | docker stop has a **10 second SIGTERM grace**; T0 was marked before the kill | docker stop -t 0, and mark T0 only **after** the container is confirmed dead |
| 30s hole in the ping stream, first failure looked like +40s | the heavy snapshot() loop (~30 docker exec per iteration) starved the ping process | light telemetry every 5s; full snapshots only at phase boundaries |
| agent lab NOT healthy after 200s during rep 1 | transient; healthy in isolation on retry | a failed health check should abort the rep rather than continue |
| agent died silently after capture, no traceback | 34 Jev calls in a row against a flaky proxy; process killed mid-judging | **stop passing --reset-cursors** - with cursors seeded a run judges 1-2 lines instead of 34 |

That last one is worth stating plainly: the incremental cursor design is not
just an optimisation, it is what makes the agent survivable against this proxy.

---

## 9. Layout

```
lab/
  docker-compose.agent.yml    agent lab, 10.90.x, static + LangGraph agents
  docker-compose.ospf.yml     OSPF lab,  10.91.x, no agents
  frr/agent/*.conf            static configs, __PA__/__PB__/__PC__/__ST__ placeholders
  frr/ospf/*.conf             OSPF configs, same placeholders
  frr/agent|ospf/daemons      staticd=yes vs ospfd=yes
  docker/router/              Debian + FRR 10.3 + sshd + iputils-ping, retrying apt
  docker/agent/               Debian + langgraph/langchain + openssh-client
  agent/                      the LangGraph agents (section 1)
  recorder.py                 ICMP observer, telemetry, downtime analysis
  run-comparison.py           one matched repetition across both labs
  agent/seed-cursors.py       mark existing log lines as already judged
  runs/                       per-repetition bundles
```

outage = T0 -> first successful probe. downtime.json carries per-lab,
per-direction numbers. ping.csv is the raw evidence and should be committed.

---

## 10. Still open

- **The matched comparison has not completed.** Rep 1 was aborted because the
  agent died against the flaky API. The cursor fix addresses the cause but the
  run has not been repeated.
- **The dead-interval OSPF variant is not implemented** (section 7). Until it
  is, the honest OSPF figure is "under 0.2s on interface-down, unmeasured on
  link-failure".
- Whether to widen the noise filter for F2 is an editorial decision.
- A failed health check should abort the repetition rather than proceed.
- `docker stop` also removes the container, so recovering r1 mid-run means a
  recreate, not a start. Worth deciding whether a self-healing variant is in
  scope, since no config agent can bring back a dead machine.
- Article corrections still outstanding: Typeface -> TypeSafe, Mercurey ->
  Mercury, and state that the action model is space-bunny-free because Mercury
  was unavailable.

---

## 11. Session log - 2026-09-28 evening

Everything in this section was re-derived from scratch today. None of it needed
to be, and the reason it nearly was is the single most useful thing in this
file: **the two models live on two different API paths, and the wrong one fails
with an error that looks like a permissions problem.**

### 11.1 Task checklist

- [x] 11.2 Identify why space-bunny-free returned 403
- [x] 11.3 Identify why jev-1.13 appeared to return endpoint-unavailable
- [x] 11.4 Confirm exact model IDs and endpoints against the OpenCode docs
- [x] 11.5 Fix models.py (split base URLs, add session header)
- [x] 11.6 Re-measure the reasoning-suppression parameters
- [x] 11.7 Disable TLS verification container-wide
- [x] 11.8 Find the stale-OSPF path bug and close the harness gap
- [x] 11.9 Diagnose the HTTP 302 stall
- [x] 11.10 Fix the 302 stall (root cause: proxy was bypassed)
- [x] 11.11 Run 3 matched reps, agent vs OSPF (agent 138s median vs OSPF 33.5s)
- [ ] 11.12 Tear down all 13 containers

### 11.2 The 403 that was not a permissions problem

Symptom, from the lab:

~~~
POST https://opencode.ai/zen/v1/chat/completions   model=space-bunny-free
  -> 403 Model access is disabled
~~~

Five attempts over 20s, identical every time. Six header combinations made no
difference. Paid models on the same key returned 200 throughout.

The message says access is disabled, which reads as an entitlement wall, so the
instinct is to go looking for a different key. That is a dead end. **The key was
fine and the model was fine.** The answer was in the path.

The docs at https://opencode.ai/v2/docs/console/go list:

~~~
Space Bunny Free   space-bunny-free   https://opencode.ai/zen/go/v1/chat/completions
~~~

Note `/zen/go/v1/`, not `/zen/v1/`. **OpenCode Go and OpenCode Console are two
different products with two different URL prefixes**, and the free models are
only served on the Go one.

| call | result |
|---|---|
| POST /zen/v1/chat/completions + space-bunny-free | **403 Model access is disabled** |
| POST /zen/go/v1/chat/completions + space-bunny-free | **400 MissingSessionID** |

The 403 was never about access. It was the Console gateway being asked for a
model that only the Go gateway serves. And the 403 wording actively misleads
you into thinking entitlements, which is what sent me down the wrong path.

### 11.3 The second requirement: x-opencode-session

Having the right path was not enough. The Go gateway refuses to route anything
without a session header:

~~~
400 {"type":"MissingSessionID",
     "message":"Request is missing x-opencode-session and cannot be routed
                efficiently. Please see https://opencode.ai/docs/go/#where-can-i-use-it"}
~~~

Add it and the model answers:

~~~
HTTP 200
{"model":"space-bunny-free",
 "choices":[{"finish_reason":"stop",
   "message":{"role":"assistant","content":"BUNNY_OK","name":"Space Bunny",
              "reasoning_content":"We need answer exactly BUNNY_OK. Need no extra."}}],
 "usage":{"completion_tokens_details":{"reasoning_tokens":15}}}
~~~

With a tool bound it returns a proper call:
`finish_reason: tool_calls`, `{"node": "localhost", "command": "ls -la /etc"}`.

The Go docs also ask clients to send their own User-Agent rather than a generic
SDK string, framed as abuse monitoring. That was tried and changed nothing here,
but it is the documented contract so the lab sends it anyway.

### 11.4 Jev: working code, my own bad test payload

/zen/v1/systemone returned 422 Endpoint-is-unavailable for jev-1.13, which reads
like a decommissioned endpoint. It was not. **The gateway answers a malformed
request with a misleading 422**, and the hand-written probe was malformed.

The documented shape for a `choice` question is an **object**, mapping each option
to its definition:

~~~
"questions": { "verdict": {
    "type": "choice",
    "instructions": "Which one describes this router?",
    "criteria": { "normal": "The router is operating normally",
                  "failed": "The router has failed or lost connectivity" } }}
~~~

Sending `criteria` as a bare string instead returns 422 Endpoint-is-unavailable.
Same endpoint, same model, same key. Only the payload shape differs.

| payload | result |
|---|---|
| criteria as object | **200** choice=failed confidence=0.95, probs normal 0.02 failed 0.98 |
| criteria as string | 422 Endpoint is unavailable |
| noul, verbatim from docs | **200** noul=0.96 |

**The lab code was already correct.** models.py:137 already declares
`criteria: Dict[str, str] = {...}`, and JEV_MODEL already defaults to the paid
`jev-1.13`. The free variant returns 403 like the others, so the paid one is the
right default.

Lesson: when a gateway returns something that sounds like this-thing-is-gone,
reproduce it with the documented payload before concluding the thing is gone.

### 11.5 The fix applied to models.py

Two edits, both in agent/models.py, both verified to compile.

~~~python
ZEN    = os.environ.get("ZEN_BASE",    "https://opencode.ai/zen/v1").rstrip("/")
ZEN_GO = os.environ.get("ZEN_GO_BASE", "https://opencode.ai/zen/go/v1").rstrip("/")
BUNNY_SESSION = os.environ.get("BUNNY_SESSION", "jevshowcase-lab")
~~~

and in build_bunny_model():

~~~python
base_url=ZEN_GO,
default_headers={"x-opencode-session": BUNNY_SESSION},
~~~

**Jev is untouched.** It keeps ZEN + /systemone. Do not unify these two
constants; they are different products and only the shared name suggests
otherwise.

The agent code is bind-mounted by docker-compose, so code changes need **no
image rebuild**. /agent is empty in the image itself.

### 11.6 Reasoning parameters, re-measured on the Go endpoint

| parameter | result |
|---|---|
| reasoning_effort: none | **HTTP 400** - breaks every call, must stay deleted |
| chat_template_kwargs: enable_thinking false | 200, but **no measurable effect** |

On a single arithmetic turn: plain request gave reasoning_tokens=21, with
chat_template_kwargs gave 26. That is noise, not suppression.

**This contradicts the comment currently in the code**, which claims a measured
median 1831 -> 674 over 8 samples with 4 of 8 strongly suppressed. Those samples
were taken against the wrong endpoint. On a working endpoint Space Bunny spends
roughly 20 reasoning tokens on a trivial turn, not 1831.

The honest reading: chat_template_kwargs does nothing here, and the earlier
number was measuring a failing or differently-routed endpoint. The comment
should be corrected rather than left as a reproducible claim.

This also matters for the article. The 324s agent run was attributed to
expensive reasoning turns, and that attribution needs re-measuring on Go before
it goes into print.

### 11.7 TLS verification, container-wide

Patching the two httpx clients was not enough. docker/agent/sitecustomize.py
(also copied into the router image) now disables verification process-wide:

1. ssl._create_default_https_context -> unverified
2. ssl.create_default_context -> forced CERT_NONE
3. ssl.SSLContext.__init__ -> forced CERT_NONE
4. ssl.SSLContext.wrap_socket -> re-asserted immediately before every handshake

Plus ENV LAB_NO_TLS_VERIFY=1, PYTHONHTTPSVERIFY=0, GIT_SSL_NO_VERIFY=1,
NODE_TLS_REJECT_UNAUTHORIZED=0.

**Step 4 exists because of urllib3.** Steps 1-3 all failed against it: urllib3
builds its context and then explicitly re-asserts verify_mode afterwards,
overriding whatever the factory returned. Patching its factory did not stick
either, because it binds create_urllib3_context into urllib3.connection at
import time, so the patch has to land *after* import. An earlier attempt hooked
__import__ to do that and **deadlocked the container on startup**, because the
hook is re-entrant: the patcher itself calls __import__. A _BUSY guard fixes it.

wrap_socket is the honest chokepoint. Every TLS handshake in CPython goes
through it, so nothing at the call site can override it.

Verified: create_default_context verify_mode=0, httpx default pool verify_mode=0,
urllib3 and requests both succeed where they previously raised
CERTIFICATE_VERIFY_FAILED.

There is no env var that disables curl verification; curl still needs -k.

### 11.8 Stale-OSPF: how a lab measures nothing and looks perfect

The labs had been sitting about 12h. ospf-rc1 had learned a 2-hop path to the
server directly across the standby segment, bypassing r1 and r2 entirely.

| | next hop to server | metric | after killing r1 |
|---|---|---|---|
| agent lab | 10.90.10.12 (r1, pa) | static d1 | traffic dies |
| OSPF lab, stale | 10.91.20.14 (rc2, direct on st) | 100 | **traffic unaffected** |
| OSPF lab, converged | 10.91.10.12 (r1, pa) | 30 | traffic dies |

Killing r1 in the stale state caused **zero outage**. There was nothing to
recover, so any recovery time measured there is an artifact.

Root cause: rc1 and rc2 are DROthers on the same broadcast segment, so they
never form a Full adjacency with each other, and the direct st path can win on
cost. After r1 was recreated and OSPF re-converged, the correct 3-hop path is
installed.

**Why this matters beyond this session:** a harness that does not verify which
path is carrying traffic will report a clean fast number while measuring
nothing at all.

run-comparison.py was missing the precondition entirely - it had only ever been
added to run-ospf.py. A sed meant to strip --reset-cursors missed its target, so
that bug was live too. reset_labs() used compose --force-recreate, which silently
skips a container left behind by docker stop.

run-comparison.py now has, on **both** labs, before any fault is injected:

- wait_all_up(pfx) - every router container is actually running
- primary_in_use(pfx) - rc1 routes to the server via the primary next hop

and raises PreconditionFailed, which main() records as status=aborted. An
aborted rep is never folded into the comparison. reset_labs() now does an
explicit docker rm -f first.

### 11.9 The 302 stall

From inside a container:

~~~
models._http_client().post(ZEN + "/systemone", ...)
  -> HTTP 302 after 84.5s
~~~

The same call by curl on the host returns 200 in well under a second, and a plain
GET /zen/go/v1/models from the container returns 200 in 0.7s. TLS and routing are
fine; something about this path through the corporate proxy yields a redirect.

The reason it stalls instead of failing fast: **302 is a member of RETRYABLE** in
models.py, so RetryTransport burns all 10 tries with exponential backoff before
giving up. One API call becomes an 85-second hole, which is what silently blew
out the first several live probes.

**RESOLVED. The Location headers answered it immediately:**

~~~
systemone -> 302  Location: http://10.122.106.86:15871/cgi-bin/blockpage.cgi?ws-session=...
chat Go   -> 307  Location: http://sheua017-wcg:8080/auth/?du=aHR0cHM6Ly9vcGVuY29kZS5haS96ZW4v
~~~

The first is a web-filter block page, the second is the proxy login portal. So
the 30x was the corporate path refusing a **direct** connection.

The actual bug was in `_http_client()`, whose docstring said the proxy was
deliberately bypassed because direct egress used to work. It no longer does.
Side by side, same body and same key, from inside the container:

| path | via _http_client() | via plain httpx |
|---|---|---|
| systemone | 302 in 106.8s | **200 in 1.0s** |
| chat Go | 307 in 85.5s | **200 in 1.7s** |

Supplying an explicit transport to httpx.Client makes httpx ignore the
client-level proxy= argument, exactly as it already ignored verify=. So the
transport was going direct while plain httpx was using the proxy.
RetryTransport was then faithfully retrying a redirect that could never
resolve, which is where the 85-107s went.

Fix: pass the proxy into the transport itself.

~~~python
proxy = (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "")
return httpx.Client(timeout=60.0,
                   transport=RetryTransport(tries=tries, verify=False,
                                            proxy=proxy or None))
~~~

General lesson, which has bitten this lab three separate times: **an explicit
httpx transport silently disables client-level verify= and proxy=.** Both must
be handed to the transport.

The langchain-openai warning about injected transports disabling proxy
auto-detection is a red herring here, because the lab passes its own
http_client and that wins.

### 11.9b Both agents verified end to end, through the real classes

~~~
JEV   FAULT log    1.2s -> choice=failed  confidence=0.99  failed=1.00 normal=0.00
JEV   HEALTHY log  0.6s -> choice=normal  confidence=0.95  normal=0.97 failed=0.03

BUNNY tool call    1.9s -> run(node=r1, command="ls -la /etc")
                              finish_reason=tool_calls

retry_stats: {"jev": {"calls": 2, "retries": 0, "by_status": {}}}
~~~

Zero retries, and the 107s stall became 1.2s. Jev separates the two cases
cleanly on probability, with no threshold anywhere in the code.


### 11.10 Reference: exact IDs, endpoints and shapes

**Jev - TypeSafe SystemOne, on Console**

- endpoint: POST https://opencode.ai/zen/v1/systemone
- model: jev-1.13 (paid, entitled). jev-1.13-free -> 403.
- question types: noul (yes/no), choice (multiple choice), score (rubric)
- noul returns P(yes to the question as asked), so polarity flips with wording
- choice needs criteria as an **object**; a string returns 422
- parallel questions allowed, answered under matching question IDs

~~~json
{"model":"jev-1.13",
 "state":"<router log lines>",
 "questions":{"verdict":{
   "type":"choice",
   "instructions":"Which one describes this router?",
   "criteria":{"normal":"...","failed":"..."}}}}
~~~

**Space Bunny - on Go**

- endpoint: POST https://opencode.ai/zen/go/v1/chat/completions
- model: space-bunny-free (free, listed as limited time). No paid variant.
- header x-opencode-session is **mandatory**, stable per conversation
- native OpenAI tool calling, finish_reason tool_calls
- returns reasoning_content alongside content

**Entitled alternatives if Space Bunny ever goes away** (all emit native tool
calls):

| model | reasoning_tokens |
|---|---|
| glm-5.3-flash | 26 |
| qwen3.8-flash | 77 |
| kimi-k3 | 110 |
| deepseek-v4.1-flash | 121 |
| qwen3.6-plus | 1882 |

The gateway is not uniform: claude-*, gpt-*, gemini-* and grok-* all return 400
Model-does-not-support-this-protocol on /chat/completions, because they are
served from /zen/v1/messages and /zen/v1/responses instead. Only some models
are @ai-sdk/openai-compatible.

### 11.11 Error-message cheat sheet

Read these literally. Several are actively misleading.

| message | actually means |
|---|---|
| Model access is disabled (403) | wrong product path, or genuinely unentitled |
| Model is unavailable (400) | that model ID does not exist |
| Endpoint is unavailable (422) | malformed request, NOT a dead endpoint |
| MissingSessionID (400) | missing x-opencode-session on the Go gateway |
| does not support this protocol (400) | model needs /messages or /responses |
| Invalid request (400) | bad payload shape, usually criteria |

### 11.12 MATCHED RESULTS - 3 reps, both labs, same fault, same T0

First complete matched set. r1 killed with `docker stop -t 0` in both labs at
the same instant, T0 marked only after both were confirmed dead. Downtime is
T0 to the first successful ICMP probe, measured externally at 0.2s intervals.
Never self-reported by the agent.

| rep | agent_fwd | agent_rev | ospf_fwd | ospf_rev |
|---|---|---|---|---|
| 1 | 138.806s | 138.918s | 34.446s | 33.126s |
| 2 | 370.111s | 370.182s | 33.859s | 32.846s |
| 3 | 136.363s | 136.251s | **no outage** | 32.335s |

agent fwd mean 215.1s, median 138.8s. ospf mean 33.5s over the five direction
pairs that saw any outage. **OSPF is roughly 4x faster on the median and 6x on
the mean.** The agent is not close, and that is the honest headline.

Rep 2 is a 2.7x outlier against reps 1 and 3, and it is the most interesting
number in the table precisely because it was not engineered. Nothing in the
code varies between repetitions: same fault, same seed, same prompts, same
tools. The only difference is which commands the model chose to run and how
long it spent thinking. That variance *is* the finding.

Rep 3 ospf_fwd recorded no outage at all while ospf_rev took 32.3s. With a
0.2s probe interval, that means the forward path recovered inside 200ms.

### 11.13 What the agent actually did (rep 3, from 06-apply.ndjson)

Space Bunny made exactly **four** configuration writes, and every one is a
distance change rather than a new design:

~~~
rc1  ip route 10.90.8.1/32 10.90.10.12 300     rc=0   raise the dead primary
rc1  no ip route 10.90.8.1/32 10.90.10.12     rc=0   then remove it outright
rc2  no ip route 10.90.1.1/32 10.90.12.15     rc=0   same on the return path
~~~

It arrived there by investigation, not instruction. It tried r1 first and got
`No route to host` twice, then walked every other router with `ip -br addr`,
then asked `ip route get 10.90.8.1` on rc1 and saw the answer was still the
dead next hop. It then ran `show running-config` on both edge routers and
read the static routes out loud before touching them.

The verification loop is visible in the transcript and it is genuinely
checking its own work:

~~~
ip route get 10.90.8.1 from 10.90.1.1  -> via 10.90.10.12 dev eth0   (still dead)
no ip route 10.90.8.1/32 10.90.10.12                              rc=0
ip route get 10.90.8.1 from 10.90.1.1  -> via 10.90.20.12 dev eth1   (failover)
~~~

23 model calls, 8790 completion tokens, 1979 reasoning tokens,
`reasoning_suppressed: false`. Jev made 1 call with 0 retries.

It also wasted calls. `ip route`, `ip -4 route`, `ip -br link` and
`arping ... | tail -5` all came back as FRR parse errors, because the run tool
routes anything not matching `show|do|ping|...` into FRR config mode. Four of
twenty-three calls were spent on syntax that does not exist. That is real
cost and it belongs in the article.

### 11.14 Jev blamed the agent for the agent's own fix

The most quotable result. After Bunny finished, Jev re-judged and returned
**faulty=['r1', 'rc1']** - flagging rc1, which was perfectly healthy.

~~~
{"node": "rc1", "source": "frr_log", "choice": "failed", "confidence": 1,
 "line": "2026/09/28 20:15:04 STATIC: [PNYPZ-BCP8Y] Static Route using 300
         interface not installed because the interface does not exist in
         specified vrf"}
~~~

The log line Jev called a failure was **written by Bunny's own remediation**,
20 seconds earlier. Bunny told FRR to install a static route with distance 300,
FRR complained that the interface for that distance did not exist, and the
monitor read FRR's complaint as a new fault.

So the agent was judged as faulty for fixing the fault. This is a real and
specific weakness of judging a router purely by its own log: **the router
narrates the operator's mistakes as its own errors.** No threshold or
correlation would have caught it, because from rc1's point of view the line
genuinely does say a route failed to install.

It is also self-limiting here: the run ends after the fix, so a flapping
verdict costs nothing. In a loop it would be considerably worse.

### 11.15 The reasoning-suppression claim is now settled

`04-bunny-usage.json` from a real 23-call run:

~~~
{"usage": {"calls": 23, "completion_tokens": 8790, "reasoning_tokens": 1979,
         "reasoning_suppressed": false},
 "api_retries": {"jev": {"calls": 1, "retries": 0, "by_status": {}}}}
~~~

`reasoning_suppressed: false` confirms what 11.6 suspected:
`chat_template_kwargs.enable_thinking` does nothing on this endpoint. The
comment in models.py claiming a median drop from 1831 to 674 should be
deleted rather than kept as a claim the code cannot reproduce.

Note the shape of the cost: 1979 reasoning tokens across 23 calls is about 86
per call, which is nothing. **The 136s agent time is not thinking time.** It is
model round trips - roughly 23 sequential calls at a few seconds each - plus
the agent reading its own output before each next step. The earlier 324s
figure and its explanation were both artefacts of the broken endpoint.


---

## 12. Option C build, 2026-09-29

### 12.1 What changed and why

The 138s run was slow for reasons that had nothing to do with the models. The
agent spent 23 calls re-deriving a topology that could simply have been told to
it, and 4 of those calls died on FRR rejecting shell syntax. So:

| change | what it fixes |
|---|---|
| Jev makes a **second call** and picks the path, from a closed set of two | removes the entire discovery phase |
| Bunny gets the topology, the segments and the exact next hops up front | no re-deriving |
| Bunny decides only **how** to execute (option C) | keeps its judgement where judgement matters |
| capture reads all six routers in a thread pool | 6 serial SSH round trips -> 1 |
| command dispatcher inverted: default shell, FRR only on known heads | kills the 4 wasted calls |
| `ping` claim corrected in the prompt | agent could verify instead of guessing |
| decision trail archived per rep | all 3 trails survive |

### 12.2 The two Jev calls

First call, unchanged: one line in, normal or failed, categorical, no threshold.
It correctly named r1 in every run.

Second call, new: given the ASCII diagram of both paths plus the routing state
read from the devices, choose a **path id**. Closed set, no free text.

~~~
A failover has just been detected.

Routers the first pass judged FAILED: r1

Routing state read from the devices themselves:

  rc1 to the server network:
    PATH-A  next hop 10.90.10.12    distance 1    ACTIVE NOW
    PATH-B  next hop 10.90.20.12    distance 200  installed, standby
...
~~~

Measured on the live lab:

| case | result | latency |
|---|---|---|
| r1 dead, both paths installed | **PATH-B**, confidence 0.95-0.97 | 0.6-1.5s |
| r3 also dead, PATH-B has no route | **PATH-A** | 1.2s |
| both paths dead on both routers | **raises ModelError, no answer invented** | - |

That third row matters. A free-text path answer would produce a route FRR accepts
with rc=0 and that silently blackholes traffic. An answer outside the set raises.

### 12.3 Bugs found and fixed while building this

Four, all caught by testing against the real devices rather than by inspection:

1. **`path_state()` matched on next hop only.** On rc1 the standby next hop
   10.90.20.12 also serves 10.90.3.1 at distance 1, so the standby path was
   reported as the active one. Now filtered by target prefix as well.
2. **`[200/0]` is distance/metric, not metric/distance.** The regex read group
   2, the metric, which is always 0 for a static. Every distance came out 999.
3. **`usable` was computed from either router.** A healthy rc2 keeps a route
   installed for a path whose forward half is dead, which resurrected an
   unusable path. Now both directions must have the route.
4. **`os.environ.get(name, default)` returns the empty string** when a variable
   is exported by the host but unset there, which silently produced empty next
   hops. Added an `_env()` helper.

Also: the prompt claimed **there is no ping binary on any device**. That is
false, ping is installed and works. The invariant was inherited from an earlier
phase and had never been re-checked. Corrected, and the agent now uses ping to
verify reachability, which is the cheapest check available.

### 12.4 RESULTS: option C, 3 matched reps, same fault, same T0

| rep | agent_fwd | agent_rev | ospf_fwd | ospf_rev |
|---|---|---|---|---|
| 1 | 51.9s | 51.9s | 34.2s | 32.8s |
| 2 | 52.2s | 52.2s | 34.3s | 32.8s |
| 3 | 44.5s | 43.0s | 34.2s | no outage |

| | n | mean | median | max |
|---|---|---|---|---|
| agent_fwd | 3 | 49.5s | 51.9s | 52.2s |
| agent_rev | 3 | 49.0s | 51.9s | 52.2s |
| ospf_fwd | 3 | 34.2s | 34.2s | 34.3s |
| ospf_rev | 2 | 32.8s | 32.8s | 32.8s |

**Before and after, same fault, same T0, same models:**

| | median agent | median OSPF | gap |
|---|---|---|---|
| free-form agent over SSH | 138.8s | 34.2s | 104.6s |
| option C | **51.9s** | 34.2s | **17.7s** |

The agent got **2.7x faster** and the gap to OSPF closed from 105s to 18s.
OSPF did not move at all, which is the control.

The variance also collapsed. The old run produced a 370s outlier across three
reps; option C produced 44.5, 51.9 and 52.2. That spread was not the model being
slow, it was the model guessing at commands and topology.

### 12.5 What the agent actually does now

Per repetition, from the archived trails:

| rep | Bunny model calls | tool calls | config writes | path chosen | confidence |
|---|---|---|---|---|---|
| 1 | 6 | 17 | 2 | PATH-B | 0.95 |
| 2 | 5 | 18 | 2 | PATH-B | 0.95 |
| 3 | 4 | - | 2 | - | - |

Down from 23 model calls to 4-6.

**Parallel tool calls work and are being used.** The transcript shows five
separate turns issuing 4, 5, 2, 4 and 2 tool calls at once, so 17 calls were
issued in about 7 turns. This was verified in the transcript rather than assumed.

**The two config writes are always the same shape:**

~~~
rc2   no ip route 10.90.1.1/32 10.90.12.15     rc=0
rc1   no ip route 10.90.8.1/32 10.90.10.12     rc=0
~~~

Withdraw the dead primary on both edge routers so the already-configured
standby becomes the lowest-distance route. The read-only calls around them are
ip -br addr, show ip route, ip route get, and ping on both next hops.

### 12.6 Where the remaining 18 seconds goes

| | old | option C |
|---|---|---|
| model calls | 23 | 4-6 |
| Jev calls | 1 | 2 |
| tool calls issued | 23 serial | ~17 in ~7 parallel turns |
| config writes | 4 | 2 |

It is no longer discovery and it is no longer syntax errors. What is left is
genuine sequential latency: each model turn waits for the SSH results of the
previous turn before it can decide what to read next. OSPF does not pay that
because it never talks to anybody.

### 12.7 CAVEATS, DEVIATIONS AND COMPROMISES

Everything the reader should know before quoting any number above.

**Changed the article premise**

1. `jev-1.13-free` returns 403, so the decision model is the **paid** `jev-1.13`.
   Jev is no longer a free model in this writeup.
2. Space Bunny is reached at **`/zen/go/v1/chat/completions`**, not `/zen/v1/`.
   Any URL or base path already published is wrong.
3. The path decision moved from Space Bunny to Jev. The original brief was
   *Jev decides which router failed, Bunny decides how to fix it*. Jev now also
   chooses which path should carry traffic, and Bunny chooses how to make that
   happen. That is a deliberate change of the split, and the article has to state
   it rather than describe the original design.

**Deliberate compromises**

4. **TLS verification is fully disabled** container-wide. `sitecustomize.py`
   patches `ssl` at four levels so every Python library skips verification.
   Operator instruction, lab only, but it means the lab cannot detect a
   man-in-the-middle on its own API traffic and must never be copied anywhere
   real.
5. **The corporate proxy is mandatory now.** The transport used to bypass it
   because direct egress worked. It no longer does: a direct request comes back
   302 to a Forcepoint block page or 307 to the proxy login portal. The lab is
   now coupled to corporate proxy policy in a way it was not before.
6. **`x-opencode-session` is now sent.** The Go gateway hard-requires it and
   answers 400 without it. It is a documented contract, but it is per-conversation
   state the agent now carries.

**gNMI was asked for and is not available**

7. This FRR is built `--disable-protobuf`, and `gnmi`/`netconf` are absent from
   vtysh, so **gNMI cannot be used without rebuilding FRR from source** (order of
   an hour, through the same flaky proxy). mgmtd listens on 2623 but resets
   unauthenticated connections. SSH plus vtysh is what the lab uses. SSH is a
   legitimate northbound interface; it was the *usage* that was sloppy, not the
   protocol. Rebuilding FRR for gNMI is worth doing as a separate experiment and
   was not done here.

**Bugs and gaps, disclosed**

8. The environment prompt asserted **there is no ping binary**. That was false
   and is now corrected. It shows an inherited invariant that was never
   re-checked against the running image.
9. Four bugs in the path model were only caught by testing against live routers:
   next-hop-only matching, distance read from the wrong bracket group, `usable`
   computed from either router, and empty env vars defeating defaults. All fixed,
   all documented in 12.3. Any earlier number produced before those fixes should
   not be quoted.
10. `ModelError` was missing from the working tree, which is the no-fallback
    guarantee, and it took out repetition 1 of the first matched set. It had
    been dropped by an earlier uncommitted rewrite. Restored from git.
11. `RETRYABLE` still contains 301/302/307/308. That is what turned one
    permanently-redirecting response into an 85-107s stall. Moot now the proxy is
    used, but it should be removed and has not been.
12. Rep 3 `ospf_rev` recorded **no outage** at all. With a 0.2s probe interval
    that means the return path recovered inside 200ms. Plausible, but
    unexplained and asymmetric with the 34.2s forward figure.

**Superseded, must not be restated**

13. The old **324s** figure and its explanation are artifacts of the broken
    `/zen/v1` endpoint. The reasoning-token story behind it was also wrong: real
    cost is roughly 86 reasoning tokens per call.
14. The `chat_template_kwargs` suppression claim in `models.py` does not
    reproduce on the Go endpoint. Comment corrected, but if an earlier draft
    quotes 1831 -> 674 it should be struck.

**Scope**

15. Only the **container-kill** fault is in the matched set. The 0.62s
    interface-down figure is from an earlier OSPF-only session, so there is no
    agent-vs-OSPF comparison on a link failure.
16. **n=3**, one machine, one fault type, one topology. Directionally clear, not
    statistically meaningful. The agent figures in particular are a sample from a
    stochastic process.
17. Space Bunny is a free promotional model listed as *limited time*. It may
    disappear, as its endpoint nearly did during this work.
