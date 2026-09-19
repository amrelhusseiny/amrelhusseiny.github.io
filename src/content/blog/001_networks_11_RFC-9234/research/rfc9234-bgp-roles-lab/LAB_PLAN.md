# Lab Plan — Demonstrating RFC 9234 (BGP Roles & OTC) with FRR

**Status:** Topology, configs, and scripts are written and deployable. Scenario runs / evidence capture not yet executed.
**Blog post:** `001_networks_11_RFC-9234` (same folder, draft)
**Source article:** https://blog.cloudflare.com/rfc9234-bgp-role-model/

> **Pivot note (2026-09-03):** originally scoped for SONiC OS. Since RFC 9234 (Roles + OTC) is
> implemented *inside FRR*, and SONiC just runs FRR as its BGP control-plane, we dropped SONiC
> entirely to avoid image-sourcing/build overhead. This lab uses plain `frrouting/frr` Docker
> containers via docker-compose. Same protocol behavior, far less setup friction. SONiC (or real
> hardware) remains a possible stretch goal for a dataplane-level follow-up.

---

## 1. Objective

Demonstrate how **RFC 9234 (BGP Roles)** prevents route leaks using the **Only to Customer (OTC)**
attribute. Prove the two headline capabilities:

1. **Role Mismatch** detection — peers that disagree on their relationship fail the BGP handshake (code 2, subcode 11).
2. **OTC-based route leak suppression** — a leaked route carrying OTC is rejected downstream, with no operator-written policy.

## 2. Technology stack

- **FRR** (`frrouting/frr:latest` Docker image) — RFC 9234 support: **Yes**
- **docker-compose** — topology/link simulation (one dedicated bridge network per point-to-point link); no containerlab, no SONiC
- Runs on the **Deployment server** (`10.122.8.16`, Docker 29.6.1 already installed)

## 3. Topology

See **`TOPOLOGY.md`** for the full diagram and node table. Summary: 4 nodes, mirroring Cloudflare's
hairpin example ASNs (peer1=64502, provider1=64503, customer1=64504) plus provider2=64505 so the
leak has an illegitimate destination:

```
peer1(64502) --peer-- provider1(64503) --provider/customer-- customer1(64504) --customer/provider-- provider2(64505)
```

`customer1` is dual-homed to `provider1` and `provider2` — the hairpin leak candidate.

## 4. Files in this folder

| Path | Purpose |
|---|---|
| `TOPOLOGY.md` | Diagram, node/link tables, test prefix |
| `CONNECT_GUIDE.md` | How to reach each node + all `show` commands needed |
| `RFC_ROLE_PAIRINGS.md` | Every valid/invalid RFC 9234 role pairing, mapped to this lab's sessions |
| `notes/rfc9234-notes.md` | Condensed RFC 9234 technical notes |
| `topology/docker-compose.yml` | The 4-node topology definition |
| `configs/<node>/{daemons,frr.conf}` | Per-node FRR config (roles pre-applied) |
| `scripts/deploy.sh` | `docker compose up -d` wrapper |
| `scripts/destroy.sh` | `docker compose down -v` wrapper |
| `scripts/status.sh` | Quick `show bgp summary` across all nodes |
| `scripts/run_scenarios.sh` | Captures evidence (`show bgp ...` output) per scenario into `evidence/` |
| `evidence/` | Populated when scenarios are actually run (empty for now) |

## 5. Scenarios / experiments

1. **Baseline (no roles / policy leak)** — temporarily strip `local-role` lines from customer1's
   config (or add explicit route re-advertisement) and show the route learned from provider1
   propagates to provider2 — the hairpin leak, uncontrolled.
2. **Enable BGP Roles** — restore/apply the roles as shipped in `configs/*/frr.conf`; show all
   sessions establish cleanly (they use only the 5 valid pairings).
3. **Role Mismatch** — deliberately flip one side's role to an invalid partner (see
   `RFC_ROLE_PAIRINGS.md` §2 for the exact steps); observe the session rejected with Role
   Mismatch (code 2 / subcode 11).
4. **OTC leak suppression** — with roles correctly applied, attempt the same leak as scenario 1;
   show the OTC attribute causes provider2 (or customer1 itself) to refuse/not re-announce it.
5. **Optional: strict mode** — add `local-role <role> strict-mode` on one session and show a
   neighbor that sends no Role capability gets rejected outright.
6. **Optional: Route Server / RS-Client** — extend the topology (see `RFC_ROLE_PAIRINGS.md` §3)
   to demo the RS/RS-Client pairing and OTC propagation through a route server.

## 6. Verification tooling

- `vtysh` — `show bgp summary`, `show bgp ipv4 unicast`, `show bgp ipv4 unicast <prefix>`,
  `show bgp neighbors <ip>`, `show logging` (full command list in `CONNECT_GUIDE.md`)
- `tcpdump` inside a container, exported via `docker cp`, opened in Wireshark to inspect the raw
  OTC path attribute (type code 35) if `vtysh` output isn't granular enough

## 7. Work items (ordered, updated)

