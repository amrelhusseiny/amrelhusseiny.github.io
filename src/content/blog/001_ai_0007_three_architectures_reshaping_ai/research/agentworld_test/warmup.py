#!/usr/bin/env python3
"""Warm-up / availability poller for a Featherless "niche" model.

Per Featherless docs (featherless.ai/docs/api-reference-error-codes):
  - Models are in one of three states: cold, loading, warm.
  - 503 "capacity_exhausted" means: retry the SAME request; if it still
    fails after 3 retries, the model class may be temporarily unavailable.
  - Cold-start time: "as little as 5 minutes for small models, up to an
    hour for larger ones." Qwen-AgentWorld-35B-A3B is a 35B-parameter
    model, so we budget generously.

This script:
  1. Checks GET /v1/models/{id} for the live `availability` field
     (tier, is_hot_live, loading_stage) - refreshed ~every 5 minutes
     server-side.
  2. Sends a minimal chat completion request to actually trigger loading
     (per docs: "any subscriber may load a model" just by requesting it).
  3. Retries on 503 with backoff, logging every attempt with a timestamp,
     until it gets a real response or a time budget is exhausted.

Run this BEFORE the real test script. It exits 0 once the model responds
successfully, or exits 1 if the budget is exhausted (re-run later or
increase --budget-minutes).
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

import httpx
from dotenv import load_dotenv
load_dotenv()

MODEL = "cryptonaut/Qwen-AgentWorld-35B-A3B-heretic"
BASE_URL = "https://api.featherless.ai/v1"

parser = argparse.ArgumentParser()
parser.add_argument("--budget-minutes", type=float, default=20.0,
                     help="Total time budget to keep retrying before giving up")
parser.add_argument("--poll-interval", type=float, default=20.0,
                     help="Seconds between attempts")
args = parser.parse_args()

API_KEY = os.environ.get("FEATHERLESS_API_KEY")
if not API_KEY:
    print("FEATHERLESS_API_KEY not set in environment/.env", file=sys.stderr)
    sys.exit(1)

client = httpx.Client(verify=False, timeout=60.0)
headers = {"Authorization": f"Bearer {API_KEY}"}

LOG_FILE = f"warmup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_lines = []


def log(msg):
    ts = datetime.now().isoformat()
    line = f"{ts} {msg}"
    print(line, flush=True)
    log_lines.append(line)


def check_catalog_status():
    """Read the model's cached availability snapshot from the catalog."""
    try:
        resp = client.get(f"{BASE_URL}/models/{MODEL}", headers=headers)
        data = resp.json()
        avail = data.get("availability", {})
        log(f"[catalog] status={data.get('status')} tier={avail.get('tier')} "
            f"is_hot_live={avail.get('is_hot_live')} loading_stage={avail.get('loading_stage')}")
        return avail
    except Exception as exc:
        log(f"[catalog] check failed: {exc}")
        return {}


def try_completion():
    """Send a minimal completion request; this is also what triggers a
    cold model to start loading, per Featherless docs."""
    start = time.perf_counter()
    try:
        resp = client.post(
            f"{BASE_URL}/chat/completions",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
                "max_tokens": 5,
            },
        )
        elapsed = round(time.perf_counter() - start, 2)
        if resp.status_code == 200:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            log(f"[completion] SUCCESS in {elapsed}s -> {text!r}")
            return True
        else:
            body = resp.text[:300]
            log(f"[completion] HTTP {resp.status_code} in {elapsed}s -> {body}")
            return False
    except Exception as exc:
        elapsed = round(time.perf_counter() - start, 2)
        log(f"[completion] EXCEPTION after {elapsed}s: {exc}")
        return False


log(f"=== Warm-up started | model={MODEL} | budget={args.budget_minutes}min "
    f"| poll_interval={args.poll_interval}s ===")

start_time = time.perf_counter()
budget_s = args.budget_minutes * 60
attempt = 0
success = False

while True:
    attempt += 1
    elapsed_total = round(time.perf_counter() - start_time, 1)
    if elapsed_total > budget_s:
        log(f"=== Budget exhausted after {elapsed_total}s ({attempt - 1} attempts). Giving up. ===")
        break

    log(f"--- Attempt {attempt} (elapsed {elapsed_total}s) ---")
    check_catalog_status()
    ok = try_completion()
    if ok:
        success = True
        log(f"=== Model is WARM after {elapsed_total}s and {attempt} attempt(s). ===")
        break

    log(f"Sleeping {args.poll_interval}s before retry...")
    time.sleep(args.poll_interval)

with open(LOG_FILE, "w") as f:
    f.write("\n".join(log_lines) + "\n")

summary = {
    "model": MODEL,
    "success": success,
    "attempts": attempt,
    "elapsed_seconds": round(time.perf_counter() - start_time, 1),
    "timestamp": datetime.now().isoformat(),
}
with open("warmup_result.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
sys.exit(0 if success else 1)
