# Failover race: OSPF (automatic) vs Jev + Mercury agents (static routes)

Two parallel labs, same overlay topology (10.1.0.0/16 over GRE tunnels on
Calico), same client ping vm1 (10.1.1.1) -> vm2 (10.1.8.1).

| | Scenario 1: OSPF | Scenario 2: Agents |
|---|---|---|
| Namespace | `ffr-lab-ospf` | `ffr-lab` |
| Routing | FRR OSPF area 0, out-of-box timers (hello 10s / dead 40s), Path1 cost 10, Path0 cost 100 | Static routes, Path 1 only; Path 0 tunnels idle |
| Failure | TRUE gray: `SIGSTOP ospfd` on r1 (process alive, no LSA flush, hellos stop, links stay UP) | Hard: `ip link set gre-r1/gre-rc1 down` (rc1 + r1) |
| Detector | 1s watcher: `show ip route` on rc1 + ping from vm1 | `jev-monitor.py`: 1s polls, incident on FIRST ping fail (no debounce) |
| Repair | OSPF SPF reconvergence | Mercury-2.5 renders plan -> allowlist-validated `vtysh` apply on rc1/r1/r2/rc2 |

## Results

| Metric | OSPF | Agents |
|---|---|---|
| Detection / route flip | **38.0s** (dead-timer expiry, textbook 40s) | **10.4s** (1 failed poll + evidence gather over SSH) |
| Jev classify call | n/a | 1.3s, $0.00021 |
| Mercury render call | n/a | 5.5s, $0.00048 |
| Apply | SPF install (~0s after flip) | **2.3s** (4 nodes via vtysh) |
| End-to-end repair | **38.0s** | **24.2s** |
| Packet loss during event | **none** (kernel FIB survived; control plane blind 38s) | hard outage, then 0% loss |
| Total OpenRouter cost | $0 | ~$0.0007/run |

Bonus datapoint: OSPF **fail-stop** variant (SIGKILL ospfd -> LSA flush) reconverged
in **2.2s** - OSPF is fast when it gets an explicit signal; the 38s is what a
*gray* failure costs with default timers. The agents' value: explicit-signal
speed on failures that give no signal + autonomous repair.

## Timeline excerpts

OSPF (`ospf/ospf-watch.log`, 31 polls, route via Path1 until flip):
```
T0+0s   route=[* 10.1.2.2, via gre-r1] ping=[0% packet loss]   # data still flows!
...     (38 identical polls, control plane dead, FIB intact)
T0+38s  route=[* 10.1.5.2, via gre-r3] ping=[0% packet loss]   # flipped
```

Agents (`agents/clean-run/`):
```
T0       chaos.sh: BEFORE ping 0% loss, route via 10.1.2.2; Path 1 DOWN
T0+10.4s [JEV] INCIDENT -> {link_failure, rc1-r1, conf 0.95, FAILOVER_TO_PATH0}
T0+11.7s [MERCURY] trigger received, statedump, render call (5.5s)
T0+~22s  [MERCURY] applied on rc1/r1/r2/rc2 (2.3s)
T0+24.2s [MERCURY] VERIFY ping: OK - REPAIRED
```

## Files

- `ospf-scenario.sh` - scenario 1 runner (before/break/watch/after/restore)
- `ospf/` - before.txt, chaos.log, watch.log (every poll), after.txt, metrics.json
- `agents/clean-run/` - before/after, chaos.log, jev-monitor.log, config-agent.log,
  decision.json, rendered-plan.json, metrics.json
- `agents/failed-run1/` - an earlier run where Mercury's render omitted rc1
  (`repaired:false`, clean abort telemetry). Kept as evidence of LLM variance
  and of the guardrails working (allowlist + node-coverage validator + retry,
  added after this run).
- `failback-path1.sh` - deterministic Path0->Path1 restore (direct exec, no SSH quoting)

## Caveats (for article honesty)

1. Different failure modes: gray (OSPF) vs hard-down (agents). OSPF never
   dropped a packet; agents healed a real outage. Times are not interchangeable;
   the fair claim: "agents beat default-timer OSPF reconvergence 38s -> 24s
   while also repairing hard failures OSPF can't fix without a signal."
2. Agent detection (10.4s) is dominated by sequential SSH polling overhead, not
   the LLM (0.8-1.3s). A streaming log tail would cut it to ~2s.
3. Mercury render quality varies run to run (see failed-run1); the coverage
   validator + single self-correction retry + abort-on-incomplete are load-bearing.
   Mercury also needs max_tokens>=4000 (reasoning-heavy).
4. No Jev/Typesafe model exists on OpenRouter (458 models checked); JEV_MODEL is
   currently `inception/mercury-2` stand-in, one env var to swap.
5. FRR static replace semantics: always `no`+`ip` as a pair or ECMP duplicates
   accumulate in the kernel FIB (seen live; `ip route show proto 196` to audit).
