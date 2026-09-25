# Scenario 2 — Agent-Based Failover

**Lab:** `ffr-lab`  |  **Failure:** R1 pod deleted (`scale r1 --replicas=0`) — identical to Scenario 1  
**T0:** `1790280808.0` = **2026-09-24 20:13:28**  
**Result:** `t_repair_total_s = 49.7 s`, `repaired: true`, `applied_clean: true`

---

## 1. Mechanism

No routing protocol. Four cooperating roles run on the `ssh-server` jump host:

| Role | Model | Job |
|---|---|---|
| `jev-monitor.py` | `inception/mercury-2` | 1 Hz polling; incident on first failed ping |
| Jev LLM classify | `inception/mercury-2` | turn evidence into a typed decision |
| `config-agent.py` | `inception/mercury-2.5` | probe liveness, render a route plan, apply via `vtysh`/SSH |
| executor | — | validate against allowlist, apply, verify |

The agent path replaces 'wait for a timer' with 'poll, judge, synthesise, act'.

## 2. Timeline

```
T0 = 20:13:28.000   kubectl scale r1 --replicas=0
  |
  + 4.0s   20:13:32  BEFORE snapshot taken:
  |               rc1 route = * 10.1.5.2 via gre-r3   <-- ALREADY ON PATH 0 (see Finding F1)
  |               ping 0% loss, rtt 2.196/2.267/2.367
  |
  +10.0s   20:13:38  chaos.log: "R1 GONE"
  |
  |         ..... no per-second watch log for this scenario (gap in instrumentation)
  |
  +33.0s   20:14:01  JEV poll -> ping FAIL, immediate incident (no debounce)
  |               gre-r1 up=True  <- tunnel still advertised although pod is gone
  |
  +33.8s   20:14:01.809  INCIDENT declared, detect_latency = 33.8 s
  |
  +34.8s   20:14:02  Jev LLM call, latency 1.0 s, 346 tok, $0.000205
  |               *** LLM raw reply: EMPTY ***
  |               DECISION conf=0.9 action=FAILOVER_TO_PATH0 (from fallback path, see F3)
  |
  +35.8s   20:14:03  config-agent trigger accepted (t_trigger = 1790280842.8)
  |
  +36.0s   20:14:04  liveness probe:
  |               reachable = [rc1-svc, r2-svc, rc2-svc]   dead = [r1-svc]
  |
  +37.8s   20:14:06  Mercury 2.5 render starts  (llm_render_latency_s = 12.0)
  |               -> 11 commands / 3 nodes; dead node r1-svc deliberately skipped
  |
  +45.8s   20:14:13  apply begins
  |               rc1-svc   2 cmds    rc=0
  |               r2-svc    3 cmds    rc=0
  |               rc2-svc   6 cmds    rc=0            apply_s = 1.7
  |
  +49.7s   20:14:17  VERIFY ping vm1->vm2 : OK - REPAIRED
```

## 3. Time budget

| Component | Duration | Notes |
|---|---|---|
| kill -> first detected failure | **33.8 s** | includes k8s grace; no watch log to bound it better |
| Jev classify (LLM) | **1.0 s** | 346 tok, $0.000205, reply EMPTY |
| Mercury 2.5 render | **12.0 s** | 11 cmds / 3 nodes, dead-node aware |
| Apply (3 nodes) | **1.7 s** | all `rc=0` |
| Verify | **~1.2 s** | ping green |
| **Total T0 -> restored** | **49.7 s** | matches `metrics.json` |
| **Post-detection reaction** | **15.9 s** | 49.7 - 33.8 |

> 15.9 s is the number that isolates agent behaviour from pod teardown.

## 4. Log snippets (verbatim)

### 4.1 Chaos
```
v2-agents/chaos.log:
T0=1790280808. -- KILLING R1 pod (router death, identical to OSPF lab)
deployment.apps/r1 scaled
NAME                  READY   STATUS        RESTARTS   AGE
r1-86b4697dc9-xqwn7   1/1     Terminating   0          8m32s
R1 GONE at 2026-09-24T20:13:38
```

### 4.2 Monitor + decision
```
v2-agents/jev-monitor.log:
[2026-09-24T20:13:22] [JEV] monitor up (model=inception/mercury-2). Polling Path 1 every 1s.
[2026-09-24T20:14:01] [JEV] poll: ping FAIL - immediate incident (no debounce), gre-r1 up=True
[2026-09-24T20:14:01] [JEV] INCIDENT declared at 1790280841.8 (t0=1790280808.0, detect_latency=33.8s)
[2026-09-24T20:14:02] [JEV] LLM call latency=1.0s usage={'prompt_tokens': 106, 'completion_tokens': 240, 'total_tokens': 346, 'cost': 0.000205375, ...}
[2026-09-24T20:14:02] [JEV] LLM raw reply: EMPTY
[2026-09-24T20:14:02] [JEV] DECISION -> {"ts": 1790280841.8085728, "t0": 1790280808.0, "detect_latency_s": 33.8, "failed_link": "rc1-r1 (Path1)", "confidence": 0.9, "action": "FAILOVER_TO_PATH0"} (trigger armed for config agent)
```

