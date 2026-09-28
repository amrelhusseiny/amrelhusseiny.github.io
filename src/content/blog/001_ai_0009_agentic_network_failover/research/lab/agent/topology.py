#!/usr/bin/env python3
"""
topology.py - the single source of truth for the lab.

DEVICES is what the agents can reach. TOPOLOGY_PROMPT is the factual brief
given to Space Bunny: what the devices are, what they do, where the clients
are. It contains no fault hypothesis and no suggested commands.
"""
import re


DEVICES = {
    "rc1": "10.90.0.11",
    "r1": "10.90.0.12",
    "r2": "10.90.0.13",
    "rc2": "10.90.0.14",
    "r3": "10.90.0.15",
    "r4": "10.90.0.16",
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
over SSH as root, and two tools are available to you:

  ssh(node, command)    run a shell command on a device
  vtysh(node, command)  run an FRR command (show ... or configuration)

Topology:

  rc1  10.90.0.11   client edge router.  The client network 10.90.1.1/32 sits behind it.
  r1   10.90.0.12   transit router, PRIMARY path
  r2   10.90.0.13   transit router, PRIMARY path
  rc2  10.90.0.14   server edge router. The server network 10.90.8.1/32 sits behind it.
  r3   10.90.0.15   transit router, STANDBY path
  r4   10.90.0.16   transit router, STANDBY path

  primary path :  rc1 -> r1 -> r2 -> rc2
  standby path :  rc1 -> r3 -> r4 -> rc2

Traffic must keep flowing between the client network 10.90.1.1/32 and the
server network 10.90.8.1/32. Routing between the routers is by static /32
routes, currently pointed along the primary path only.

Investigate with the tools, work out what is wrong, and apply whatever
configuration changes are required to restore traffic. You are expected to act.
"""
