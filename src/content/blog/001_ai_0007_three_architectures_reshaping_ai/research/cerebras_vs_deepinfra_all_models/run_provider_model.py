#!/usr/bin/env python3
"""Multi-provider showcase: real call to a chosen model via OpenRouter,
routed exclusively to a chosen provider. Same prompt/settings used across
runs for an apples-to-apples comparison.

Usage:
    python3 run_provider_model.py --provider DeepInfra --model openai/gpt-oss-120b --label gpt-oss-120b
    python3 run_provider_model.py --provider DeepInfra --model google/gemma-4-31b-it --label gemma-4-31b
    python3 run_provider_model.py --provider DeepInfra --model z-ai/glm-4.7 --label glm-4.7
"""

import os
import sys
import json
import time
import argparse
import tiktoken
from datetime import datetime

import httpx
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--provider", required=True, help="OpenRouter provider name, e.g. DeepInfra, cerebras")
parser.add_argument("--model", required=True, help="OpenRouter model slug, e.g. openai/gpt-oss-120b")
parser.add_argument("--label", required=True, help="Short label used for output filenames")
parser.add_argument("--max-tokens", type=int, default=8000)
args = parser.parse_args()

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    print("OPENROUTER_API_KEY not set", file=sys.stderr)
    sys.exit(1)

http_client = httpx.Client(verify=False)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY, http_client=http_client)

_encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(_encoder.encode(text))

# Identical prompt used across all runs (Cerebras + DeepInfra) for apples-to-apples comparison
PROMPT = (
    "Write a comprehensive, ~3000-word technical guide on configuring a network "
    "infrastructure for a mid-size enterprise (500 employees). Structure it with "
    "clear sections and subheadings, and be thorough and concrete throughout. "
    "Cover, in detail: "
    "(1) VLAN design and segmentation - how to group users/devices, why segmentation "
    "matters for security and broadcast domains, with example VLAN IDs; "
    "(2) IP addressing and subnetting - a complete addressing plan for the campus, "
    "with example subnets, masks, and a table mapping VLANs to subnets; "
    "(3) Firewall architecture and rules - placement, default-deny posture, east-west "
    "filtering, with example rule sets; "
    "(4) VPN and remote access - site-to-site and remote-user VPNs, protocols, "
    "cryptography choices, with a sample configuration snippet; "
    "(5) Network monitoring and observability - SNMP, flow telemetry (NetFlow/sFlow), "
    "logging, alerting thresholds; "
    "(6) High availability and failover - redundant links, spanning tree, LACP "
    "port-channels, first-hop redundancy; "
    "(7) Security hardening and best practices - segmentation, access control, "
    "change management, auditing. "
    "Include tables where they aid clarity, and write in a practical, vendor-agnostic "
    "style suitable for an experienced network engineer."
)

print(f"Model: {args.model} (label={args.label})")
print(f"Provider: {args.provider} (via OpenRouter)")
print("Sending request...")

full_text = ""
token_count = 0
start = time.perf_counter()
first_token_time = None
chunk_count = 0

try:
    stream = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": PROMPT}],
        stream=True,
        max_tokens=args.max_tokens,
        extra_body={"provider": {"only": [args.provider]}},
    )
    for chunk in stream:
        chunk_count += 1
        if chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            if first_token_time is None:
                first_token_time = time.perf_counter()
                print(f"First token at {round((first_token_time - start) * 1000, 2)} ms")
            token_count += count_tokens(text)
            full_text += text
            if token_count % 500 < 5:
                print(f"  ...{token_count} tokens so far @ {round(time.perf_counter()-start,1)}s", flush=True)
except Exception as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    sys.exit(1)

end = time.perf_counter()
ttft_ms = round((first_token_time - start) * 1000, 2) if first_token_time else None
total_s = round(end - start, 2)
gen_s = round(end - first_token_time, 2) if first_token_time else 0
avg_tps = round(token_count / gen_s, 2) if gen_s > 0 else 0

result = {
    "timestamp": datetime.now().isoformat(),
    "architecture": "GPU (standard cluster)" if args.provider.lower() == "deepinfra" else "LPU (wafer-scale)",
    "provider": args.provider,
    "model": args.model,
    "label": args.label,
    "ttft_ms": ttft_ms,
    "tps": avg_tps,
    "total_tokens": token_count,
    "total_time_s": total_s,
    "chunks_received": chunk_count,
}

print(f"TTFT: {ttft_ms}ms | Total: {total_s}s | Tokens: {token_count} | TPS: {avg_tps}")

with open(f"results_{args.provider.lower()}_{args.label}.json", "w") as f:
    json.dump(result, f, indent=2)
with open(f"response_{args.provider.lower()}_{args.label}.txt", "w") as f:
    f.write(full_text)

print(json.dumps(result, indent=2))
