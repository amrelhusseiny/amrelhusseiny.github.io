#!/usr/bin/env python3
'''
tools.py - the single tool Space Bunny is given.

A previous version exposed two tools, ssh() and vtysh(). That doubled the
decision surface for no benefit and cost real time: the agent picked vtysh, got
rc=1, and went looking for a different way to run the same thing. One tool that
accepts either a shell command or an FRR command removes that whole class of
wasted turns, and it decides config-vs-show itself.

The destructive-command guard is a rail against wrecking the lab, not a hint
about what is wrong: it does not steer the diagnosis.
'''
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

# FRR 10 refuses a configuration line through a bare "vtysh -c" and answers rc=1
# with no message, so anything not read-only is wrapped in config mode by
# transport.vtysh().


def _unknown(node):
    return ("ERROR: unknown device %r. Known devices: %s"
            % (node, ", ".join(DEVICES)))




RUN_DOC = """Run one command on a lab router over SSH.

You do not need to know whether a command is a shell command or an FRR
command. Pass either one and this tool routes it correctly.

Shell examples:
  cat /var/log/frr/frr.log
  ip -br addr
  ip route get 10.90.8.1
  ps -eo comm=

FRR read-only examples:
  show ip route
  show ip ospf neighbor

FRR configuration examples:
  ip route 10.90.8.1/32 10.90.20.12
  ip route 10.90.8.1/32 10.90.20.12 200
  no ip route 10.90.8.1/32 10.90.10.12

Configuration changes take effect immediately and stay in the running
configuration.

Args:
  node: device name, one of: rc1, r1, r2, rc2, r3, r4.
  command: the shell or FRR command to run.
"""


@tool
def run(node: str, command: str) -> str:
    """Run one command on a lab router over SSH.

    You do not need to know whether a command is a shell command or an FRR
    command. Pass either one and this tool routes it correctly.

    Shell examples:
      cat /var/log/frr/frr.log
      ip -br addr
      ip route get 10.90.8.1
      ps -eo comm=

    FRR read-only examples:
      show ip route
      show ip ospf neighbor

    FRR configuration examples:
      ip route 10.90.8.1/32 10.90.20.12
      ip route 10.90.8.1/32 10.90.20.12 200
      no ip route 10.90.8.1/32 10.90.10.12

    Configuration changes take effect immediately and stay in the running
    configuration.

    Args:
      node: device name, one of: rc1, r1, r2, rc2, r3, r4.
      command: the shell or FRR command to run.
    """
    if node not in DEVICES:
        return _unknown(node)

    ip = DEVICES[node]
    t = trail_mod.get_trail()
    is_shell = bool(SHELL_FIRST.match(command))
    is_ro = is_shell

    if not is_ro:
        for pat in DENY:
            if re.search(pat, command, re.I):
                if t:
                    t.append_apply({"tool": "run", "node": node,
                                    "command": command, "refused": pat})
                    t.log("   [run]    %-4s REFUSED %s" % (node, command[:40]))
                return ("REFUSED: %r matches destructive-command guard %r. "
                        "Nothing was run." % (command, pat))

    if is_shell:
        rc, out, err, dt = transport.ssh(ip, command)
    else:
        rc, out, err, dt = transport.vtysh(ip, command)

    if t:
        t.append_apply({"tool": "run", "node": node, "ip": ip,
                        "mode": "readonly" if is_ro else "config",
                        "command": command, "rc": rc, "stdout": out,
                        "stderr": err, "elapsed_s": dt})
        t.log("   [run]    %-4s %-44s rc=%s" % (node, command[:44], rc))

    body = ("exit=%d  elapsed=%.2fs\n--- stdout ---\n%s\n--- stderr ---\n%s"
            % (rc, dt, (out or "").strip() or "(empty)",
               (err or "").strip() or "(empty)"))
    if rc != 0 and not is_ro:
        body += ("\n\nNOTE: a non-zero exit on a configuration line usually "
                 "means the\nsyntax was rejected. Check the exact form of the "
                 "route you asked for.")
    return body


TOOLS = [run]

# Anything whose first word is a real shell utility runs as a shell command;
# everything else is treated as an FRR command. Without this the merged tool
# would wrap "ip -br addr" in config mode and get rc=1.
SHELL_FIRST = re.compile(
    r"^\s*(ip\s+route\s+get|ip\s+neigh|ip\s+link|ip\s+-?\w*\s+addr|"
    r"ip\s+a\b|cat|ps|ls|grep|tail|head|echo|awk|sed|python3|which|env|"
    r"uptime|hostname|ss|netstat|find|wc|sort|date|docker|sh\b|bash\b|"
    r"tr\b|cut\b|paste\b|test\b|expr\b|ping\b|traceroute\b)",
    re.I)
