# lab/ - building and running the failover lab

Target: the Deployment_Server (WSL2 Ubuntu, Docker). Everything runs in
containers; the agents SSH to the routers.

---

## Topology

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

All 13 static routes live in `frr/*.conf` and are loaded at boot. The baseline is
**primary-only**: rc1 has no route toward r3, so restoring traffic is a real
configuration change rather than a no-op.

---

## One-time setup

```bash
cd research/lab

# SSH keypair: routers trust the public key, the agent holds the private one
ssh-keygen -t ed25519 -N '' -C lab-agent -f keys/agent_ed25519
cp keys/agent_ed25519.pub docker/router/agent_ed25519.pub
cp keys/agent_ed25519      docker/agent/agent_ed25519

# API key for Jev and Space Bunny
printf 'OPENCODE_API_KEY=<your key>\n' > .env
chmod 600 .env

# corporate TLS-inspecting CA, so the agent image trusts the same chain
mkdir -p docker/agent/ca
cp /usr/local/share/ca-certificates/clean_proxy_1.crt docker/agent/ca/forcepoint-1.crt
cp /usr/local/share/ca-certificates/clean_proxy_2.crt docker/agent/ca/forcepoint-2.crt
```

---

## Build and start

```bash
docker build -t lab-router:latest docker/router
docker build -t lab-agent:latest  docker/agent

docker compose -f docker-compose.agent.yml up -d
sleep 20
```

Expect 7 containers: `agt-rc1 r1 r2 rc2 r3 r4` plus `agt-agent`.

---

## Run the agents

```bash
# one cycle: capture -> Jev -> (Space Bunny) -> re-verify
docker exec agt-agent python3 -u /agent/monitor.py --out /agent/out

# re-judge every log line from scratch instead of only new ones
docker exec agt-agent python3 -u /agent/monitor.py --out /agent/out --reset-cursors
```

Long runs must be started detached or an SSH timeout will kill them mid-flight
and the bundle never finalises:

```bash
docker exec -d agt-agent sh -c 'cd /agent && python3 -u monitor.py --out /agent/out > /agent/run.log 2>&1'
```

### Injecting the fault

```bash
docker stop agt-r1        # primary path transit router
# then run the agent as above
```

Afterwards `rc1 -> 10.90.8.1` should be reachable again. Check it from outside
the agent, since the agent is not a reliable narrator of its own success:

```bash
docker exec agt-rc1 python3 -c "import socket; s=socket.create_connection(('10.90.8.1',22),4); print('REACHABLE'); s.close()"
```

There is no `ping` in the router image and FRR's `ping` is not compiled into this
build, hence the TCP connect to sshd as an L3 reachability probe.

---

## Reset between runs

```bash
# authoritative baseline: frr.conf wins over any runtime change an agent made
docker compose -f docker-compose.agent.yml up -d --force-recreate rc1 r1 r2 rc2 r3 r4

# drop accumulated log cursors so every line is judged again
docker exec agt-agent sh -c 'rm -f /agent/out/cursors.json'
```

Do **not** try to undo an agent change route by route. The agents also reroute
loopback prefixes, and a partial undo leaves the edge router with no route to the
server network. Recreate from `frr.conf` instead.

---

## Tear down

```bash
docker compose -f docker-compose.agent.yml down -v --remove-orphans
docker rmi lab-router:latest lab-agent:latest
```

---

## The graph

```
START -> capture -> judge -> (healthy -> END)
                          (faulty  -> bunny -> capture_after
                                     -> judge_after -> END)
```

| module | role |
|---|---|
| `topology.py` | devices, log-noise filter, and Space Bunny's system prompt |
| `models.py` | `JevChatModel` (a real `BaseChatModel`) and `build_bunny_model()` |
| `tools.py` | the two LangChain tools, `ssh` and `vtysh` |
| `graph.py` | the `StateGraph` and its nodes |
| `monitor.py` | entrypoint |
| `transport.py` | the only path to a router |
| `trail.py` | writes the decision trail |
