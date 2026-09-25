# Head-to-Head: OSPF vs Agent-Based

Identical failure injected into two labs, both fully scripted, humans only
launched the orchestrators.

```
  SCENARIO 1  ffr-lab-ospf          SCENARIO 2  ffr-lab
  failure    scale r1 -> 0         failure    scale r1 -> 0
  T0         19:56:32.513          T0         20:13:28.000
       |                                   |
  +30.4s  pod dies (grace)             +10.0s  chaos logs R1 GONE
  +30.4s  first packet loss           +33.0s  JEV sees first failed ping
         ...... 31.8 s of blackhole  |
         ...... OSPF dead timer       +33.8s  INCIDENT declared
  +62.2s  ROUTE FLIP                  +34.8s  classify (1.0s, reply EMPTY)
         ping green                   +46.8s  Mercury render 12.0s
                                       +47.5s  apply 1.7s (3 nodes)
                                       +49.7s  VERIFY ping green
  ============== 12.5 s faster ============
```

## 1. Scoreboard

| Metric | OSPF | Agents | Delta |
|---|---:|---:|---|
| T0 -> restored forwarding | **62.2 s** | **49.7 s** | agents **-12.5 s (-20%)** |
| True outage after pod death | **31.8 s** | **~15.9 s** | agents **-15.9 s (-50%)** |
| Detection mechanism | dead timer (~30 s) | active poll (1 s) | agent polls 30x faster |
| Decision latency | 0 s (implicit) | 1.0 s | — |
| Plan synthesis | 0 s (SPF) | 12.0 s | agent +12.0 s |
| Apply | ~0 s (SPF install) | 1.7 s / 11 cmds | — |
| Verify | 0 s | ~1.2 s | — |
| Cost | $0 | **$0.000705** | 346 + 4125 tok |
| Human action | none | none | tie |
| External dependency | none | OpenRouter API | agent risk |
| Determinism | guaranteed | stochastic | agent risk |

## 2. The honest framing of the 12.5 s win

Two thirds of the OSPF number is not OSPF. The pod keeps forwarding for 30.4 s
after `scale -> 0` because of k8s' termination grace period, and only then does
the dead interval start counting. Strip that and:

- OSPF after actual death: **~31.8 s** (dead interval + LSA flood + SPF)
- Agents after actual death: **~15.9 s** (detect + classify + render + apply)
- **Agent advantage post-death: ~2x faster.**

With `--grace-period=0` (proposed in REPORT-V2) the gap widens further, because
the agent's 1 Hz poll would see the failure almost immediately while OSPF still
waits a full dead interval.


### Precision note: which baseline for the agent run?

The agent run has no per-second watch log (finding F5), so its outage start cannot
be pinned the way OSPF's can. Three baselines are defensible, and the article should
state which one it is quoting:

| Baseline | OSPF | Agents | Note |
|---|---:|---:|---|
| kill command -> restored | **62.2 s** | **49.7 s** | fully verifiable both sides; agent wins 12.5 s |
| outage start -> restored | **31.8 s** (first lost packet, watched) | **15.9 s – 19.7 s** (assumes the same ~30 s grace) | agent's outage start is unobserved |
| detection -> restored | n/a (no separate detect) | **15.9 s** | cleanest measure of agent response |

`v2-agents/chaos.log` logs `R1 GONE at 20:13:38` (T+10 s), but `v2-ospf/ospf-chaos.log`
logs `R1 pod DELETED` at T+0 while its own watch log proves forwarding continued for
30.4 s. The two labs label the same event differently, so T+10 s is almost certainly
"gone from the Kubernetes API" (Terminating), not "process killed". If instead T+10 s
were the true death, the agent outage would be 39.7 s — worse than OSPF's 31.8 s. The
Jev detection time (T+33.8 s) strongly suggests the ~30 s grace applied to both,
because a process still forwarding until ~T+30 s explains why the first failed ping
appeared at T+33 s.

**Recommended wording:** *"From the kill command, OSPF restored forwarding in 62.2 s
and the agent stack in 49.7 s. Excluding the shared 30 s Kubernetes termination grace,
the agent reacted in 15.9 s from its own detection versus OSPF's 31.8 s from first lost
packet."* That is defensible from the data on disk.

## 3. What the comparison does NOT prove

- **Not a controlled A/B at baseline.** See F1 — the agent lab did not start from
  a clean Path 1 state.
- **Different operations.** OSPF only had to flip a prefix. The agent had to
  reconcile a forward/return asymmetry across three nodes. That is a harder task
  than the one OSPF performed.
- **Single sample, n=1.** One run per scenario. No variance estimate, no
  repeated trials. 12.5 s could be partly noise.
- **The classifier did not actually classify** (F3). The 1.0 s classify step is
  a fallback, not a model decision.

## 4. Findings that affect the article

### F1 — The agent scenario did not start from a clean Path 1 (material)

`REPORT-V2.md` states: *"Baseline: both green on Path 1, clean single-nexthop
FIBs."* The raw evidence contradicts this for the agent lab:

```
v2-agents/before.txt  (20:13:32, 4 s after T0, BEFORE the pod died):
  === BEFORE (Path 1 active) ===          <- header
  * 10.1.5.2, via gre-r3, weight 1        <- data: this is PATH 0

v2-ospf/ospf-before.txt (genuine Path 1):
  * 10.1.2.2, via gre-r1, weight 1        <- PATH 1 first hop
```

