#!/usr/bin/env python3
"""Serve the lab topology as JSON with LIVE values.

Grafana's Node Graph panel cannot be built from Prometheus time series. It needs
a nodes frame with an id field and an edges frame with source and target. A metric
such as device_up_up{device="r1"} has none of those, so the panel renders nothing
even when the query returns six series.

So the frame shape is built here, from the same probe scripts the metrics come
from, and Grafana reads it over the Infinity datasource.

Design note, learned the hard way: building the payload on request does not
work. Each build SSHes into six routers and the probe scripts are not instant,
so two panels refreshing every five seconds serialise behind each other on a
single-threaded server and both time out. Instead a background thread polls
every few seconds and the HTTP handler only ever serves cached bytes, which
makes a request cost about a millisecond.

Coordinates are fixed on purpose: a topology that rearranges itself during an
incident is harder to read than one where you already know where things are.

Listening:
  127.0.0.1:8888   for curl from the host and the SSH tunnel
  <bridge>:8888    for the Grafana container on the monitoring network
Never 0.0.0.0, which would publish the lab on the corporate LAN. Started by
topology-server.sh.
"""
import json
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))

# How often to re-probe the lab. Fast enough to feel live, slow enough not to
# spend its whole life in SSH.
POLL_SECONDS = float(os.environ.get("TOPO_POLL", "4"))

# The monitoring bridge address, so Grafana in a container can reach this.
# Set by topology-server.sh from the docker network gateway.
BRIDGE = os.environ.get("TOPO_BRIDGE", "")

# name -> (x, y, role). Identical in both labs; only the addressing differs.
NODES = {
    "rc1": (0, 0, "client edge"),
    "r1":  (1, 0, "transit PRIMARY"),
    "r2":  (1, 1, "transit PRIMARY"),
    "rc2": (0, 1, "server edge"),
    "r3":  (2, 0, "transit STANDBY"),
    "r4":  (2, 1, "transit STANDBY"),
}

# rc1 - r1 - r2 - rc2 is PATH-A (primary). rc1 - r3 - r4 - rc2 is PATH-B.
PATH_A = ["rc1", "r1", "r2", "rc2"]
PATH_B = ["rc1", "r3", "r4", "rc2"]

EDGES = [("rc1", "r1"), ("r1", "r2"), ("r2", "rc2"),
         ("rc1", "r3"), ("r3", "r4"), ("r4", "rc2")]

SERVER_NET = {"agt": "10.90.8.1", "ospf": "10.91.8.1"}

# r1 and r3 are the two possible primary next hops. They are told apart by the
# first three octets of the address rc1 points at, which is the only thing that
# differs between them in the route table.
HOP_PREFIX = {"r1": ("10.90.10", "10.91.10"),
              "r3": ("10.90.20", "10.91.20")}

# lab -> serialised bytes. Written only by the poller, read by request threads.
CACHE = {}
CACHE_LOCK = threading.Lock()


def run(script, *args):
    try:
        return subprocess.run(["bash", os.path.join(HERE, script), *args],
                              capture_output=True, text=True,
                              timeout=30).stdout
    except Exception:
        return ""


def parse_influx(text):
    """Parse line protocol into a LIST of (measurement, tags, fields).

    One line is one record. Keying by measurement name instead collapses every
    line that shares a measurement, which is what silently reduced the six
    per-device device_up lines to a single r4 record and made every node read
    DOWN while the path state beside it was correct.
    """
    recs = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            head, rest = line.split(" ", 1)
            name, tags = head.split(",", 1)
            tagd = dict(kv.split("=", 1) for kv in tags.split(",") if "=" in kv)
            fields = {}
            for kv in rest.split(","):
                if "=" not in kv:
                    continue
                k, v = kv.split("=", 1)
                # influx line protocol marks integers with a trailing i
                if v and v[-1] in "if":
                    v = v[:-1]
                fields[k] = v
            recs.append((name, tagd, fields))
        except Exception:
            pass
    return recs


