# Scenario 1 — OSPF-Managed Failover

**Lab:** `ffr-lab-ospf`  |  **Failure:** R1 pod deleted (`scale r1 --replicas=0`)  
**T0:** `1790279792.512978653` = **2026-09-24 19:56:32.513**  
**Result:** route flipped at **+62.2 s**, `repaired: n/a` (protocol self-heals)

---

## 1. Mechanism

OSPF has no agent and no LLM. Detection is a protocol timer: when R1 stops
sending hellos, the neighbour goes `Down` after the dead interval, an LSA is
flooded, every router recomputes SPF, and the shortest path to `10.1.8.0/24`
moves from `gre-r1` to the `gre-r3` (Path 0) branch. FRR then installs the new
route in the kernel FIB. Time = grace period + dead interval + SPF.

## 2. Timeline

```
T0 = 19:56:32.513   kubectl scale r1 --replicas=0
  |
  + 0.0s   pod r1 Terminating. 30s terminationGracePeriod starts.
  |        route = * 10.1.2.2 via gre-r1      ping = 0% loss  (still forwarding)
  |
  |        ..... 30 consecutive healthy polls, ~1.27s apart
  |             1790279792.586 -> 1790279821.699   all 0% loss
  |
  +30.4s   1790279822.958  *** FIRST 100% PACKET LOSS ***
  |        route STILL * 10.1.2.2 via gre-r1  <- blackholed, no replacement yet
  |
  |        ..... 16 consecutive failed polls
  |             1790279825.254 -> 1790279852.437  all 100% loss
  |             route STILL * 10.1.2.2 via gre-r1  <- OSPF still advertises dead path
  |
  +62.2s   1790279854.694  *** ROUTE FLIP + PING RECOVER (same sample) ***
  |        route = * 10.1.5.2 via gre-r3   ping = 0% loss
```

## 3. Time budget

| Component | Duration | Notes |
|---|---|---|
| k8s termination grace | **30.4 s** | pod still forwarding until SIGKILL |
| OSPF dead interval -> SPF | **31.8 s** | dead timer + LSA flood + SPF recompute |
| SPF apply to kernel FIB | **~0 s** | same sample as flip |
| **Total T0 -> restored** | **62.2 s** | matches `ospf-metrics.json` |
| **True user-visible outage** | **31.8 s** | from first lost packet to recovery |

> The 62.2 s headline is mostly *waiting to be killed* (30.4 s). The number
> that reflects protocol behaviour is the **31.8 s** dead-timer window.

## 4. Log snippets (verbatim)

### 4.1 Chaos
```
v2-ospf/ospf-chaos.log:
T0=1790279792.512978653 -- BREAKING Path 1 (gray: DROP hellos rc1<->r1, links stay UP)
R1 pod DELETED (router death) at 2026-09-24T19:56:32
ROUTE FLIPPED at 1790279854.693713296
PING RECOVERED at 1790279854.693713296
```

### 4.2 Watch log — last healthy / first loss / recovery
```
v2-ospf/ospf-watch.log (per-second, verbatim):

1790279821.698115156 :: route=[  * 10.1.2.2, via gre-r1, weight 1] ping=[1 packets transmitted, 1 received, 0% packet loss, time 0ms]
1790279822.957574510 :: route=[  * 10.1.2.2, via gre-r1, weight 1] ping=[1 packets transmitted, 0 received, 100% packet loss, time 0ms]
        ... 15 more 100% loss samples, route unchanged ...
1790279852.436509879 :: route=[  * 10.1.2.2, via gre-r1, weight 1] ping=[1 packets transmitted, 0 received, 100% packet loss, time 0ms]
1790279854.693713296 :: route=[  * 10.1.5.2, via gre-r3, weight 1] ping=[1 packets transmitted, 1 received, 0% packet loss, time 0ms]
```

### 4.3 Routing table before / after
```
v2-ospf/ospf-before.txt:
--- rc1 neighbors ---
1.1.1.11          1 Full/-          19m48s            31.151s 10.1.2.2        gre-r1:10.1.2.1                      0     0     0
1.1.1.13          1 Full/-          27m25s            34.782s 10.1.5.2        gre-r3:10.1.5.1                      0     0     0
--- rc1 route to vm2 ---
  Known via "ospf", distance 110, metric 40, best
  * 10.1.2.2, via gre-r1, weight 1

v2-ospf/ospf-after.txt:
  Known via "ospf", distance 110, metric 310, best
  * 10.1.5.2, via gre-r3, weight 1
```

## 5. Technical analysis

**Strengths**
- Zero operational cost and zero external dependency. No API key, no model, no
  inference latency in the repair path.
- Deterministic. The recovery time is a function of configured timers, not of
  traffic load or LLM behaviour.
- Handles *any* failure type the adjacency can observe, not a scripted one.
- The standby branch was already in the RIB (neighbour `1.1.1.13` Full on
  `gre-r3`), so no warm-up cost at failover time.

**Weaknesses exposed by this run**
- **No fast detection override.** For 31.8 s the FIB actively pointed traffic
  into a black hole. A protocol cannot know a node is dead faster than its
  dead interval allows.
- **Detection and repair are the same event.** There is no place for an
  operator/agent to intervene between 'noticed' and 'acted'.
- **Blast radius is protocol-wide.** The dead interval is global: every prefix
  through R1 waits the same timer, whether or not it is affected.
- The 62.2 s figure is dominated by k8s grace, not OSPF. Quote 31.8 s as the
  protocol's real contribution.

## 6. Raw metrics
```json
v2-ospf/ospf-metrics.json:
{
 "t0": 1790279792.5129786,
 "t_route_flip_s": 62.2,
 "t_ping_repair_s": 62.2
}
```
