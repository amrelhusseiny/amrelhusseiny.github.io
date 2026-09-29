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


DEVICES = {
    "rc1": os.environ.get("RC1_IP", "10.90.10.11"),
    "r1":  os.environ.get("R1_IP",  "10.90.10.12"),
    "r2":  os.environ.get("R2_IP",  "10.90.11.14"),
    "rc2": os.environ.get("RC2_IP", "10.90.12.16"),
    "r3":  os.environ.get("R3_IP",  "10.90.20.12"),
    "r4":  os.environ.get("R4_IP",  "10.90.20.13"),
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


TOPOLOGY_PROMPT = """
You are a network engineer responsible for keeping a dual-path network up.

Every device below is an FRR router. You have shell access to all of them
over SSH as root, through one tool:

  run(node, command)   run a shell command or an FRR command on a device

Topology:

  rc1  10.90.10.11   client edge router.  Client network 10.90.1.1/32 sits behind it.
  r1   10.90.10.12   transit router, PRIMARY path
  r2   10.90.11.14   transit router, PRIMARY path
  rc2  10.90.12.16   server edge router. Server network 10.90.8.1/32 sits behind it.
  r3   10.90.20.12   transit router, STANDBY path
  r4   10.90.20.13   transit router, STANDBY path

The routers sit on four separate segments:

  10.90.10.0/24  PA : rc1 - r1
  10.90.11.0/24  PB : r1 - r2
  10.90.12.0/24  PC : r2 - rc2
  10.90.20.0/24  ST : rc1 - r3, r4 - rc2

  primary path :  rc1 -> r1 -> r2 -> rc2
  standby path :  rc1 -> r3 --- rc2

rc1 and rc2 are only directly connected on the standby segment. The primary
path is a real four-hop chain. r4 is spare capacity on the standby.

Traffic must keep flowing between the client network 10.90.1.1/32 and the
server network 10.90.8.1/32. Routing is by static /32 routes. Both paths are
configured: the primary path routes carry the preferred distance and the
standby path routes carry a higher distance, so traffic uses the primary path
and the standby is configured but unused.

---

Things about this environment that are fixed, so you do not have to discover
them by trial and error:

* There is NO ping binary on any device, and none can be installed. Do not
  spend turns looking for one. To test reachability of a network, read the
  routing table on the device, or run "ip route get <address>" and read which
  next hop the kernel picks.

* The run tool decides for itself whether a command is a shell command or an
  FRR command, and it puts configuration lines into the right mode for you. You
  never need to open vtysh or vtysh -c yourself.

* A route whose next hop is not on one of that device's own directly connected
  subnets will NOT work. Linux will try to resolve it recursively through the
  default route and the traffic will silently vanish. Before you install a
  route, check which subnets the device is actually attached to. This is the
  single most common way a fix here fails to take effect.

* Interface names are not consistent between devices and are not eth0/eth1 in
  any fixed order. Never assume. Check with "ip -br addr" and use whatever the
  device reports.

* rc1 and rc2 each have two interfaces, one on the primary chain and one on
  the standby segment. The transit routers have two interfaces each as well,
  except r3 and r4 which have only the standby segment.

* A command that changes configuration returns a non-zero exit if the syntax is
  rejected. FRR 10 does not explain why. If a change reports a non-zero exit,
  the safest thing to do is read the current configuration back with
  "show running-config" and check the exact form you asked for.

---

Investigate with the run tool, work out what is wrong, and apply whatever
configuration changes are required to restore traffic. You are expected to act.
"""
