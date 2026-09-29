#!/usr/bin/env python3
"""
recorder.py - the external observer for a failover comparison.

Nothing here trusts the agents to report their own success. Reachability is
measured by ICMP from inside the edge routers against a shared wall-clock time
base, and the OSPF adjacency is captured at 1s so we can see WHY it reconverged.

Per repetition it writes into the run directory:
  ping.csv       ts,lab,direction,seq,result,rtt_ms   <- the downtime measurement
  telemetry.log  timestamped route tables, OSPF state, interface state
  T0             the exact instant the fault was injected
  events.log     phase markers
"""
import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LABS = {
    "agent": {"pfx": "agt", "fwd": "10.90.8.1", "rev": "10.90.1.1",
              "fwd_node": "rc1", "rev_node": "rc2",
              "fwd_src": "10.90.1.1", "rev_src": "10.90.8.1"},
    "ospf":  {"pfx": "ospf", "fwd": "10.91.8.1", "rev": "10.91.1.1",
              "fwd_node": "rc1", "rev_node": "rc2",
              "fwd_src": "10.91.1.1", "rev_src": "10.91.8.1"},
}

NODES = ["rc1", "r1", "r2", "rc2", "r3", "r4"]
PING_INTERVAL = 0.2
PING_TIMEOUT = 1800


