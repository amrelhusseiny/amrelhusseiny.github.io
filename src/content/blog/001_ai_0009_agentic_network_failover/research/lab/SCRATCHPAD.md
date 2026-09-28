# SCRATCHPAD - agentic dual-path failover lab

Working notes: what was decided, what was built, what broke, and what the
lab actually proved. Written for the article author, not for the code.

---

## 1. The idea

Two network paths between a client and a server. Kill something on the primary
path. Either OSPF notices and reroutes by itself, or two agents notice and one
of them fixes it. The point of the article is the second one: what the agents
actually did, in detail, with the raw reasoning visible.

Two agents with deliberately separate jobs:

- **TypeSafe Jev** decides. Reads router logs, says which router is faulty.
- **Space Bunny** acts. Given the fault, works out a fix and applies it.

Non-negotiable design rule carried through everything: **no fallbacks**. If a
model returns empty or unparseable output, the run aborts. Nothing is ever
synthesised or guessed.

---

## 2. Topology

One flat Docker bridge, 6 routers, no L3 routing between bridges (does not work
on this WSL2 host). All devices are FRR 10.3 routers with sshd, reached by SSH
key auth from the agent container.

```
  rc1  10.90.0.11   client edge   client net 10.90.1.1/32 behind it
  r1   10.90.0.12   transit       PRIMARY path
  r2   10.90.0.13   transit       PRIMARY path
  rc2  10.90.0.14   server edge   server net 10.90.8.1/32 behind it
  r3   10.90.0.15   transit       STANDBY path
  r4   10.90.0.16   transit       STANDBY path

  primary :  rc1 -> r1 -> r2 -> rc2
  standby :  rc1 -> r3 -> r4 -> rc2
```

Baseline is **primary-only**: rc1 has no route toward r3. Restoring traffic
therefore means the agent has to install an alternate path itself, which is a
real configuration change rather than a no-op.

---

## 3. Framework: LangGraph, and why

Originally hand-rolled plain Python with an `if`-statement orchestrator. That was
**option A**: Space Bunny returned a JSON plan and *my code* executed it over
SSH. The user asked for **option B** instead - Bunny gets a live SSH tool and
issues commands itself, each logged as it happens - and asked for the whole thing
on LangChain/LangGraph.

LangGraph was chosen over a bare LangChain AgentExecutor so the workflow is an
inspectable graph rather than a hidden loop, which matters for an article whose
whole point is showing the reader the decision trail.

```
START -> capture -> judge -> (healthy -> END)
                          (faulty  -> bunny -> capture_after
                                     -> judge_after -> END)
```

Files:

| file | role |
|---|---|
| `topology.py`  | devices, noise filter, and the system prompt text |
| `models.py`    | `JevChatModel` (a real `BaseChatModel`) + `build_bunny_model()` |
| `tools.py`     | the two LangChain tools: `ssh`, `vtysh` |
| `graph.py`     | the `StateGraph` |
| `monitor.py`   | entrypoint, builds and invokes the graph |
| `transport.py` | the only path to a router |
| `trail.py`     | writes the decision trail |

### Jev as a real LangChain model

Jev is reached at `POST https://opencode.ai/zen/v1/systemone`, which is **not**
a chat API - it takes `{model, state, questions}`. It is wrapped as a subclass of
`langchain_core.language_models.chat_models.BaseChatModel`, so `_generate()` does
the HTTP call and returns an `AIMessage`. Jev can therefore be used anywhere in
the graph like any other LangChain model.

One gotcha: `_identifying_params` must be a `@property`. As a plain method,
LangChain raises `TypeError: method object is not iterable`.

### Bunny as a real ReAct agent

`create_react_agent` from `langgraph.prebuilt`, with `ChatOpenAI` pointed at the
OpenAI-compatible Zen endpoint. **Verified before building:** that endpoint does
support native OpenAI tool calling, and unprompted it emitted parallel `ssh(...)`
calls. So this is a real tool loop, not a JSON-parsing imitation.

---

## 4. How the decision is actually made

This changed several times during the work. Final design, per the user:

- **One API call per log line.** Not one call per blob of logs. Each line is
  judged on its own so a single real error cannot be diluted by surrounding
  noise, and vice versa.
- **Incremental.** A per-router cursor means only *new* lines are judged each
  cycle. A steady-state cycle costs zero API calls. If a log shrinks (container
  recreated) the cursor resets.
- **No threshold.** Jev is asked a categorical question and *names* the state:
  `normal` or `failed`. One `failed` anywhere triggers failover. Nothing to tune.
