# Connect & Show-Command Guide — RFC 9234 SHOWCASE (12 nodes)

## Prerequisites

```bash
cd research/rfc9234-bgp-roles-lab/scripts
./deploy.sh          # docker compose up -d, waits for daemons
./status.sh          # quick summary of all 12 nodes
```

## Connecting to a node

Each node is a separate container running `frrouting/frr` (container name `rfc9234-<node>`).
Two ways in:

### 1. Straight into vtysh (recommended, fastest)
```bash
docker exec -it rfc9234-peer1       vtysh    # AS64502 peer
docker exec -it rfc9234-provider1   vtysh    # AS64503 peer+provider
docker exec -it rfc9234-customer1   vtysh    # AS64504 customer (dual-homed)
docker exec -it rfc9234-provider2   vtysh    # AS64505 provider
docker exec -it rfc9234-rs1         vtysh    # AS64510 route server
docker exec -it rfc9234-rsclient1   vtysh    # AS64511 rs-client
docker exec -it rfc9234-rsclient2   vtysh    # AS64512 rs-client
docker exec -it rfc9234-m1          vtysh    # AS64701 -> Provider/Peer MISMATCH
docker exec -it rfc9234-m2          vtysh    # AS64702 -> Peer/Provider MISMATCH
docker exec -it rfc9234-m3          vtysh    # AS64703 -> RS/Peer MISMATCH
docker exec -it rfc9234-m4          vtysh    # AS64704 -> Customer/Customer MISMATCH
docker exec -it rfc9234-m5          vtysh    # AS64705 -> no Role (strict-mode reject)
```

### 2. Shell first, then vtysh
```bash
docker exec -it rfc9234-customer1 bash
vtysh
```

### One-shot command (no interactive shell)
```bash
docker exec rfc9234-customer1 vtysh -c "show bgp summary"
```

## Essential show commands (run inside vtysh, or via `vtysh -c "..."`)

| Command | What it tells you |
|---|---|
| `show bgp summary` | Session state per neighbor (Established / Idle / Active), prefix counts |
| `show bgp neighbors <ip>` | Full neighbor detail: **local-role / remote-role**, Role Mismatch evidence |
| `show bgp ipv4 unicast` | Full BGP table as seen by this node |
| `show bgp ipv4 unicast <prefix>` | Detail for a prefix incl. the **OTC attribute** (`otc <asn>`) |
| `show bgp ipv4 unicast <prefix> bestpath` | Just the best path detail |
| `show ip route bgp` | What actually made it into the FIB via zebra |
| `show bgp ipv4 unicast summary` | Condensed AFI/SAFI-specific summary |
| `show run` (in vtysh) | Live running config vs `configs/<node>/frr.conf` |
| `show bgp memory` | Sanity check the daemon is healthy |
| `show logging` | Recent BGP log lines -- watch for NOTIFICATION code 2 / subcode 11 (Role Mismatch) |

## Showcase-specific verification commands

### OTC attribute (set by peer/RS on egress)
```bash
docker exec rfc9234-customer1 vtysh -c "show bgp ipv4 unicast 198.51.100.0/24"  # -> otc 64502
docker exec rfc9234-rsclient1 vtysh -c "show bgp ipv4 unicast 203.0.114.0/24"   # -> otc 64510
docker exec rfc9234-rsclient2 vtysh -c "show bgp ipv4 unicast 203.0.113.0/24"   # -> otc 64510
```

### Role Mismatch (rejected sessions)
```bash
# On any mismatch node, confirm session is Idle + NOTIFICATION sent (OPEN Error / Role Mismatch)
docker exec rfc9234-m1 vtysh -c "show bgp neighbors 10.0.5.2" | grep -iE "Local Role|Remote Role|BGP state|Notification|Last reset"
#   expect: Local Role: peer, Remote Role: undefined, BGP state = Idle,
#           Last reset ... Notification sent (OPEN Message Error/Role Mismatch)

# On the valid node side, same session shows as Idle too:
docker exec rfc9234-provider1 vtysh -c "show bgp neighbors 10.0.5.3" | grep -iE "BGP state|Notification|Last reset"
```

### Strict-mode rejection (m5 vs provider1)
```bash
docker exec rfc9234-provider1 vtysh -c "show bgp neighbors 10.0.9.3" | grep -iE "Local Role|Remote Role|BGP state|Notification"
#   expect: Local Role: provider (strict-mode), Remote Role: undefined (no capability),
#           BGP state = Idle, NOTIFICATION sent
```

## tmux quick layout (topology sections)

Topology A (peer/provider/customer chain + mismatch m1/m2/m4) and Topology B (RS + m3) --
use the pane layout from earlier messages, or simply:

```bash
# one pane per node (12 panes is heavy -- recommended: 2 windows)
tmux new-session -d -s lab -x 240 -y 60
tmux send-keys -t lab:1 "docker exec -it rfc9234-peer1 vtysh" Enter
# ...repeat for the nodes you care about...
tmux attach -t lab
```

## Teardown

```bash
./destroy.sh   # docker compose down -v
```
