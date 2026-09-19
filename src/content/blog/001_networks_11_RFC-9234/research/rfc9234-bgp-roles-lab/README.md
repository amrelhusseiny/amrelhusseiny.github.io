# rfc9234-bgp-roles-lab — RFC 9234 SHOWCASE Lab

**Topic:** RFC 9234 — BGP Roles and the Only-to-Customer (OTC) route-leak prevention mechanism.

**Stack:** Pure FRR (`frrouting/frr` Docker image) + docker-compose. No SONiC, no containerlab.

**Scope:** A single combined topology (12 nodes) that demonstrates **all 5 valid RFC 9234 role
pairings** (Established) **and every rejected case** (Role Mismatch, code 2 subcode 11, plus the
strict-mode rejection) at the same time — built for a live showcase.

## What lives here

| Path | Purpose |
|---|---|
| `LAB_PLAN.md` | Plan + full verified results |
| `TOPOLOGY.md` | Combined 12-node diagram, node/link tables, showcase verification table |
| `CONNECT_GUIDE.md` | How to connect to each node + all show commands |
| `RFC_ROLE_PAIRINGS.md` | Every valid/invalid RFC 9234 role pairing mapped to this lab |
| `notes/rfc9234-notes.md` | Condensed technical notes on RFC 9234 |
| `topology/docker-compose.yml` | 12-node combined topology definition |
| `configs/<node>/` | Per-node FRR configs (valid + mismatch + strict) |
| `scripts/` | deploy / destroy / status / scenario-evidence scripts |
| `evidence/` | Captured `show bgp` outputs (valid runs + `all-cases` showcase run) |

## Quick start

```bash
cd scripts
./deploy.sh        # docker compose up -d
./status.sh        # show bgp summary for all 12 nodes
docker exec -it rfc9234-customer1 vtysh
```

## The 12 nodes at a glance

**Valid (Established):** peer1(64502), provider1(64503), customer1(64504), provider2(64505),
rs1(64510), rsclient1(64511), rsclient2(64512)

**Rejected (Role Mismatch / strict):** m1(64701) Prov/Peer ✘, m2(64702) Peer/Prov ✘,
m3(64703) RS/Peer ✘, m4(64704) Cust/Cust ✘, m5(64705) no-role vs strict ✘

See `CONNECT_GUIDE.md` for the full command reference and `LAB_PLAN.md` for the scenario list.

## Why this lab

The Cloudflare research ([BGP Role model: tracking the adoption of RFC 9234](https://blog.cloudflare.com/rfc9234-bgp-role-model/)) shows route leaks are a real, frequent problem and that RFC 9234 moves leak prevention into the protocol itself. FRR (which SONiC also runs under the hood) supports RFC 9234 — a single lab that shows both the acceptance (valid pairings) and rejection (Role Mismatch / strict-mode) behavior hands-on, useful as a teaching/showcase tool.

## Related

- Blog post (draft): `../001_networks_11_RFC-9234.md`
- [RFC 9234](https://datatracker.ietf.org/doc/html/rfc9234)
- [RFC 7908 — Route Leak classification](https://datatracker.ietf.org/doc/html/rfc7908)
- [RFC 7606 — BGP error handling](https://datatracker.ietf.org/doc/html/rfc7606)
- [FRR BGP Roles and Only to Customers docs](https://docs.frrouting.org/en/latest/bgp.html#bgp-roles-and-only-to-customers)