`10.1.5.2` is r3, the first hop of **Path 0**. The rendered plan corroborates it:
rc1 only needed **2 commands**, and only for `10.1.3.0/24` — because rc1 was
already pointing at r3 for the rest. The real work was on `r2` (3 drain cmds) and
`rc2` (6 cmds).

**Reconstruction:** the lab was in a split state — rc1 forward via Path 0, rc2
return via Path 1 (`r2` -> `r1`). Deleting r1 killed the *return* path, so ping
failed. The agent's repair made both directions Path 0.

**Why this matters:**
1. The headline comparison is not apples-to-apples at t=0.
2. It is *not* purely negative — an asymmetric-return failure is a realistic
   production bug (partial migration, half-applied change) and arguably a harder
   repair than a clean path death. Worth framing that way if you use it.
3. `failback-path1.sh` presumably was not run before this scenario. A pre-flight
   assertion (`assert rc1 via gre-r1 AND rc2 via gre-r2`) would have caught it.

### F2 — `gre-r1 up=True` while R1 was dead (instrumentation gap)

```
[20:14:01] [JEV] poll: ping FAIL - immediate incident (no debounce), gre-r1 up=True
```

R1's pod was deleted at 20:13:38, 23 s earlier. The monitor's tunnel-state probe
still reported the GRE interface as up. In Kubernetes the interface can persist
briefly after process death, so `up=True` is not proof of liveness. The ping was
the only reliable signal — which is exactly what made the incident fire, but it
means the `rc1_gre_r1_state` field in the evidence bundle is unreliable and should
not be quoted as a signal in the article.

### F3 — The classify LLM returned nothing, but a 0.9 decision shipped

```
[20:14:02] [JEV] LLM call latency=1.0s ... 'completion_tokens': 240 ... 'cost': 0.000205375
[20:14:02] [JEV] LLM raw reply: EMPTY
[20:14:02] [JEV] DECISION -> {... "confidence": 0.9, "action": "FAILOVER_TO_PATH0"}
```

240 completion tokens were billed ($0.000205) and the parsed content was empty,
yet a calibrated-looking `confidence: 0.9` was emitted. That value cannot have come
from this model's output. Most likely a deterministic fallback classified the
evidence (ping FAIL + known failed link -> failover).

**Consequence:** the Jev role did not contribute reasoning in this run. The v1 run
(`lab-article/`) did return real JSON, so this is a regression between v1 and v2 —
worth checking what changed in the parsing path. For the article, either state
"classification fell back to deterministic rules in run 2" or re-run with the raw
content logged.

### F4 — No TypeSafe Jev in either scenario

```
jev-monitor.log: monitor up (model=inception/mercury-2)
config-agent.log: config agent up (model=inception/mercury-2.5)
```

Both roles are Inception-family models via OpenRouter chat completions. The
`~typesafe/jev-latest` decisions endpoint (wired in `research/agent/jagent.py`) was
not used. If the article names "Jev" as the detector, footnote that the Jev role
ran on `inception/mercury-2`.

### F5 — Different grace behaviour between the two runs

```
v2-ospf/ospf-chaos.log :  "R1 pod DELETED (router death) at 19:56:32"   (T0 + 0.0 s)
v2-agents/chaos.log    :  "R1 GONE at 2026-09-24T20:13:38"             (T0 +10.0 s)
```

The OSPF run has a per-second watch log proving forwarding continued for 30.4 s.
The agent run has **no** watch log, so the true outage start is unobservable and
the 33.8 s detect figure may be inflated by an unknown amount of dead time. For a
fair headline, add the same per-second watcher to the agent scenario.

## 5. Recommendations before publishing

| # | Action | Why |
|---|---|---|
| 1 | Re-run the agent scenario from a **verified clean Path 1** with a pre-flight assert | removes finding F1; makes the A/B defensible |
| 2 | Add a per-second watch log to the agent scenario | bounds outage start (F5) |
| 3 | Log the raw LLM content on parse failure; alert on `EMPTY` | F3 — a silent fallback is a production risk, not a footnote |
| 4 | Run n>=3 per scenario, report median + spread | 12.5 s from n=1 is weak |
| 5 | Either add `--grace-period=0` as a third condition, or quote post-death numbers | removes the 30 s artefact |
| 6 | Fix or remove the `gre-*_state` evidence field | F2 — it publishes a misleading signal |
| 7 | Decide the Jev naming: use TypeSafe Jev, or stop calling mercury-2 "Jev" | F4 |

## 6. Suggested narrative arc for the article

1. **Same failure, two doctrines.** OSPF optimises for determinism; the agent
   stack optimises for responsiveness + synthesised repair.
2. **Be precise about what the 12.5 s is.** 30.4 s of the 62.2 s is k8s grace,
   not OSPF. The real contest is 31.8 s vs 15.9 s.
3. **Show the cost honestly.** 12.0 s of the agent's 49.7 s is the LLM rendering
   the plan. That is a real, permanent tax on this architecture — unless a
   deterministic planner replaces it for the common cases.
4. **The interesting engineering is the safety layer**, not the speed:
   dead-node-aware planning (v1's fatal flaw), allowlist validation, abort-on-
   incomplete, self-verification, `rp_filter=0` for asymmetric paths.
5. **Close with the limitations section** — findings F1–F5 make the write-up
   credible and pre-empt reviewer objections.