def sh(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout)
        return p.stdout.strip()
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except Exception as e:
        return "(error %s)" % e


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Recorder:
    def __init__(self, run_dir):
        self.dir = Path(run_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.telemetry = (self.dir / "telemetry.log").open("a")
        self.events = (self.dir / "events.log").open("a")
        self.t0 = None

    def event(self, text):
        line = "%s %s" % (now_iso(), text)
        self.events.write(line + "\n")
        self.events.flush()
        print(line, flush=True)

    def mark_t0(self):
        self.t0 = time.time()
        (self.dir / "T0").write_text(json.dumps({
            "iso": now_iso(),
            "epoch": self.t0,
        }, indent=2))
        self.event("T0 fault injected")
        return self.t0

    def block(self, title, text):
        self.telemetry.write("===== %s %s =====\n%s\n" % (now_iso(), title, text))
        self.telemetry.flush()

    def close(self):
        self.telemetry.close()
        self.events.close()


    # ---- continuous ICMP -------------------------------------------------
    def start_pings(self):
        """Source each probe from the edge loopback, not the interface address.
        Traffic really originates on the client/server network, and the edge
        routers have no route back to the transit subnets otherwise."""
        for lab, c in LABS.items():
            for direction, node, target, src in (
                    ("fwd", c["fwd_node"], c["fwd"], c["fwd_src"]),
                    ("rev", c["rev_node"], c["rev"], c["rev_src"])):
                out = "/tmp/pg_%s_%s.log" % (lab, direction)
                cmd = ("timeout %d ping -i %s -D -W 1 -I %s %s > %s 2>&1"
                       % (PING_TIMEOUT, PING_INTERVAL, src, target, out))
                sh("docker exec -d %s-%s sh -c %s"
                   % (c["pfx"], node, json.dumps(cmd)))
        self.event("ping streams started: interval %ss, source = edge loopback"
                   % PING_INTERVAL)


    def stop_pings(self):
        for lab, c in LABS.items():
            for node in (c["fwd_node"], c["rev_node"]):
                sh("docker exec %s-%s pkill -f ping || true" % (c["pfx"], node))
        self.event("ping streams stopped")

    def collect_pings(self):
        """Parse the raw ping -D logs into one CSV. A probe counts as OK only if
        the target itself replied; a redirect or unreachable is a failure."""
        out_csv = self.dir / "ping.csv"
        rows = 0
        with out_csv.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ts", "lab", "direction", "seq", "result", "rtt_ms"])
            for lab, c in LABS.items():
                for direction in ("fwd", "rev"):
                    cont = "%s-%s" % (c["pfx"], c["fwd_node"] if direction == "fwd"
                                      else c["rev_node"])
                    raw = sh("docker exec %s cat /tmp/pg_%s_%s.log"
                             % (cont, lab, direction))
                    rows += self._parse_ping(w, lab, direction, c, raw)
        self.event("ping.csv written (%d probes)" % rows)
        return out_csv

    def _parse_ping(self, w, lab, direction, c, raw):
        target = c["fwd"] if direction == "fwd" else c["rev"]
        seen = {}
        order = []
        ts_re = re.compile(r"^\[(\d+\.\d+)\]\s+(.*)$")
        reply_re = re.compile(r"bytes from %s: icmp_seq=\d+ ttl=\d+ time=([\d.]+)"
                             % re.escape(target))
        for line in raw.splitlines():
            m = ts_re.match(line.strip())
            if not m:
                continue
            epoch, rest = float(m.group(1)), m.group(2)
            sq = re.search(r"icmp_seq=(\d+)", rest)
            if not sq:
                continue
            seq = int(sq.group(1))
            if seq not in seen:
                seen[seq] = {"epoch": epoch, "ok": False, "rtt": ""}
                order.append(seq)
            reply = reply_re.search(rest)
            if reply:
                seen[seq]["ok"] = True
                seen[seq]["rtt"] = reply.group(1)
        for seq in order:
            e = seen[seq]
            iso = datetime.fromtimestamp(e["epoch"], timezone.utc).isoformat(
                                       timespec="milliseconds")
            w.writerow([iso, lab, direction, seq,
                        "OK" if e["ok"] else "FAIL", e["rtt"]])
        return len(order)

    # ---- telemetry -------------------------------------------------------
    def vt(self, cont, arg):
        return sh("docker exec %s vtysh -c %s" % (cont, json.dumps(arg)))

    def snapshot(self):
        for lab, c in LABS.items():
            for n in NODES:
                cont = "%s-%s" % (c["pfx"], n)
                self.block("%s %s ip-route" % (lab, cont),
                           self.vt(cont, "show ip route"))
                self.block("%s %s addrs" % (lab, cont),
                           sh("docker exec %s ip -br addr" % cont))
                if lab == "ospf":
                    self.block("%s %s ospf-neighbor" % (lab, cont),
                               self.vt(cont, "show ip ospf neighbor"))
                    self.block("%s %s ospf-lsdb" % (lab, cont),
                               self.vt(cont, "show ip ospf database summary"))
                self.block("%s %s frr-log" % (lab, cont),
                           sh("docker exec %s tail -n 12 /var/log/frr/frr.log" % cont))


    # ---- analysis --------------------------------------------------------
    def analyze(self):
        """Downtime runs from T0, the instant the fault was injected, to the first
        successful probe after the outage. Measured per lab and per direction,
        never self-reported."""
        t0 = self.t0 or json.loads((self.dir / "T0").read_text())["epoch"]
        rows = list(csv.DictReader((self.dir / "ping.csv").open()))
        out = {}
        for lab in LABS:
            for direction in ("fwd", "rev"):
                key = "%s_%s" % (lab, direction)
                series = [r for r in rows
                          if r["lab"] == lab and r["direction"] == direction]
                if not series:
                    out[key] = {"outage": False, "note": "no probes"}
                    continue
                post = [r for r in series if r["result"] == "FAIL"
                        and _epoch(r["ts"]) >= t0 - 1.0]
                if not post:
                    out[key] = {"outage": False,
                                "note": "no failed probe at or after T0"}
                    continue
                first_fail = _epoch(post[0]["ts"])
                recovery = None
                for r in series:
                    if r["result"] == "OK" and _epoch(r["ts"]) > first_fail:
                        recovery = _epoch(r["ts"])
                        break
                end = recovery if recovery else 1e18
                in_window = [r for r in series
                             if first_fail <= _epoch(r["ts"]) <= end]
                out[key] = {
                    "outage": True,
                    "first_fail_offset_s": round(first_fail - t0, 3),
                    "recovery_offset_s": (round(recovery - t0, 3)
                                          if recovery else None),
                    "downtime_s": (round(recovery - t0, 3)
                                   if recovery else None),
                    "failed_probes": len([r for r in in_window
                                          if r["result"] == "FAIL"]),
                    "total_probes_in_window": len(in_window),
                    "recovered": recovery is not None,
                }
        (self.dir / "downtime.json").write_text(json.dumps(
            {"t0_epoch": t0, "results": out}, indent=2))
        self.event("analysis written to downtime.json")
        return out



def _epoch(iso):
    return datetime.fromisoformat(iso).timestamp()


if __name__ == "__main__":
    print("recorder.py is a library; use run-comparison.py")
