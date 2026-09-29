#!/usr/bin/env python3
"""
seed-cursors.py - mark every currently-present log line as already judged.

The agent judges only NEW log lines each cycle, which is the design and also
what keeps the API call count at one or two per run instead of thirty-four.
Seeding once up front means a run only judges what the fault actually produced.
"""
import json
import os
import sys

sys.path.insert(0, "/agent")

import transport
from topology import DEVICES, FRR_LOG, is_noise

cursors = {}
for node, ip in DEVICES.items():
    rc, out, err, dt = transport.ssh(ip, "cat " + FRR_LOG, timeout=20)
    if rc != 0:
        print("  %-4s unreachable, cursor stays 0" % node)
        continue
    kept = [l for l in out.splitlines() if l.strip() and not is_noise(l)]
    cursors[node] = len(kept)
    print("  %-4s seeded at %d line(s)" % (node, len(kept)))

os.makedirs("/agent/out", exist_ok=True)
with open("/agent/out/cursors.json", "w") as fh:
    json.dump(cursors, fh, indent=2)
print("  wrote /agent/out/cursors.json")