- **No debounce, no cooldown, no waiting.** The user was explicit about this.
- **Unreachable routers count.** A router that will not answer SSH produces the
  item `"r1 10.90.0.12 did not respond to SSH: ..."`, which is judged by Jev like
  any other line. A dead router is still a decision, not a hardcoded `if`.

### The `noul` polarity trap

Jev's `noul` is P(yes to the question you asked). Asking *"Is router X operating
normally?"* gives 0.85 for healthy. Asking *"Does this log line report a
failure?"* gives **0.98 for a failure**. Same model, opposite reading. The
categorical `choice` question type avoids the ambiguity entirely and is what the
final code uses - it returns `{choice, confidence, probabilities}`.

Validated 7/7 against hand-labelled lines including both real failures and
benign boot noise.

---

## 5. What Space Bunny is told

The system prompt carries **topology only** - device names, addresses, roles,
which path is primary, and where the client and server networks sit. No fault
hypothesis, no template, no suggested commands. The user message is the list of
lines Jev marked failed, plus *"What is wrong, and how can you fix it?"*.

The `vtysh` tool carries a deny list (`reboot`, `write erase`, `delete`, `format`,
`kill`, `shutdown`, `reload`). That is a guard rail against destroying the lab,
not a hint: it does not steer the diagnosis, it only refuses those verbs.

---

## 6. Results

### Healthy baseline

```
capture[before]: 0 item(s) to judge
JEV[before] verdict: faulty=none
CONCLUSION : healthy_no_action
elapsed     : 3.04s
```

Zero API calls, three seconds, no dispatch. Correct.

### Fault: `docker stop agt-r1`

```
capture[before]: 1 item(s) to judge
jev r1   failed conf=1     r1 10.90.0.12 did not respond to SSH
JEV[before] verdict: faulty=['r1']
handing to Space Bunny: 1 faulty router(s)
... 68 messages ...
CONCLUSION : still_faulty
faulty before : ['r1']
faulty after  : ['r1', 'rc1']
elapsed       : 324.39s
```

Bunny confirmed r1 was genuinely hard-down rather than just refusing SSH: no ARP
reply, a port scan of the whole /24 that found everything *except* .12, and an
unreachable loopback. It then identified the actual design flaw - rc1 had no
alternate route at all - and applied:

```
rc1  no ip route 10.90.8.1/32 10.90.0.12     (drop the dead primary)
rc1  ip  route 10.90.8.1/32 10.90.0.15     (point it at r3)
rc1  ip  route 10.90.2.2/32 10.90.0.15
rc1  ip  route 10.90.3.2/32 10.90.0.15
```

**Traffic restored and independently verified from outside the agent:**

```
rc1 -> 10.90.8.1  REACHABLE     (was: No route to host)
rc2 -> 10.90.1.1  REACHABLE
```

r1 stayed down - the agent rerouted around it, it did not revive it. That is the
honest limit of what a config agent can do.

---

## 7. Findings worth writing about

**F1 - the monitor flags its own repair as a new fault.** After the fix, the
post-change re-read returned `faulty_after = ['r1', 'rc1']`. rc1 was judged
failed with confidence 1.0 on this line, which Bunny's own config burst had just
produced:

```
MGMTD: Locking for DS 2 failed, Err: 'Lock already taken on DS by another session!'
```

That is FRR config-lock contention from issuing several vtysh writes in quick
succession - routine bookkeeping, not a fault. The agent fixed the network and
then the monitor reported the fix as a new problem. This is the single most
interesting thing the lab produced.

**F2 - benign boot chatter causes false positives.** On a completely healthy lab,
`MGMTD: XXX txn in progress, retry init` was judged `normal` on rc1 (confidence
0.02) and `failed` on r2 (confidence 0.06). **Same line, opposite verdicts, both
low confidence.** Post-restart internals (`BE-client: msg_conn_send_msg`,
`NB_OP_CHANGE: oper_walk_done`) were judged `failed` at confidence 1.0.

