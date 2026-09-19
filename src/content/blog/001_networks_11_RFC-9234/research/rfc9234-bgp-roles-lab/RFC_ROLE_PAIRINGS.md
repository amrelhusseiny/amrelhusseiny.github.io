# RFC 9234 — All Role Pairing Cases, Mapped to the SHOWCASE Lab (12 nodes)

RFC 9234 defines 5 roles: **Provider, Customer, Peer, RS (Route Server), RS-Client**. Only 5
pairings are valid; every other combination triggers **Role Mismatch** (NOTIFICATION code 2,
subcode 11) and the eBGP session is refused. This lab has ALL valid pairings **up** and 5
rejected sessions **down**, simultaneously.

## 1. Valid pairings (session ESTABLISHED) — all live here

| # | Local Role | Remote Role | In this lab | Evidence |
|---|---|---|---|---|
| 1 | Provider | Customer | provider1 <-> customer1; provider2 <-> customer1 | Established, OTC flows |
| 2 | Customer | Provider | customer1 <-> provider1; customer1 <-> provider2 | Established |
| 3 | Peer | Peer | peer1 <-> provider1 | Established |
| 4 | RS-Server | RS-Client | rs1 <-> rsclient1; rs1 <-> rsclient2 | Established, OTC=64510 |
| 5 | RS-Client | RS-Server | rsclient1 <-> rs1; rsclient2 <-> rs1 | Established |

## 2. Invalid pairings (session REJECTED — Role Mismatch)

Total = 5x5 - 5 valid = **20 invalid combinations**, collapsing into the mismatch categories
below. The lab ships one live example per representative category (all verified Idle +
NOTIFICATION "OPEN Message Error / Role Mismatch"):

| Node | Local Role | Peer | Remote Role | Pairing (invalid) | State |
|---|---|---|---|---|---|
| m1 (AS64701) | peer | provider1 | provider | Provider/Peer ✘ | **Idle** |
| m2 (AS64702) | provider | peer1 | peer | Peer/Provider ✘ | **Idle** |
| m3 (AS64703) | peer | rs1 | rs-server | RS/Peer ✘ | **Idle** |
| m4 (AS64704) | customer | customer1 | customer | Customer/Customer ✘ | **Idle** |
| m5 (AS64705) | *(none)* | provider1 | provider (strict-mode) | no Role vs strict-mode ✘ | **Idle** |

## 3. Strict-mode case

`provider1` runs `neighbor 10.0.9.3 local-role provider strict-mode` toward m5. m5 sends **no
Role capability at all**. In strict mode, a missing Role capability is treated as a Role
Mismatch → session rejected. (In non-strict mode, a one-sided Role would still come up — see
RFC 9234 partial-deployment behavior.)

## 4. Full invalid-pairing table (for reference)

| Local | Remote (invalid partners shown) |
|---|---|
| Provider | Provider, Peer, RS, RS-Client |
| Customer | Customer, Peer, RS, RS-Client |
| Peer | Provider, Customer, RS, RS-Client |
| RS | Provider, Customer, Peer, RS |
| RS-Client | Provider, Customer, Peer, RS-Client |

Every row above = Role Mismatch (code 2 / subcode 11). To demo any of them live, clone one of
the m1–m4 nodes and set the local-role to the corresponding invalid value.

## 5. OTC behavior per role (quick recap)

| Local role on this session | On announce (egress) | On receive (ingress) |
|---|---|---|
| Provider | Never forward OTC-carrying route upward (n/a upstream) | Stamp OTC = peer ASN if absent |
| Customer | If sending down to customer w/o OTC, stamp OTC = own ASN | If from provider w/o OTC, stamp OTC = provider ASN |
| Peer | If to peer w/o OTC, stamp OTC = own ASN | If from peer w/o OTC, stamp OTC = peer ASN; reject if OTC w/ different ASN |
| RS-Client | Like customer/peer for OTC on announce | — |
| RS | Like provider/peer on receive; re-announces w/ OTC = own ASN | — |

See `notes/rfc9234-notes.md` for the exact RFC 9234 set/check rules.