### 4.3 Dead-node-aware planning + apply
```
v2-agents/config-agent.log:
[2026-09-24T20:14:02] [MERCURY] trigger: {"ts": 1790280841.8085728, ... "confidence": 0.9, "action": "FAILOVER_TO_PATH0"}
[2026-09-24T20:14:04] [MERCURY] reachable=['rc1-svc', 'r2-svc', 'rc2-svc'] dead=['r1-svc']
[2026-09-24T20:14:13] [MERCURY] applying on rc1-svc: ['no ip route 10.1.3.0/24 10.1.2.2', 'ip route 10.1.3.0/24 10.1.5.2']
[2026-09-24T20:14:14] [MERCURY] rc1-svc apply rc=0 :: Note: this version of vtysh never writes vtysh.conf
[2026-09-24T20:14:14] [MERCURY] applying on r2-svc: ['no ip route 10.1.1.0/24 10.1.3.1', 'no ip route 10.1.2.0/24 10.1.3.1', 'no ip route 10.1.8.0/24 10.1.4.254']
[2026-09-24T20:14:14] [MERCURY] applying on rc2-svc: ['no ip route 10.1.1.0/24 10.1.4.1', 'ip route 10.1.1.0/24 10.1.7.1', ... 'ip route 10.1.3.0/24 10.1.7.1']
[2026-09-24T20:14:15] [MERCURY] rc2-svc apply rc=0
[2026-09-24T20:14:17] [MERCURY] VERIFY ping vm1->vm2: OK - REPAIRED
[2026-09-24T20:14:17] [MERCURY] METRICS {"t0": 1790280808.0, "t_detect_latency_s": 33.8, "t_trigger": 1790280842.8, "llm_render_latency_s": 12.0, "apply_s": 1.7, "repaired": true, "t_repair_total_s": 49.7, "applied_clean": true}
```

### 4.4 The plan (verbatim)
```json
v2-agents/rendered-plan.json:
{ "steps": [
  { "node": "rc1-svc", "cmds": [
      "no ip route 10.1.3.0/24 10.1.2.2",
      "ip route 10.1.3.0/24 10.1.5.2" ] },
  { "node": "r2-svc",  "cmds": [
      "no ip route 10.1.1.0/24 10.1.3.1",
      "no ip route 10.1.2.0/24 10.1.3.1",
      "no ip route 10.1.8.0/24 10.1.4.254" ] },
  { "node": "rc2-svc", "cmds": [
      "no ip route 10.1.1.0/24 10.1.4.1", "ip route 10.1.1.0/24 10.1.7.1",
      "no ip route 10.1.2.0/24 10.1.4.1", "ip route 10.1.2.0/24 10.1.7.1",
      "no ip route 10.1.3.0/24 10.1.4.1", "ip route 10.1.3.0/24 10.1.7.1" ] }
 ] }
```

> Note the plan contains **no steps for `r1-svc`** — the probe marked it dead, so
> the planner excluded it. That was the v1 run's fatal flaw (planning commands on a
> dead node); REPORT-V2 records it as fixed by design.

### 4.5 Before / after
```
v2-agents/before.txt:
--- rc1 route to vm2 ---   Known via "static", distance 1, metric 0, best
  * 10.1.5.2, via gre-r3, weight 1        <-- header claims Path 1, data says Path 0

v2-agents/after.txt:
--- ping vm1->vm2 ---   0% packet loss, rtt 1.452/1.494/1.520
--- rc1 route to vm2 ---   Known via "static", distance 1, metric 0, best
  * 10.1.5.2, via gre-r3, weight 1        <-- unchanged from before
```

## 5. Technical analysis

**Strengths demonstrated**
- **Dead-node awareness.** A liveness probe ran before planning; unreachable
  nodes were excluded from the plan rather than causing a doomed apply.
- **Bidirectional repair.** It did not only flip the ingress router — it also
  drained the transit router (`r2`) and moved the egress router (`rc2`), which
  is what actually restored the round trip.
- **Synthesised, not templated.** The route set was generated per incident from
  live `show ip route` dumps, not replayed from a stored script.
- **Auditable.** Every command is in `rendered-plan.json`; every return code and
  FRR write in `config-agent.log`.
- **Self-verifying.** The agent measured its own success (ping green) before
  declaring `repaired: true`.

**Weaknesses / risks exposed**
- **An LLM sits in the critical path.** 12.0 s of the 49.7 s (24%) is Mercury
  rendering the plan. OSPF pays 0 s there. That is the price of the approach.
- **The classify step produced no model output this run** (`LLM raw reply: EMPTY`)
  yet still emitted `confidence: 0.9`. The number is not model-derived — see F3.
- **No debounce on the incident trigger.** A single failed ping declares an
  incident. Cheap and fast, but a 1-packet blip can trigger a full re-route.
- **Blind to tunnel state.** `gre-r1 up=True` while the R1 pod was gone: the
  monitor's tunnel check did not reflect pod liveness.
- **Asymmetric-state risk (see F1).** The lab entered this run with rc1 already
  on Path 0 and rc2 still on Path 1, which is exactly the condition the agent
  ultimately repaired.

## 6. Raw metrics
```json
v2-agents/metrics.json:
{
 "t0": 1790280808.0,
 "t_detect_latency_s": 33.8,
 "t_trigger": 1790280842.8,
 "llm_render_latency_s": 12.0,
 "apply_s": 1.7,
 "repaired": true,
 "t_repair_total_s": 49.7,
 "applied_clean": true
}
```
