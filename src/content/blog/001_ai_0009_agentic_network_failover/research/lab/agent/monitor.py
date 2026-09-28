#!/usr/bin/env python3
"""
monitor.py - entrypoint. Builds the LangGraph workflow and runs it once.

Every artefact lands under <out>/<run-id>/ :
  trail/     numbered decision trail (what was judged, what Bunny did)
  evidence/  the raw per-router logs and routing tables, unfiltered
  timeline.txt  the human-readable run log
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from graph import build_graph
from models import ModelError
from trail import Trail, set_trail
from topology import DEVICES


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/agent/out")
    ap.add_argument("--reset-cursors", action="store_true",
                    help="re-judge every log line from scratch")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    trail = Trail(out / run_id)
    set_trail(trail)
    trail.log("=== run %s ===" % run_id)
    trail.log("devices: %s" % json.dumps(DEVICES))

    cpath = out / "cursors.json"
    cursors = {}
    if cpath.exists() and not args.reset_cursors:
        try:
            cursors = json.loads(cpath.read_text())
            trail.log("resumed log cursors: %s" % cursors)
        except Exception:
            cursors = {}
    elif args.reset_cursors:
        trail.log("cursors reset by request")

    metrics = {"run_id": run_id,
               "started": datetime.now(timezone.utc).isoformat(
                                       timespec="milliseconds"),
               "devices": DEVICES}

    t0 = time.time()
    try:
        graph = build_graph()
        state = graph.invoke({"cursors": cursors}, {"recursion_limit": 80})
        cpath.write_text(json.dumps(state.get("cursors") or {}, indent=2))
    except ModelError as e:
        metrics["conclusion"] = "abort_model_error"
        metrics["error"] = str(e)
        metrics["total_s"] = round(time.time() - t0, 2)
        trail.log("ABORT (model): %s" % e)
        trail.finalize(metrics)
        print("\nABORTED - model error: %s" % e)
        return 2
    except Exception as e:
        metrics["conclusion"] = "abort_unexpected"
        metrics["error"] = repr(e)
        metrics["total_s"] = round(time.time() - t0, 2)
        trail.log("ABORT (unexpected): %r" % e)
        trail.finalize(metrics)
        raise

    metrics["total_s"] = round(time.time() - t0, 2)
    metrics["conclusion"] = state.get("conclusion")
    metrics["faulty_before"] = state.get("faulty_before")
    metrics["faulty_after"] = state.get("faulty_after")
    metrics["judged_before"] = state.get("judged_before")
    metrics["judged_after"] = state.get("judged_after")
    metrics["bunny_result"] = state.get("bunny_result")
    metrics["cursors"] = state.get("cursors")
    trail.finalize(metrics)

    print("\nCONCLUSION : %s" % metrics["conclusion"])
    print("faulty before : %s" % (metrics["faulty_before"] or "none"))
    print("faulty after  : %s" % (metrics["faulty_after"] or "none"))
    print("elapsed       : %ss" % metrics["total_s"])
    print("bundle        : %s" % (out / run_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
