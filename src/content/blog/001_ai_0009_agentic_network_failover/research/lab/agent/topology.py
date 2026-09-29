#!/usr/bin/env python3
'''
topology.py - the single source of truth for the lab.

Four-segment topology, identical in the agent lab and the OSPF lab. The only
difference between the two labs is the routing mechanism, never the physical
layout, so a comparison between them means something.

rc1 and rc2 share only the standby segment, so the primary path is a genuine
four-hop chain through r1 and r2 rather than a direct adjacency.
'''
import os
import re


def _env(name, default):
    """os.environ.get returns the empty string when a variable is exported by
    the host but unset there, which would silently produce an empty next hop
    and therefore a route that FRR accepts and that blackholes traffic."""
    return (os.environ.get(name) or "").strip() or default


DEVICES = {
    "rc1": _env("RC1_IP", "10.90.10.11"),
    "r1":  _env("R1_IP",  "10.90.10.12"),
    "r2":  _env("R2_IP",  "10.90.11.14"),
    "rc2": _env("RC2_IP", "10.90.12.16"),
    "r3":  _env("R3_IP",  "10.90.20.12"),
    "r4":  _env("R4_IP",  "10.90.20.13"),
}

FRR_LOG = "/var/log/frr/frr.log"

# Noise filter. FRR 10.3 emits these once at boot while reporting VRF runtime
# state. They are not faults, so they are withheld from the decision maker.
# The raw log is still written to the trail in full.
NOISE_PATTERNS = [
    re.compile(p, re.I)
    for p in [
        r"libyang\s+Invalid\b.*\/frr-vrf:lib\/vrf\/state",
    ]
]


def is_noise(line):
    for p in NOISE_PATTERNS:
        if p.search(line):
            return True
    return False




# ---- the two paths, and the second decision -------------------------------
#
# Derived from the captured running-config of rc1 and rc2, not from the diagram,
# because the next hop on the return path is not the same address as the hop on
# the forward path: rc2 reaches r2 on r2 PC-side address 10.90.12.15, not on
# r2 PB-side 10.90.11.14. Getting this wrong would produce a route that FRR
# accepts and that blackholes traffic.
#
#   rc1  ip route 10.90.8.1/32 10.90.10.12          <- PATH-A forward
#   rc1  ip route 10.90.8.1/32 10.90.20.12 200      <- PATH-B forward
#   rc2  ip route 10.90.1.1/32 10.90.12.15          <- PATH-A return
#   rc2  ip route 10.90.1.1/32 10.90.20.12 200      <- PATH-B return

# r3 and r4 are the standby transit pair. Both sit on the shared standby
# segment ST together with rc1 and rc2, so PATH-B is short.

LINK = {
    "rc1": {"pa": "10.90.10.11", "st": "10.90.20.11"},
    "r1":  {"pa": "10.90.10.12", "pb": "10.90.11.13"},
    "r2":  {"pb": "10.90.11.14", "pc": "10.90.12.15"},
    "rc2": {"pc": "10.90.12.16", "st": "10.90.20.14"},
    "r3":  {"st": "10.90.20.12"},
    "r4":  {"st": "10.90.20.13"},
}

CLIENT_NET = "10.90.1.1"      # loopback behind rc1, the source of the probes
SERVER_NET = "10.90.8.1"      # loopback behind rc2, the destination

PATHS = {
    "PATH-A": {
        "label": "PRIMARY, through r1 and r2",
        "diagram": "rc1 --pa--> r1 --pb--> r2 --pc--> rc2",
        "hops": ["rc1", "r1", "r2", "rc2"],
        "fwd_next_hop": _env("R1_IP", "10.90.10.12"),
        "rev_next_hop": LINK["r2"]["pc"],
        "distance": 1,
    },
    "PATH-B": {
        "label": "STANDBY, through r3 on the shared standby segment",
        "diagram": "rc1 --st--> r3 --st--> rc2   (r4 also sits on st)",
        "hops": ["rc1", "r3", "rc2"],
        "fwd_next_hop": _env("R3_IP", "10.90.20.12"),
        "rev_next_hop": _env("R3_IP", "10.90.20.12"),
        "distance": 200,
    },
}

PATH_DIAGRAM = """
  Two paths join the client edge rc1 to the server edge rc2. They share no
  intermediate router.

     PATH-A   PRIMARY                     PATH-B   STANDBY

     rc1 ──pa──► r1                       rc1 ──st──► r3
           ──pb──► r2                            ──st──┐
                ──pc──► rc2  ◄──st───────────────────┘

     fwd next hop on rc1:  %s        fwd next hop on rc1:  %s
     rev next hop on rc2:  %s        rev next hop on rc2:  %s
""" % (PATHS["PATH-A"]["fwd_next_hop"], PATHS["PATH-B"]["fwd_next_hop"],
       PATHS["PATH-A"]["rev_next_hop"], PATHS["PATH-B"]["rev_next_hop"])


