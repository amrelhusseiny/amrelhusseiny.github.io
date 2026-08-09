#!/usr/bin/env python3
"""Web World Model test: predict-vs-real diff on a genuinely unseen website.

Methodology (matches the official Qwen-AgentWorld "web" domain design,
per prompts/web/system_prompt.txt in github.com/QwenLM/Qwen-AgentWorld):

  1. Capture a REAL accessibility-tree snapshot of a live page
     (snapshot_before.txt) - this is the "Current Page State" input.
  2. Choose one real browser action from the model's action space
     (action.txt), e.g. click(bid='e42').
  3. Ask the model (cryptonaut/Qwen-AgentWorld-35B-A3B-heretic via
     Featherless) to predict the next page state - it NEVER sees the
     real result, only imagines it from the current state + action.
  4. Separately (via a real browser), perform that same action for real
     and capture the actual resulting page (snapshot_after.txt).
  5. Diff the model's <predicted_observation> against the real
     snapshot_after.txt.

This script only does step 3 (the model call) plus the diff in step 5,
assuming snapshot_before.txt / action.txt / snapshot_after.txt already
exist (produced separately via real browser automation, since Featherless
itself has no browser - it only ever sees text we give it).

Usage:
    python3 run_web_test.py --before snapshot_before.txt --action action.txt \
        [--after snapshot_after.txt]
"""

import os
import re
import sys
import json
import time
import argparse
import difflib
from datetime import datetime

import httpx
from dotenv import load_dotenv
load_dotenv()

MODEL = "cryptonaut/Qwen-AgentWorld-35B-A3B-heretic"
BASE_URL = "https://api.featherless.ai/v1"
SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "system_prompts", "web_world_model_system_prompt.txt"
)

parser = argparse.ArgumentParser()
parser.add_argument("--before", required=True, help="Path to the real 'current page state' snapshot (text)")
parser.add_argument("--action", required=True, help="Path to a text file containing the single action, e.g. click(bid='e42')")
parser.add_argument("--after", help="Path to the real 'resulting page state' snapshot (text), for diffing")
parser.add_argument("--max-tokens", type=int, default=4000)
args = parser.parse_args()

API_KEY = os.environ.get("FEATHERLESS_API_KEY")
if not API_KEY:
    print("FEATHERLESS_API_KEY not set", file=sys.stderr)
    sys.exit(1)

with open(SYSTEM_PROMPT_PATH) as f:
    system_prompt = f.read()

with open(args.before) as f:
    before_state = f.read().strip()

with open(args.action) as f:
    action = f.read().strip()

user_message = (
    f"## Current Page State\n{before_state}\n\n"
    f"## Browser Action\n{action}\n"
)

client = httpx.Client(verify=False, timeout=180.0)
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print(f"Model: {MODEL}")
print(f"Action: {action}")
print(f"Current page state length: {len(before_state)} chars")
print("Sending request...")

start = time.perf_counter()
resp = client.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": args.max_tokens,
        "temperature": 0.0,
    },
)
elapsed = round(time.perf_counter() - start, 2)

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}\n{resp.text[:1000]}", file=sys.stderr)
    sys.exit(1)

data = resp.json()
raw_output = data["choices"][0]["message"]["content"]
usage = data.get("usage", {})

print(f"Response received in {elapsed}s")
print(f"Usage: {usage}")

# Extract the <predicted_observation> block
match = re.search(r"<predicted_observation>(.*?)</predicted_observation>", raw_output, re.DOTALL)
predicted_observation = match.group(1).strip() if match else raw_output.strip()
format_compliant = match is not None

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

with open(f"model_raw_response_{timestamp}.txt", "w") as f:
    f.write(raw_output)

with open("model_prediction.txt", "w") as f:
    f.write(predicted_observation)

result = {
    "timestamp": datetime.now().isoformat(),
    "model": MODEL,
    "action": action,
    "elapsed_seconds": elapsed,
    "usage": usage,
    "format_compliant": format_compliant,
    "predicted_observation_length_chars": len(predicted_observation),
}

# If we have the real "after" state, diff against it
if args.after:
    with open(args.after) as f:
        after_state = f.read().strip()

    diff_lines = list(difflib.unified_diff(
        after_state.splitlines(),
        predicted_observation.splitlines(),
        fromfile="REAL (ground truth)",
        tofile="PREDICTED (model)",
        lineterm="",
    ))
    with open("diff_real_vs_predicted.txt", "w") as f:
        f.write("\n".join(diff_lines))

    # crude similarity ratio as a quick quantitative signal
    ratio = difflib.SequenceMatcher(None, after_state, predicted_observation).ratio()
    result["real_state_length_chars"] = len(after_state)
    result["diff_line_count"] = len([l for l in diff_lines if l.startswith("+") or l.startswith("-")])
    result["similarity_ratio"] = round(ratio, 4)
    print(f"Similarity ratio (real vs predicted): {ratio:.4f}")
    print(f"Diff lines (added/removed): {result['diff_line_count']}")

with open("test_result.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
