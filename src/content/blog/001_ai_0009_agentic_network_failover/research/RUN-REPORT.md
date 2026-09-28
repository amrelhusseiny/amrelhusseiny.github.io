# RUN REPORT - agentic failover, run 20260927T201248Z

Written for the article author. Every number here is taken from the run bundle in
[evidence-runs/fault-run/](evidence-runs/fault-run/), not from memory.

---

## The shape of it

```
  capture  -> read all 6 routers over SSH, one item per NEW log line
  judge    -> TypeSafe Jev, one API call per line, categorical normal/failed
  route    -> any "failed" => dispatch, otherwise stop
  bunny    -> Space Bunny, ReAct agent, ssh + vtysh tools, free to act
  re-check -> capture and judge again
```

There are no thresholds, no debounce and no waiting. One `failed` verdict
triggers failover immediately.

---

## Run 1 - healthy baseline

```
capture[before]: 0 item(s) to judge
JEV[before] verdict: faulty=none
CONCLUSION : healthy_no_action
elapsed       : 3.04s
```

Zero API calls in 3 seconds. A per-router log cursor means only *new* lines are
judged, so a quiet network costs nothing. Correct behaviour, and the reason the
fault run costs exactly one Jev call.

---

## Run 2 - fault injected

`docker stop agt-r1`, killing the primary-path transit router. The agent was
started detached (`docker exec -d`) because an SSH timeout otherwise kills the run
before the bundle is written.

### The decision

Exactly one line to judge:

```
r1   failed  conf=1     r1 10.90.0.12 did not respond to SSH: ssh: connect to host ...
```

`faulty_before = ['r1']`. One API call, ~11s, confidence 1.0. A router that will
not answer SSH is submitted as a line like any other and judged the same way, so
a dead router is still a model decision rather than a hardcoded branch.

### What Space Bunny did

```
68 messages:  1 human, 24 assistant, 43 tool results
43 tool calls: 28 x ssh, 15 x vtysh
wall clock:    324s
guard refusals: 0
```

It did not take the verdict at face value. Before changing anything it established
that r1 was genuinely hard-down rather than merely refusing SSH or flapping:

- `ip neigh` on rc1 showed `FAILED` for 10.90.0.12, so r1 was not answering ARP
- a port scan of the whole 10.90.0.0/24 found .1 .11 .13 .14 .15 .16 and
  **nothing at .12**
- r1's loopback 10.90.2.1 was unreachable too, so the whole node was gone, not
  just sshd or frr

Having established that, it disagreed with the framing of the problem. The verdict
was right, but the actual fault was a design flaw on rc1:

```
ip route 10.90.8.1/32 10.90.0.12    <- primary only
ip route 10.90.2.2/32 10.90.0.12
ip route 10.90.3.2/32 10.90.0.12
```

So the single failure of r1 blackholed the entire client-to-server path.

### What it changed

Nine configuration writes, all on rc1, all `rc=0`:

```
no ip route 10.90.8.1/32 10.90.0.12      drop the dead primary
no ip route 10.90.2.2/32 10.90.0.12
no ip route 10.90.3.2/32 10.90.0.12
ip  route 10.90.8.1/32 10.90.0.15      point at r3 instead
ip  route 10.90.2.2/32 10.90.0.15
ip  route 10.90.3.2/32 10.90.0.15
ip  route 10.90.8.1/32 10.90.0.12 200  re-add primary at distance 200, as fallback
ip  route 10.90.2.2/32 10.90.0.12 200
ip  route 10.90.3.2/32 10.90.0.12 200
```

That last group is the part worth dwelling on. It did not simply delete the dead
path. It demoted it to distance 200 - installed but not preferred - so that if r1
ever comes back, traffic returns to the primary path on its own without anyone
having to undo anything.

### Outcome

Verified from outside the agent:

```
rc1 -> 10.90.8.1   REACHABLE      (before the fix: No route to host)
rc2 -> 10.90.1.1   REACHABLE
```

r1 stayed down. The agent rerouted around it; it did not and could not revive it.
That is the honest ceiling of a configuration agent.

---

## The finding: the monitor flags its own repair as a new fault

The run concluded `still_faulty`, and `faulty_after` was not just `['r1']`:

```
faulty before : ['r1']
faulty after  : ['r1', 'rc1']
```

rc1 was judged failed at **confidence 1.0**, on this line:

```
2026/09/27 20:16:17 MGMTD: [WEJ55-ZGM1W] Locking for DS 2 failed,
                            Err: 'Lock already taken on DS by another session!'
```

That line did not exist before the agent started working. Bunny issued several
vtysh writes in quick succession, one lost FRR's config-lock race, FRR logged the
contention, and the monitor read its own repair as a fresh fault - at maximum
confidence, with no hesitation.

The agent repaired the network and the instrumentation immediately reported the
repair as a new problem. Any naive "alert on log change" monitor has this failure
mode, and it gets worse the more autonomous the agent is, because the agent is
what generates the log traffic.

---

## Findings

**F1 - self-inflicted false positive.** See above. The post-fix verdict is wrong
about rc1, and wrong with maximum confidence.

**F2 - the same line can get opposite verdicts.** On a fully healthy lab,
`MGMTD: XXX txn in progress, retry init` came back `normal` on rc1 (confidence
0.02) and `failed` on r2 (confidence 0.06). Same text, same model, opposite
answers, both effectively coin-flips.

**F3 - low confidence is a usable signal that the code ignores.** Every F2
verdict carried a confidence under 0.11. A single `failed` at confidence 1.0 is
trustworthy; a single `failed` at 0.06 is not. The design deliberately has no
threshold, which is right for a dead router and wrong for ambiguous chatter.

**F4 - noise filtering is a blunt instrument, and the obvious version is unsafe.**
Only `libyang Invalid ... /frr-vrf:.../state` boot lines were filtered. A broader
filter on the word "invalid" was explicitly rejected, because the lab's very first
genuine fault was an FRR config rejection containing that word:
`invalid address 127.0.0.1/8`. Filtering on the token would have hidden exactly
the class of failure the lab exists to catch.

**F5 - the cursor hides F2 in steady state.** Because only new lines are judged,
the boot-chatter false positives fire once after a restart and never again. The
clean baseline in run 1 is clean only because those lines were already consumed.
Any write-up must disclose that the first cycle after a restart is not
representative of steady state.

**F6 - autonomous means slow.** 324 seconds and 43 tool calls to restore one path,
and several turns spent rediscovering that the routers have no `ping` binary and
that `show interfaces` is not a valid command in this FRR build. All correct
behaviour, none of it fast. `space-bunny-free` is a reasoning model and each turn
costs 20-40s.
