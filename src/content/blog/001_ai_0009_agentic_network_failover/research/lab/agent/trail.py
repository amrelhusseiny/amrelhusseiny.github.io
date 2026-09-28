#!/usr/bin/env python3
"""
trail.py - writes the complete decision trail so every step is inspectable
after the run. Nothing is summarised; everything is stored verbatim.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

_CURRENT = None


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def set_trail(t):
    global _CURRENT
    _CURRENT = t


def get_trail():
    return _CURRENT


class Trail:
    def __init__(self, root):
        self.root = Path(root)
        self.trail_dir = self.root / "trail"
        self.ev_dir = self.root / "evidence"
        for d in (self.root, self.trail_dir, self.ev_dir):
            d.mkdir(parents=True, exist_ok=True)
        self.events = []
        self._lines = []

    def log(self, text):
        line = "%s %s" % (now(), text)
        self._lines.append(line)
        print(line, flush=True)

    def event(self, kind, detail=None):
        self.events.append({"ts": now(), "kind": kind, "detail": detail})

    def write(self, stage, name, payload):
        p = self.trail_dir / ("%02d-%s.json" % (stage, name))
        p.write_text(json.dumps(payload, indent=2, default=str))
        self.log("trail: wrote %s" % p.name)

    def evidence(self, node, kind, text):
        d = self.ev_dir / node
        d.mkdir(parents=True, exist_ok=True)
        (d / kind).write_text(text)

    def append_apply(self, rec):
        with (self.trail_dir / "06-apply.ndjson").open("a") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")

    def finalize(self, metrics):
        (self.trail_dir / "07-metrics.json").write_text(
            json.dumps(metrics, indent=2, default=str))
        (self.root / "timeline.txt").write_text("\n".join(self._lines))
        (self.root / "events.ndjson").write_text(
            "\n".join(json.dumps(e, default=str) for e in self.events))
        self.log("trail: finalized -> timeline.txt, trail/, evidence/")
