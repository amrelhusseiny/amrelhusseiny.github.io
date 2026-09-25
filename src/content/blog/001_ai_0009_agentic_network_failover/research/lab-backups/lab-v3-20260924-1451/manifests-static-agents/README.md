# FRR dual-path lab on Kubernetes (`ffr-lab` namespace)

Static routes, **Path 1 only**: `vm1 → rc1 → r1 → r2 → rc2 → vm2`.
Path 0 (`r3`/`r4`) is scaled to 0. No OSPF anywhere.

## How it maps

Calico is flat (no Multus), so each point-to-point link is a **GRE tunnel**
carrying the `10.1.0.0/16` overlay:

| Link | Subnet | Endpoints |
|---|---|---|
| vm1–rc1 | 10.1.1.0/24 | vm1 `.1` ↔ rc1 `.254` |
| rc1–r1 | 10.1.2.0/24 | rc1 `.1` ↔ r1 `.2` |
| r1–r2 | 10.1.3.0/24 | r1 `.1` ↔ r2 `.2` |
| r2–rc2 | 10.1.4.0/24 | r2 `.1` ↔ rc2 `.254` |
| rc2–vm2 | 10.1.8.0/24 | rc2 `.254` ↔ vm2 `.1` |

## Files

| File | Purpose |
|---|---|
| `00-services.yaml` | Headless `*-svc` services → peer pod-IP discovery via DNS |
| `01-router-script-cm.yaml` | Router boot: GRE tunnels, FRR install/start, 30s self-heal loop |
| `02-frr-configs.yaml` | FRR static configs (Path 1); minimal stubs for r3/r4 |
| `03-vm-script-cm.yaml` | Client boot: GRE + `10.1.0.0/16` route + sshd |
| `04-ssh-server-cm.yaml` | Jump-host boot: tmux `lab` session, auto-login panes |
| `05-ssh-server-deploy.yaml` | Jump-host Deployment (mounts `ssh-host-keys` Secret) |
| `10-routers.yaml` | `rc1 r1 r2 rc2` Deployments (`privileged` for `ip_forward`) |
| `20-clients.yaml` | `vm1 vm2` Deployments |

Not in git (cluster state / secrets):
- `Secret/ssh-host-keys` — jump-host SSH host keys. Recreate with:
  `for t in ed25519 rsa ecdsa; do ssh-keygen -t $t -N '' -f ssh_host_${t}_key; done`
  `kubectl create secret generic ssh-host-keys -n ffr-lab --from-file=ssh_host_ed25519_key ...`
- `deploy/r3 deploy/r4` (legacy) scaled to 0: `kubectl scale deploy r3 r4 -n ffr-lab --replicas=0`

## Deploy / verify

```bash
kubectl apply -f k8s-dualpath/
kubectl get pods -n ffr-lab -o wide
VM1=$(kubectl get pod -n ffr-lab -l name=vm1 -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ffr-lab $VM1 -- ping -c3 10.1.8.1
kubectl exec -n ffr-lab -l name=rc1 -n ffr-lab -- vtysh -c 'show ip route static'
```

## Access

- Jump: `ssh -p 30022 root@<nodeIP>` (root/labpass), then `tmux attach -t lab`
- Direct: `ssh -J root@<nodeIP>:30022 root@<rc1|r1|r2|rc2|vm1|vm2>-svc`
- FRR CLI on routers: `vtysh`

## Tweaking

- Static routes → edit `02-frr-configs.yaml`, then `kubectl rollout restart deploy/<node> -n ffr-lab`
- Tunnels/peers → `TUN` env in `10-routers.yaml` (`greName:peerSvc` pairs)
- Tunnels self-heal (30s loop), so restarts converge without ordering
