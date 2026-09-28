#!/usr/bin/env python3
"""
tools.py - the two tools Space Bunny is given.

ssh    read anything: logs, process state, connectivity tests.
vtysh  inspect and change the FRR configuration. Changes apply immediately.

The vtysh tool carries a deny list. That is a guard rail to stop the agent
destroying the lab, not a hint about what is wrong: it does not steer the
diagnosis, it only refuses a handful of destructive verbs.
"""
import re

from langchain_core.tools import tool

import trail as trail_mod
import transport
from topology import DEVICES

DENY = [
    r"\breboot\b",
    r"write\s+erase",
    r"\bdelete\b",
    r"\bformat\b",
    r"\bkill\b",
    r"\bshutdown\b",
    r"\breload\b",
]


def _fmt(rc, out, err, dt):
    return ("exit=%d  elapsed=%.2fs\n--- stdout ---\n%s\n--- stderr ---\n%s"
            % (rc, dt, (out or "").strip() or "(empty)",
               (err or "").strip() or "(empty)"))


def _unknown(node):
    return ("ERROR: unknown device %r. Known devices: %s"
            % (node, ", ".join(DEVICES)))


@tool
def ssh(node: str, command: str) -> str:
    """Run a shell command on one of the lab routers over SSH.

    Use this to read evidence: the FRR log at /var/log/frr/frr.log, running
    processes, interface state, or to test whether a peer answers.

    Args:
        node: device name, one of rc1 r1 r2 rc2 r3 r4.
        command: the shell command to run on that device.
    """
    if node not in DEVICES:
        return _unknown(node)
    ip = DEVICES[node]
    rc, out, err, dt = transport.ssh(ip, command)
    t = trail_mod.get_trail()
    if t:
        t.append_apply({"tool": "ssh", "node": node, "ip": ip,
                        "command": command, "rc": rc, "stdout": out,
                        "stderr": err, "elapsed_s": dt})
        t.log("   [ssh]    %-4s %-42s rc=%s" % (node, command[:42], rc))
    return _fmt(rc, out, err, dt)


@tool
def vtysh(node: str, command: str) -> str:
    """Run an FRR command on one of the lab routers through vtysh.

    Use a "show ..." command to inspect the routing table, interfaces or
    daemons. Use a bare configuration line (for example
    "ip route 10.90.8.1/32 10.90.0.15") to add or change a route. Changes
    take effect immediately in the running configuration.

    Args:
        node: device name, one of rc1 r1 r2 rc2 r3 r4.
        command: the vtysh command, without the leading "vtysh -c".
    """
    if node not in DEVICES:
        return _unknown(node)
    t = trail_mod.get_trail()
    for pat in DENY:
        if re.search(pat, command, re.I):
            if t:
                t.append_apply({"tool": "vtysh", "node": node,
                                "command": command, "refused": pat})
                t.log("   [vtysh]  %-4s REFUSED %s" % (node, command[:38]))
            return ("REFUSED: %r matches destructive-command guard %r. "
                    "Nothing was run." % (command, pat))
    ip = DEVICES[node]
    rc, out, err, dt = transport.vtysh(ip, command)
    if t:
        t.append_apply({"tool": "vtysh", "node": node, "ip": ip,
                        "command": command, "rc": rc, "stdout": out,
                        "stderr": err, "elapsed_s": dt})
        t.log("   [vtysh]  %-4s %-42s rc=%s" % (node, command[:42], rc))
    return _fmt(rc, out, err, dt)


TOOLS = [ssh, vtysh]
