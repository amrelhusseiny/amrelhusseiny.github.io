# research/ - agentic dual-path failover lab

Everything here belongs to **one run**: the Docker Compose + LangGraph failover
experiment. Material from the earlier Containerlab and Kubernetes attempts has
been removed as superseded.

---

## What the run was

Six FRR routers on one flat bridge carry traffic between a client network and a
server network over two paths. The primary path is killed and two agents are
left to deal with it:

- **TypeSafe Jev** decides. Reads each router log line individually and says
  which router is faulty.
- **Space Bunny** acts. A ReAct agent with live `ssh` and `vtysh` tools. It
  investigates freely and applies its own configuration changes.

Both run inside a container on a LangGraph state graph. Nothing is templated and
there are no fallbacks: if a model returns empty or unparseable output the run
aborts rather than guessing.

---

## Headline result

```
healthy baseline : 0 log lines to judge -> healthy_no_action, 3.04s, 0 API calls

fault (r1 killed):
  jev r1  failed conf=1  r1 10.90.0.12 did not respond to SSH
  -> Space Bunny ran 68 messages, proved r1 hard-down,
     installed an alternate path on rc1
  -> rc1 -> 10.90.8.1  REACHABLE   (was: No route to host)
```

The interesting part is not that it worked. It is what the monitor did next -
see [RUN-REPORT.md](RUN-REPORT.md).

---

## Layout

| path | what it is |
|---|---|
| [RUN-REPORT.md](RUN-REPORT.md) | results and findings, written for the article |
| [lab/](lab/) | the runnable lab: images, compose, FRR configs, agent code |
| [lab/README.md](lab/README.md) | how to build and run it |
| [lab/SCRATCHPAD.md](lab/SCRATCHPAD.md) | working notes: decisions, traps, dead ends |
| [evidence-runs/](evidence-runs/) | raw decision trail and evidence from the fault run |

### Inside `evidence-runs/`

```
fault-run/
  timeline.txt              every step, wall-clock stamped, in order
  events.ndjson             structured event log
  trail/
    01-jev-judgements-before.json   one verdict per log line
    02-bunny-request.json           exactly what Bunny was told
    03-bunny-transcript.json        all 68 messages, tool calls included
    06-apply.ndjson                 every command Bunny ran, with rc/stdout/stderr
    07-metrics.json
    08-jev-judgements-after.json    the post-fix re-read
  evidence/<node>/          raw frr logs and routing tables, before and after
```

---

## Status

- Lab torn down. No containers, images or networks left behind.
- The OSPF comparison lab was **not** built in this run, so the two scenarios
  are not yet directly comparable.
