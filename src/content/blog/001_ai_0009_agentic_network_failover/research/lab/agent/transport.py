#!/usr/bin/env python3
"""
transport.py - SSH access to the lab routers from inside the agent container.

Everything that touches a router goes through here, so the decision trail
captures every command with its return code, stdout and stderr.
"""
import re
import shlex
import subprocess
import time

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
    "-i", "/root/.ssh/agent_ed25519",
]

READONLY = re.compile(r"^\s*(show|do|ping|traceroute|terminal)\b", re.I)


def ssh(node_ip, remote_cmd, timeout=25):
    """Run one command on a router over SSH. Returns (rc, stdout, stderr, secs)."""
    t0 = time.time()
    argv = ["ssh"] + SSH_OPTS + ["root@%s" % node_ip, remote_cmd]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "TIMEOUT after %ss" % timeout
    except Exception as e:
        rc, out, err = 125, "", "EXC %s" % e
    return rc, out, err, round(time.time() - t0, 3)


def vtysh(node_ip, frr_cmd, timeout=25):
    """Run a vtysh command on a router. This is the only configuration path.

    FRR 10 refuses a configuration line through a bare "vtysh -c" and answers
    rc=1 with no message, so anything that is not read-only is wrapped in
    config mode.
    """
    if READONLY.match(frr_cmd):
        return ssh(node_ip, "vtysh -c %s" % shlex.quote(frr_cmd),
                   timeout=timeout)
    return ssh(node_ip, "vtysh -c %s -c %s -c %s"
               % (shlex.quote("conf t"), shlex.quote(frr_cmd),
                  shlex.quote("end")), timeout=timeout)


def read_log(node_ip, lines=20, timeout=20):
    """Read the tail of the FRR log from a router."""
    rc, out, err, dt = ssh(node_ip, "tail -n %d /var/log/frr/frr.log" % lines,
                           timeout=timeout)
    return out if rc == 0 else "(log read failed rc=%d: %s)" % (rc, err.strip())


def show(node_ip, frr_cmd, timeout=20):
    """Run a read-only vtysh show command and return its text."""
    rc, out, err, dt = vtysh(node_ip, frr_cmd, timeout=timeout)
    return out if rc == 0 else "(show failed rc=%d: %s)" % (rc, err.strip())