# The exact FRR lines that make each path the active one, generated from PATHS
# so they cannot drift away from the numbers the decision maker is shown.
PATH_ACTIONS = """
  to carry traffic over PATH-A (primary, through r1 and r2):
    rc1   ip route %(Aser)s/32 %(Afwd)s
    rc2   ip route %(Acli)s/32 %(Arev)s

  to carry traffic over PATH-B (standby, through r3):
    rc1   ip route %(Bser)s/32 %(Bfwd)s 200
    rc2   ip route %(Bcli)s/32 %(Brev)s 200

  to withdraw a path instead, remove its route:
    rc1   no ip route %(Aser)s/32 %(Afwd)s
    rc2   no ip route %(Acli)s/32 %(Arev)s
""" % {
    "Aser": SERVER_NET, "Acli": CLIENT_NET,
    "Bser": SERVER_NET, "Bcli": CLIENT_NET,
    "Afwd": PATHS["PATH-A"]["fwd_next_hop"],
    "Arev": PATHS["PATH-A"]["rev_next_hop"],
    "Bfwd": PATHS["PATH-B"]["fwd_next_hop"],
    "Brev": PATHS["PATH-B"]["rev_next_hop"],
}


def path_state(node, observed, target):
    """Which paths this router currently has a route for, to a specific target.

    The target prefix must be filtered on. Matching on the next hop alone is
    wrong: on rc1 the next hop 10.90.20.12 also serves 10.90.3.1 at distance 1,
    so a next-hop-only scan reports the standby path as the primary one. That is
    exactly the kind of bug that makes an agent confidently choose the path that
    is about to fail.
    """
    import re as _re
    out = []
    for pid, p in PATHS.items():
        hop = p["fwd_next_hop"] if node == "rc1" else p["rev_next_hop"]
        best = None
        for line in (observed or "").splitlines():
            if hop not in line or target not in line:
                continue
            m = _re.search(r"\[(\d+)/(\d+)\]", line)
            # FRR prints [distance/metric]. Group 1 is the administrative
            # distance, which is what decides which route wins. Group 2 is the
            # metric and is always 0 for a static.
            dist = int(m.group(1)) if m else 999
            if best is None or dist < best:
                best = dist
        out.append({"path": pid, "next_hop": hop,
                    "distance": best,
                    "installed": best is not None})
    live = [x["distance"] for x in out if x["installed"]] or [999]
    for x in out:
        x["active"] = x["installed"] and x["distance"] == min(live)
    return out

TOPOLOGY_PROMPT = """
You are a network engineer responsible for keeping a dual-path network up.

Every device below is an FRR router. You have shell access to all of them
over SSH as root, through one tool:

  run(node, command)   run a shell command or an FRR command on a device

Devices:

  rc1  10.90.10.11   client edge.  Client network 10.90.1.1/32 sits behind it.
  r1   10.90.10.12   transit, primary path
  r2   10.90.11.14   transit, primary path
  rc2  10.90.12.16   server edge.  Server network 10.90.8.1/32 sits behind it.
  r3   10.90.20.12   transit, standby path
  r4   10.90.20.13   transit, spare on the standby

The routers sit on four separate segments:

  10.90.10.0/24  PA : rc1 - r1
  10.90.11.0/24  PB : r1 - r2
  10.90.12.0/24  PC : r2 - rc2
  10.90.20.0/24  ST : rc1 - r3, rc2, r4

Routing is static and bidirectional. Each path is one static route on rc1 and
one on rc2, and the lower administrative distance is the one that carries
traffic. All of these routes are already configured, so moving traffic onto the
other path is a matter of distance, not of building anything new.

""" + PATH_ACTIONS + """
---

How to be fast, because round trips are what cost you time here, not thought:

* If several commands do not depend on each other, issue them in the same turn.
  Reading all six routing tables is six independent commands, not six turns.

* The topology, the segments and the exact next hops are all above. Do not spend
  turns rediscovering them. The one thing that changes at runtime is which route
  is currently active, and that is a single "show ip route" away.

* Which path should carry traffic has already been decided for you. Your job is
  how to make it so, safely, and to confirm that it worked.

---

Things about this environment that are fixed, so you do not have to discover
them by trial and error:

* ping IS available on every device and is the fastest way to check that a next
  hop really answers. Use it.

* The run tool decides for itself whether a command is a shell command or an
  FRR command, and it puts configuration lines into the right mode for you. Never
  open vtysh or vtysh -c yourself.

* A route whose next hop is not on one of that device own directly connected
  subnets will NOT work. Linux resolves it recursively through the default route
  and the traffic silently vanishes. Every next hop listed above is already on
  the correct segment for the device it goes on.

* Interface names are not consistent between devices and are not eth0/eth1 in any
  fixed order. Never assume. Check with "ip -br addr" if you need to know.

* A configuration line that is rejected returns a non-zero exit and FRR does not
  say why. That is a syntax error, not a network fault. Correct the command and
  try again. Do not change strategy because of it.

* After you change anything, read it back with "show ip route" and confirm the
  intended path is now the active one on both rc1 and rc2. A change that was
  accepted is not the same as a change that took effect.

"""
