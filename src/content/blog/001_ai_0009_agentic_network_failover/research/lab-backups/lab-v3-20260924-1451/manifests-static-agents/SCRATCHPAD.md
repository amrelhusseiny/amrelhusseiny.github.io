# Lab scratchpad — v1 (working baseline, 2026-09-24)

Goal: FRR dual-path lab (vm1 ↔ [Path1: rc1-r1-r2-rc2 | Path0: rc1-r3-r4-rc2] ↔ vm2),
static routes, **Path 1 only**, running on the Kubernetes cluster (`ffr-lab` ns).

## Steps taken

1. **Containerlab draft** (`~/frr-dualpath-lab/`)
   - Wrote `frr-dualpath-lab.clab.yml` + FRR configs with OSPF (cost 10 vs 100).
   - No docker/containerlab on this host → converted to static Path-1-only,
     validated offline with a Python FIB simulation (ping both directions OK).

2. **Moved to Kubernetes** — found existing (broken) `ffr-lab` deployment:
   - FRR never started (ConfigMap mounted over `/etc/frr` = read-only),
     stale hardcoded pod IPs, no tunnels → all pings failed.

3. **Rebuilt overlay with GRE tunnels** (Calico is flat, no Multus)
   - `00-services.yaml`: headless `*-svc` for pod-IP discovery via DNS.
   - FRR static configs (`02`): 10.1.1/2/3/4/8.0/24 over Path 1; r3/r4 stubs.
   - Fixed along the way:
     - FRR image is Alpine → `apk`, not `apt`.
     - `ip_forward`: kubelet forbids the sysctl → router pods `privileged: true`.
     - ConfigMap mounted at `/config` + copied (keeps `/etc/frr` writable).
     - VM tunnel `gre0` collided with kernel fallback device → renamed.
     - Pod IPs change on rollout → 30s background self-heal loop refreshes GRE remotes.
   - `r3`/`r4` scaled to 0. Verified: vm1↔vm2 ping 0% loss both ways,
     `show ip route static` correct on all 4 routers, `ospfd` not running.

4. **Jump host (`ssh-server`, tmux `lab`)**
   - Old script used `kubectl` for peer IPs → all panes `ssh root@FAILED`.
   - Rewrote to SSH via stable DNS (`rc1-svc`…) with `sshpass` auto-login;
     windows: `routers` (rc1,r1,r2,rc2) + `clients` (vm1,vm2).
   - Fixed Alpine `PermitRootLogin prohibit-password` blocking VM logins.
   - Fixed `AllowTcpForwarding no` (Alpine default) blocking `-J` tunnels;
     raised `MaxStartups/MaxSessions`.
   - Host keys persisted in `Secret/ssh-host-keys` (verified stable across restarts).
   - Validated: all 6 panes live, all 6 logins OK, ping from tmux pane OK.

5. **Client access** (root/labpass everywhere)
   - `ssh -p 30022 root@<nodeIP>` → jump; `ssh root@<name>-svc` → device.
   - Or `ssh -J root@<nodeIP>:30022 root@<name>-svc`.
   - FRR CLI on routers: `vtysh`.

## Baseline v1 backup

- `~/lab-backups/lab-v1-20260924-0642/` (+ `.tar.gz`)
  - `manifests/` = copy of `~/k8s-dualpath/`
  - `containerlab/` = copy of `~/frr-dualpath-lab/`
  - `cluster-snapshot/ffr-lab-full.yaml` = live `all,cm,svc,deploy,secret`
- Restore: `kubectl apply -f manifests/` (+ recreate `ssh-host-keys` Secret, scale r3/r4 to 0)

## Current live state (verified)

- Pods Running: rc1 r1 r2 rc2 vm1 vm2 ssh-server (r3/r4 = 0/0)
- End-to-end: vm1→vm2 0% loss; FRR statics via Path-1 next-hops only.

## Next (TBD — user to define)

- Ideas: re-enable Path 0 / failover test, OSPF instead of statics,
  per-router NodePorts, persistent volume for FRR logs, Git repo for manifests.

## v2: agentic failover demo (2026-09-24)
- Path 0 pre-deployed idle (r3/r4 + gre meshes, statics pre-installed).
- Agents on jump host (`lab-agents` CM, /agents): jev-monitor.py (1s polls,
  JEV_MODEL decision via OpenRouter) + config-agent.py (Mercury-2.5 render,
  allowlist-validated vtysh apply) + chaos.sh (scripted Path-1 break).
- Demo result: detect 14.1s, LLM render ~4-10s, apply 2.2s, total repair 26.7s,
  verified ping green on Path 0. Cost per run < $0.001.
- Known issues: Mercury needs max_tokens>=4000 (reasoning-heavy); render missed
  rc1 .8.0/.4.0 swaps (recursion via r3 saved the data plane - tighten prompt);
  run single agent instances (stale duplicates muddied run 1-2).
- No Jev/Typesafe model on OpenRouter (checked 458 models) - JEV_MODEL currently
  inception/mercury-2 as stand-in; swap when the real ID/SDK lands.
- Backup: ~/lab-backups/lab-v2-*/ (manifests + article + cluster snapshot).
- Article pack: ~/lab-article/ (before/after, both agent logs, decision, plan, metrics).
