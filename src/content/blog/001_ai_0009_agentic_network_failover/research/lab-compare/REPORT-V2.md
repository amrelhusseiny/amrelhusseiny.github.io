# IDENTICAL-failure race: R1 router pod deleted (`scale r1 -> 0`), zero touch

Same failure, both labs, fully scripted (orchestrators run start-to-finish,
humans only launched them). Baseline: both green on Path 1, clean single-nexthop FIBs.

| | Scenario 1: OSPF (`ffr-lab-ospf`) | Scenario 2: Agents (`ffr-lab`) |
|---|---|---|
| Failure | R1 pod scaled to 0 (T0 = scale cmd) | R1 pod scaled to 0 (T0 = scale cmd) |
| Detector | 1s watcher: rc1 `show ip route` + vm1 ping | `jev-monitor.py`, incident on FIRST failed poll |
| Repair | OSPF dead-timer + SPF | Mercury-2.5 plan (dead-node aware) + `vtysh` apply |

## Results (raw, from T0 = kill command)

| Metric | OSPF | Agents |
|---|---|---|
| Detect / route flip | **62.2s** | **33.8s** |
| Jev classify | n/a | ~1s, conf 0.9, FAILOVER_TO_PATH0 |
| Mercury render | n/a | 12.0s (incl. dead-node probe) |
| Apply | SPF (~0s post-flip) | **1.7s** |
| End-to-end repair | **62.2s** | **49.7s**, `repaired:true` ✅ |
| Loss window | hard outage (r1 dead = forwarding dead) | hard outage, then 0% loss |

## Reading the numbers (termination-grace effect)

`scale -> 0` honors the 30s pod termination grace: the R1 process keeps
forwarding for ~30s after T0, so BOTH timelines include ~30s of "dying".
True reaction after actual death: OSPF ~32s (dead 40s timer), agents ~20s
(detect ~4s + render + apply). Either way the agents win by ~12-13s, and the
gap would widen further with instant death (`--grace-period=0`, proposed rerun).

## What the agents did right this run

- Reachability probe: `reachable=[rc1,r2,rc2] dead=[r1-svc]` - plan covered
  exactly `{rc1-svc, r2-svc, rc2-svc}`, no steps for the dead node (the previous
  run's fatal flaw, now fixed by design).
- applied_clean:true, verified ping green on Path 0, full transcripts kept.

## Hardening found along the way (all fixed live + persisted)

1. **Strict RPF vs asymmetric failover**: after failback, Path-0 arrivals die on
   rc2 (reverse route points Path 1). Fix: `rp_filter=0` on all GRE ifaces,
   persisted in `01-router-script-cm.yaml`. Any ECMP/transit design must do this.
2. **FRR static replace != swap**: `no`+`ip` pairs must match exactly or ECMP
   duplicates accumulate in the kernel FIB (`ip route show proto 196` audit).
   `failback-path1.sh` is now canonical: wipe all 10.1.x statics, install exact set.
3. **LLM plan variance**: self-correction retry (max 3) + node-coverage validator +
   abort-on-incomplete instead of partial apply.

## Files

- `ospf-r1kill-scenario.sh`, `agent-r1kill-scenario.sh` - hands-off orchestrators
- `v2-ospf/` - before/after, chaos log, per-second watch log, metrics
- `v2-agents/` - before/after, chaos log, BOTH full agent transcripts,
  decision.json, rendered-plan.json, metrics.json
- `failback-path1.sh` - canonical Path0->Path1 restore (idempotent)
- Previous rounds: `ospf/` + `agents/` (gray vs hard-down, first comparison),
  `REPORT.md`.