1. [x] Decide topology tooling → docker-compose, no containerlab/SONiC
2. [x] Write topology, per-node FRR configs (roles pre-applied), scripts
3. [x] Write connection guide + show-command reference (`CONNECT_GUIDE.md`)
4. [x] Write full RFC 9234 role-pairing cross-reference (`RFC_ROLE_PAIRINGS.md`)
5. [ ] Deploy (`scripts/deploy.sh`) and verify baseline BGP adjacencies come up
6. [ ] Run scenario 1 (baseline leak) and capture evidence
7. [ ] Run scenario 2 (roles enabled) and capture evidence
8. [ ] Run scenario 3 (Role Mismatch) and capture evidence
9. [ ] Run scenario 4 (OTC suppression) and capture evidence
10. [ ] Optional: scenarios 5 (strict mode) and 6 (RS/RS-Client)
11. [ ] Write up results, attach evidence, flip blog post `draft: false`

## 8. Risks / open questions

- FRR's default `bgp ebgp-requires-policy` (RFC 8212) blocks eBGP without an explicit
  import/export policy — mitigated with `no bgp ebgp-requires-policy` in all configs, but worth
  double-checking this doesn't mask the leak-suppression behavior we want to demo.
- `vtysh` may or may not render the OTC attribute directly in `show bgp` detail output depending
  on FRR version — pcap fallback documented in `CONNECT_GUIDE.md`.
- IPv6 not yet covered (OTC applies to both families) — v4-only for the first pass.
- Deployment server runs WSL2 — Docker networking (multiple bridge networks, container-to-
  container routing) should work fine but hasn't been deploy-tested yet as of this revision.

## 9. Deliverables

- Topology diagram (`TOPOLOGY.md`, ASCII) ✅
- Config + docker-compose topology file ✅
- Connection & show-command guide ✅
- RFC role-pairing cross-reference ✅
- Reproducible scenario scripts ✅ (execution pending)
- Evidence pack (captures, logs, screenshots) — pending
- Blog post update with results — pending


---

## 10. RESULTS — First successful run (2026-09-03)

**Status: Scenarios 2 and 4 VERIFIED on a clean `docker compose up -d` with no manual intervention.**

### What was proven

1. **BGP Role capability negotiates correctly.** `show bgp neighbors 10.0.1.2` on `peer1` shows:
   ```
   Local Role: peer
   Remote Role: peer
   Role: advertised and received
   ```
2. **OTC attribute is set automatically per RFC 9234 rules.** The test prefix `198.51.100.0/24`
   (originated by peer1, AS64502) shows `otc 64502` in the BGP table at both `provider1` and
   `customer1` — stamped the moment it crossed from peer1 (Peer role) into provider1 (which then
   treats it as "received from a peer/provider" and lets the existing OTC ride through).
3. **The hairpin leak is blocked automatically — no policy required.** `customer1` (dual-homed to
   provider1 AND provider2) receives the OTC-tagged route from provider1 and `show bgp ipv4
   unicast 198.51.100.0/24` on customer1 shows **"Not advertised to any peer"**. `provider2`
   never receives the prefix at all (`% Network not in table`). This is the exact Cloudflare
   hairpin scenario, reproduced and blocked, with zero manual route-maps or prefix-lists.

### Gotchas hit and fixed (useful for anyone re-running this)

- **Docker `/30` subnets collide with the bridge gateway.** Compose tried to assign `.1` to a
  container while Docker also wanted `.1` for the bridge gateway → "Address already in use".
  Fixed by widening every link to `/29` and shifting host addresses to `.2`/`.3`.
- **`network 198.51.100.0/24` alone is not enough.** FRR's `network` statement under
  `address-family ipv4 unicast` only advertises a prefix if it resolves in the RIB. Without a
  matching route, `show bgp ipv4 unicast <prefix>` showed `invalid, sourced, local` and
  **"no best path" / "Not advertised to any peer"** — nothing was actually being tested. Fixed by
  adding `ip route 198.51.100.0/24 Null0` to peer1's `frr.conf` so the network statement has a
  real route to point at.
- The `% Can't open configuration file /etc/frr/vtysh.conf` warning on every `vtysh -c` call is
  cosmetic (missing optional file) and does not affect functionality — safe to ignore or silence
  with `grep -v vtysh.conf`.

### Evidence captured

- `evidence/02-roles-enabled/` — first successful bring-up (roles negotiated, OTC visible)
- `evidence/04-otc-suppression/` — clean redeploy from committed configs only, proving the leak
  suppression is fully config-driven and reproducible (no manual vtysh patches needed)

### Remaining work items

- [ ] Scenario 1 (baseline / no-roles leak) — temporarily strip `local-role` + add explicit
      re-advertisement policy on customer1 to show the UNPROTECTED leak, for contrast
- [ ] Scenario 3 (Role Mismatch) — flip one side's role per `RFC_ROLE_PAIRINGS.md` §2 and capture
      the NOTIFICATION code 2 / subcode 11
- [ ] Scenario 5 (strict mode)
- [ ] Scenario 6 (optional RS/RS-Client extension)
- [ ] Packet capture (tcpdump) of the OTC attribute on the wire, for the blog post screenshot
- [ ] Write up final results into the blog post, flip `draft: false`
