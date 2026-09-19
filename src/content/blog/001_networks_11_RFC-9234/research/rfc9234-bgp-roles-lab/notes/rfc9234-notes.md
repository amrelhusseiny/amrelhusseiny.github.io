# RFC 9234 — Condensed Notes

## Relationship types that govern BGP routing

- Customer–Provider: customer pays for transit.
- Peer–Peer: settlement-free traffic exchange.

Routing must be **valley-free**: a route learned from a provider or peer may only be announced downward to customers, never back up to a provider or peer.

## Route leaks

- Defined in RFC 7908: "propagation of routing announcements beyond their intended scope".
- Classic shape: **hairpin turn** — a customer announces a route between two of its providers.
- Before RFC 9234, prevention relied on hand-written prefix filters + IRR policies (error-prone, per-session).

## BGP Role capability (RFC 9234)

Declares where the local AS sits on an **eBGP** session. Five roles:

| Role | Meaning |
|---|---|
| Provider | Provides transit to customers |
| Customer | Buys transit from providers |
| Peer | Settlement-free lateral peering |
| RS (Route Server) | IX route server |
| RS-Client | Client of a route server |

### Valid role pairings (only these 5)

| Local | Remote |
|---|---|
| Provider | Customer |
| Customer | Provider |
| RS | RS-Client |
| RS-Client | RS |
| Peer | Peer |

- Any other pair → **Role Mismatch** → session rejected with NOTIFICATION code 2, subcode 11.
- Single-sided role: session still comes up (partial deployment); local role still does partial leak prevention.
- **Strict mode** (opt-in): session rejected if neighbor sends no Role capability.
- Roles + ASPA should be configured together where supported.
- Complex/multi-relationship sessions must NOT set a Role — split into separate sessions instead.

## OTC — Only to Customer attribute

- Optional transitive path attribute, type code **35**, value = one ASN.
- Marks the **peak** of the path — after it is set, the route may only travel downward (to customers).
- Must be preserved unchanged. Optional-transitive → even non-RFC-9234 routers pass it through.

### Setting OTC (stamp the first time a route stops going strictly upward)

- Announcing to a customer / peer / RS-client with no OTC present → attach OTC = your own ASN.
- Receiving from a provider / peer / RS with no OTC present → attach OTC = the remote peer's ASN.

### Checking OTC (once present, route may only go down)

- Never announce an OTC route to a provider, peer, or RS.
- OTC route arriving from a customer or RS-client → leak → reject.
- OTC route from a peer whose OTC value != that peer's own ASN → leak → reject.

### Hairpin example (why it works)

AS64502 → peer AS64503 (sets OTC=64502) → customer AS64504 → leaks to provider. Stopped by: (a) compliant AS64504 won't send OTC route to a provider, or (b) the receiving provider rejects an OTC route from a customer. Either alone suffices.

## Cloudflare adoption findings (Aug 2026)

- 67 ASes set OTC on routes to Cloudflare (from PeeringDB network types, 3-month BMP data).
- Route Servers adopt fastest (YYCiX first) — critical since RSes re-announce huge route volumes.
- ~36 ASes potentially RFC 9234-compliant in public RIB data (RouteViews/RIPE RIS).
- **Two Tier-1s stripped OTC:** GTT (AS3257, consistently) and Arelion (AS1299, inconsistently — 71.4% IPv4 / 40.7% IPv6 of paths); Arelion fixed after outreach.
- 33.1% IPv4 / 17% IPv6 of AS_PATHs had OTC stripped; the two Tier-1s appeared in 96.6% (v4) / 92.9% (v6) of those.
- Context: pre-RFC 7606, malformed transitive attributes caused remote session resets → operators started dropping unknown attributes; RFC 7606 (treat-as-withdraw) fixed the risk, so stripping is no longer needed — but legacy configs persist.

## Vendor support matrix (from article)

| Impl | Support |
|---|---|
| Cisco IOS XR | Coming 26.4.1 |
| Junos / Junos Evolved | Yes |
| Arista EOS | No |
| Nokia SR OS | No |
| Huawei | No |
| Extreme SLX-OS | No |
| RouterOS | Yes |
| BIRD | Yes |
| OpenBGPD | Yes |
| **FRR** | **Yes** (→ SONiC) |
| ArcOS | No |
| GoBGP | No |
| ExaBGP | No |

## Lab-relevant implications

- SONiC == FRR underneath → RFC 9234 support available.
- Applying Roles requires a session reset (maintenance window), same in lab.
- Watch for OTC stripping by intermediate nodes — in a lab, keep the fabric RFC 9234-aware or verify with pcap.