**F3 - noise filtering is a blunt instrument.** Only the `libyang Invalid ...
/frr-vrf:.../state` lines were filtered, per the user's instruction that
"Invalid doesn't mean anything". A broader filter was deliberately *not* applied,
because the lab's very first real fault contained the word: `invalid address
127.0.0.1/8` was a genuine config rejection. Filtering on the word would have
hidden exactly the class of failure the lab exists to catch.

**F4 - the cursor hides F2 in steady state.** Because only new lines are judged,
the boot-chatter false positives fire once after a restart and never again. A
baseline run is clean only because a prior run already consumed those lines. Any
article must disclose that the first cycle after a restart is not representative.

**F5 - the agent is slow.** 324 seconds, 68 messages. `space-bunny-free` is a
reasoning model; each turn costs 20-40s. It also burned several turns rediscovering
that the routers have no `ping` binary and that `show interfaces` is not valid in
this FRR build. Perfectly correct behaviour, just not fast.

---

## 8. Everything that broke on the way

Kept because each one is a real trap for anyone repeating this.

| symptom | cause | fix |
|---|---|---|
| agent aborted instantly, every run | `OPENCODE_API_KEY` not reaching the container | `env_file` in compose |
| `CERTIFICATE_VERIFY_FAILED` from inside the container | corporate Forcepoint proxy, CA absent from the Debian store | host env exported into the container, `verify=False` per operator instruction |
| `verify=False` appeared to be ignored | **passing an explicit `transport` to `httpx.Client` makes it ignore the client-level `verify=`** | build the transport with `verify=False` itself |
| intermittent `307 Authentication Required` | filtering proxy; neither httpx nor the openai client retries a 3xx | `Retry307Transport(httpx.HTTPTransport)` |
| `space-bunny-free` returned empty content | reasoning consumed the whole `max_tokens` budget | `max_tokens=12000` (3000 is not enough) |
| FRR rejected `ip address 127.0.0.1/8` on `lo` | FRR 10 validation | drop the line from every config |
| `libyang Invalid ... vrf/state` at boot | FRR 10.3 runtime state reporting | filtered from the decision input |
| every `ip route` was lost on restart | routes were poked in with `vtysh` at runtime, never in `frr.conf` | persist routes in `frr.conf` |
| all config commands returned rc=1 | FRR 10 refuses config lines via a bare `vtysh -c` | wrap non-read-only commands in `-c "conf t" ... -c end` |
| `TypeError: 'AIMessage' object is not subscriptable` | used `m["tool_calls"]` on a message object | `m.tool_calls` |
| `TypeError: 'method' object is not iterable` | `_identifying_params` defined as a method | make it a `@property` |
| SSH worked but no `ping` in the lab | image has no `iputils-ping`; FRR `ping` not compiled in | use a TCP connect to sshd as an L3 reachability probe |

Two process notes:

- Agent output is written by the container as root, so `rm -rf out/...` from the
  host fails with `Permission denied`. Clean those from inside the container.
- Long agent runs must be started with `docker exec -d`, otherwise an SSH command
  timeout kills the run mid-flight and the bundle never finalises.

---

## 9. Housekeeping and open items

### Superseded material removed

The earlier Containerlab and Kubernetes attempts were deleted from this folder as
unrelated to this run:

```
analysis-v2/        analysis of the invalid v2 run (mercury-2, not Jev)
lab-compare/        that run's raw logs (v2-agents, v2-ospf)
lab-article/        the same run's logs and its 0.9-confidence decision.json
k8s-dualpath/       Kubernetes manifests
k8s-ospf/           Kubernetes OSPF manifests
frr-dualpath-lab/   Containerlab topology
lab-backups/        lab v1-v4 snapshots (167 files)
REDEPLOY_PLAN.md    the Jev systemone redeploy plan - done, superseded by section 4
```

All were git-tracked, so `git checkout` brings any of them back if wanted.

### Where things are documented now

- [../README.md](../README.md) - index and orientation
- [../RUN-REPORT.md](../RUN-REPORT.md) - **authoritative** results and findings
- [README.md](README.md) - how to build and run the lab
- [../evidence-runs/](../evidence-runs/) - the raw run bundle

The findings numbered F1-F5 in section 7 below were written mid-run and use an
earlier numbering. `../RUN-REPORT.md` supersedes them with figures read back out
of the evidence bundle.

### Still open

- The OSPF comparison lab (`ospf-lab`, 10.91.0.0/24) was never stood up. Only the
  agent lab was built, so the two scenarios in the article are not yet directly
  comparable.
- `CONCLUSION: still_faulty` is technically true - r1 is still down - but it also
  folds in finding F1. The verdict does not separately assert that traffic was
  restored, which is the claim the article actually wants to make. Worth adding a
  connectivity assertion to the conclusion.
- The F2 false positives are unfixed by design. Whether to widen the noise filter
  is an editorial decision, not a technical one.
- F3 suggests a cheap improvement that was deliberately not made: act on `failed`
  at high confidence, and treat low-confidence verdicts as inconclusive. That
  reintroduces a threshold, which was explicitly ruled out.
- Article corrections still outstanding: "Typeface" -> TypeSafe, "Mercurey" ->
  Mercury, and state that the action model is `space-bunny-free` because Mercury
  was unavailable.
- The lab is torn down. `lab/docker/agent/ca/` holds the corporate proxy CA, which
  is worth gitignoring rather than committing.
