# Lab Topology — RFC 9234 SHOWCASE (single combined topology, 12 nodes)

Pure FRR (no SONiC), 12 nodes, docker-compose networking. One topology, both valid and
**rejected** RFC 9234 role-pairing cases live simultaneously — built for a showcase demo.

## Diagram

```
 VALID LINKS (Established)                          REJECTED LINKS (DOWN)
 ─────────────────────────                          ─────────────────────

 [peer1]AS64502                      [m2]AS64702"provider"
     │ peer/peer                        │ (Peer/Provider ✘)
     │ 10.0.1.0/29                      │ 10.0.6.0/29
 [provider1]AS64503 ◄───────────────► [peer1]AS64502
     │  │                              ▲
     │  │ provider/customer            │ 10.0.6.3 -> peer1 peer
     │  │ 10.0.2.0/29                  │
     │  ▼                              │
 [customer1]AS64504               [m2 neighbor on peer1]
     │  │
     │  │ customer/provider            [m1]AS64701"peer"
     │  │ 10.0.3.0/29                    │ (Provider/Peer ✘)
     │  ▼                                │ 10.0.5.0/29
 [provider2]AS64505                 [provider1]AS64503

 [rs1]AS64510 ◄─rs-server/rs-client─► [rsclient1]AS64511   (10.0.4.0/29 IX seg)
     │  │                              [rsclient2]AS64512
     │  │
     │  │ rs-server/peer ✘             [m3]AS64703"peer"
     │  │ 10.0.7.0/29                    │ (RS/Peer ✘) 10.0.7.0/29 -> rs1
     │  ▼                                  │
                                      [rs1]AS64510

 [customer1]AS64504 ◄──customer/customer ✘──► [m4]AS64704"customer" (10.0.8.0/29)
 [provider1]AS64503 ◄──provider strict-mode ✘──► [m5]AS64705"NO ROLE" (10.0.9.0/29)
```

## Node summary

| Node | Container | ASN | Role(s) | Link(s) | State |
|---|---|---|---|---|---|
| peer1 | rfc9234-peer1 | 64502 | peer, peer | 10.0.1 (prov1), 10.0.6 (m2) | peer1↔provider1 Up; m2 session Idle |
| provider1 | rfc9234-provider1 | 64503 | peer, provider, provider, provider+strict | 10.0.1, 10.0.2, 10.0.5 (m1), 10.0.9 (m5) | valid Up; m1 Idle; m5 Idle (strict) |
| customer1 | rfc9234-customer1 | 64504 | customer, customer, customer | 10.0.2, 10.0.3, 10.0.8 (m4) | valid Up; m4 Idle |
| provider2 | rfc9234-provider2 | 64505 | provider | 10.0.3 | Up |
| rs1 | rfc9234-rs1 | 64510 | rs-server, rs-server, rs-server | 10.0.4 (2 clients), 10.0.7 (m3) | valid Up; m3 Idle |
| rsclient1 | rfc9234-rsclient1 | 64511 | rs-client | 10.0.4 | Up |
| rsclient2 | rfc9234-rsclient2 | 64512 | rs-client | 10.0.4 | Up |
| m1 | rfc9234-m1 | 64701 | peer | 10.0.5 | **Idle — Role Mismatch (Provider/Peer)** |
| m2 | rfc9234-m2 | 64702 | provider | 10.0.6 | **Idle — Role Mismatch (Peer/Provider)** |
| m3 | rfc9234-m3 | 64703 | peer | 10.0.7 | **Idle — Role Mismatch (RS/Peer)** |
| m4 | rfc9234-m4 | 64704 | customer | 10.0.8 | **Idle — Role Mismatch (Customer/Customer)** |
| m5 | rfc9234-m5 | 64705 | *(none — no Role capability)* | 10.0.9 | **Idle — strict-mode rejection** |

## Networks (docker bridges)

| Network | Subnet | Members |
|---|---|---|
| net-peer1-provider1 | 10.0.1.0/29 | peer1 (.3), provider1 (.2) |
| net-provider1-customer1 | 10.0.2.0/29 | provider1 (.2), customer1 (.3) |
| net-customer1-provider2 | 10.0.3.0/29 | customer1 (.2), provider2 (.3) |
| net-ix-rs | 10.0.4.0/29 | rs1 (.2), rsclient1 (.3), rsclient2 (.4) |
| net-provider1-m1 | 10.0.5.0/29 | provider1 (.2), m1 (.3) |
| net-peer1-m2 | 10.0.6.0/29 | peer1 (.2), m2 (.3) |
| net-rs1-m3 | 10.0.7.0/29 | rs1 (.2), m3 (.3) |
| net-customer1-m4 | 10.0.8.0/29 | customer1 (.2), m4 (.3) |
| net-provider1-m5 | 10.0.9.0/29 | provider1 (.2), m5 (.3) |

## Test prefixes

| Prefix | Originated by | Purpose |
|---|---|---|
| `198.51.100.0/24` | peer1 (AS64502) | Sector A: hairpin leak / OTC suppression on the valid provider/customer path |
| `203.0.113.0/24` | rsclient1 (AS64511) | Sector B: RS transparent re-announcement |
| `203.0.114.0/24` | rsclient2 (AS64512) | Sector B: RS transparent re-announcement |

All three use `ip route <prefix> Null0` + `network <prefix>` in the originating node config.

## Showcase verification (all verified 2026-09-06)

| Case | Expected | Actual |
|---|---|---|
| peer1↔provider1 (Peer/Peer) | Up | ✅ Established |
| provider1↔customer1 (Provider/Customer) | Up | ✅ Established |
| customer1↔provider2 (Customer/Provider) | Up | ✅ Established |
| rs1↔rsclient1/2 (RS-Server/RS-Client) | Up | ✅ Established + OTC=64510 re-announce |
| m1 (Provider/Peer) | Down — Role Mismatch | ✅ Idle, NOTIFICATION "OPEN Error/Role Mismatch" |
| m2 (Peer/Provider) | Down — Role Mismatch | ✅ Idle |
| m3 (RS/Peer) | Down — Role Mismatch | ✅ Idle |
| m4 (Customer/Customer) | Down — Role Mismatch | ✅ Idle |
| m5 (no role vs strict-mode) | Down — strict reject | ✅ Idle |
| OTC on hairpin path | `otc 64502`, blocked at customer1 | ✅ verified |