def build(lab):
    recs = parse_influx(run("probe-device.sh", lab))
    recs += parse_influx(run("probe-path.sh", lab, SERVER_NET[lab]))

    up = {}
    for name, tags, fields in recs:
        if name == "device_up":
            up[tags.get("device", "?")] = fields.get("up", "0")

    # path_state is emitted once per lab, so the first matching record is it.
    ps = next((r for r in recs if r[0] == "path_state"), ("path_state", {}, {}))
    ptags, pfields = ps[1], ps[2]
    next_hop = ptags.get("next_hop", "none")
    reachable = pfields.get("reachable", "0")

    # Which nodes carry traffic right now: a reachable next hop on PATH-A means
    # PATH-A is in use, anything else on PATH-B, and an unreachable hop means
    # nothing is flowing.
    if reachable == "1":
        hop = None
        for n, prefixes in HOP_PREFIX.items():
            if next_hop.startswith(prefixes):
                hop = n
                break
        live = PATH_A if hop == "r1" else PATH_B
    else:
        live = []

    nodes = []
    for n, (x, y, role) in NODES.items():
        alive = up.get(n) == "1"
        nodes.append({
            "id": n,
            "title": n,
            "subTitle": role,
            "mainStat": "UP" if alive else "DOWN",
            "arc__status": "ok" if alive else "critical",
            "arc__value": "1" if alive else "0",
            "x": x,
            "y": y,
        })

    edges = []
    for a, b in EDGES:
        hot = a in live and b in live
        edges.append({
            "id": a + "--" + b,
            "source": a,
            "target": b,
            "mainStat": "carrying" if hot else "idle",
        })

    return {
        "lab": lab,
        "next_hop": next_hop,
        "reachable": reachable,
        "distance": pfields.get("distance", "?"),
        "hop_down": pfields.get("hop_down", "0"),
        "nodes": nodes,
        "edges": edges,
    }


def poller():
    """Re-probe both labs on a timer and cache the serialised result."""
    while True:
        for lab in SERVER_NET:
            try:
                body = json.dumps(build(lab)).encode()
                with CACHE_LOCK:
                    CACHE[lab] = body
            except Exception as e:
                print("poll %s failed: %s" % (lab, e), flush=True)
        time.sleep(POLL_SECONDS)


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        lab = self.path.lstrip("/").split("/")[0]
        if lab not in SERVER_NET:
            self.send_error(404)
            return
        with CACHE_LOCK:
            cached = CACHE.get(lab)
            if cached is None:
                # The first poll has not finished yet. Say so rather
                # than serve junk, and do not index the dict: a bare
                # CACHE[lab] during warm-up raises KeyError and turns
                # into a 500.
                body = None
            else:
                doc = json.loads(cached)
                seg = self.path.strip(chr(47)).split(chr(47))
                part = seg[1] if len(seg) > 1 else ""
                # /agt/nodes and /agt/edges return a BARE ARRAY on purpose.
                # Pointing the Infinity plugin root_selector at an array
                # nested inside an object returned zero rows under every
                # json_options combination, so the arrays have own paths.
                if part == "nodes":
                    body = json.dumps(doc["nodes"]).encode()
                elif part == "edges":
                    body = json.dumps(doc["edges"]).encode()
                elif part == "meta":
                    keys = ("lab", "next_hop", "reachable", "distance", "hop_down")
                    body = json.dumps({k: doc[k] for k in keys}).encode()
                else:
                    body = json.dumps(doc).encode()
        if body is None:
            # first poll has not finished yet; say so rather than serving junk
            body = b'{"lab":"' + lab.encode() + b'","warming_up":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=poller, daemon=True).start()

    listeners = [("127.0.0.1", 8888)]
    if BRIDGE and BRIDGE != "127.0.0.1":
        listeners.append((BRIDGE, 8888))

    # Construct every listener FIRST, then serve them all in threads.
    # Calling serve_forever() inside the bind loop blocks on the first
    # one, so the bridge listener never came up and Grafana only ever
    # saw loopback and reported connection refused.
    servers = []
    for b in listeners:
        try:
            servers.append(ThreadingHTTPServer(b, H))
            print('listening on %s:%d' % b, flush=True)
        except Exception as e:
            print('bind %s failed: %s' % (b, e), flush=True)

    for srv in servers:
        threading.Thread(target=srv.serve_forever, daemon=True).start()

    threading.Event().wait()
