#!/usr/bin/env python3
"""Showcase Recording: Mercury 2 (Diffusion-Based) - REAL DATA, LONG RUN
   Real call to inception/mercury-2 via OpenRouter, routed exclusively
   to the inception provider (extra_body={"provider": {"only": ["inception"]}}).
   Same JSON-topology prompt as run_mercury.py (Test B); max_tokens raised
   to 8000 for a longer run. Includes the JSON-validity check that's core
   to Mercury's structural test (kept as an honest finding: large-JSON
   tasks tend to shortcut with placeholder comments). LIGHT MODE styling.

   Capture with:
     asciinema rec --window-size 150x40 --command "python3 showcase_mercury.py" demo_mercury.cast
     agg demo_mercury.cast demo_mercury.gif   (after injecting light theme)

   NOTE: Must be run from a network that can reach openrouter.ai -
   the corporate deployment server blocks it via Forcepoint."""

import os, sys, json, time, threading
import httpx
import tiktoken
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

_encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(_encoder.encode(text))

from rich.console import Console, Group
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align

console = Console(color_system="truecolor")

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    console.print("[bold red]OPENROUTER_API_KEY not set in environment/.env[/]")
    sys.exit(1)

http_client = httpx.Client(verify=False)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY, http_client=http_client)

MODEL = "inception/mercury-2"
PROVIDER_ONLY = ["inception"]
MAX_TOKENS = 8000

PROMPT = (
    "Output a strictly formatted, deeply nested JSON schema representing "
    "a corporate network topology. Include routers, switches, VLANs, "
    "subnets, firewalls, servers, endpoints, and their interconnections. "
    "Make it detailed and realistic for a 500-employee enterprise."
)

MAX_DISPLAY_CHARS = 550

LOG_FILE = f"mercury_showcase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_lines = []

def log(msg):
    ts = datetime.now().isoformat()
    log_lines.append(f"{ts} [INFO] {msg}")

log(f"Mercury 2 diffusion showcase started | model={MODEL} | provider={PROVIDER_ONLY} | max_tokens={MAX_TOKENS}")

console.print(Panel(
    Text(PROMPT, style="bold #1a1a1a"),
    title="[bold #2a2a2a] PROMPT — MERCURY 2 (Diffusion, REAL) [/]",
    border_style="#5f5f5f",
    style="on #ffffff",
))

full_text = ""
token_count = 0
start = time.perf_counter()
first_token_time = None
stop_flag = threading.Event()


def render():
    now = time.perf_counter()
    if first_token_time is None:
        connecting_elapsed = now - start
        status = Text()
        status.append("  \u23f3 CONNECTING TO MODEL  ", style="bold #2a2a2a")
        status.append(f"{connecting_elapsed:5.2f}s", style="bold #5f5f5f")
        return Group(
            Panel(Align.center(status), title="[bold #2a2a2a] STATUS [/]", border_style="#9c9c9c", style="on #ffffff"),
        )
    elapsed = now - first_token_time
    tps = (token_count / elapsed) if elapsed > 0 else 0

    display_text = full_text
    if len(display_text) > MAX_DISPLAY_CHARS:
        display_text = "\u2026" + display_text[-MAX_DISPLAY_CHARS:]

    stats = Text()
    stats.append("  TOKENS ", style="bold #2a2a2a")
    stats.append(f"{token_count:<6}", style="bold #1a1a1a")
    stats.append("  LIVE TPS ", style="bold #2a2a2a")
    stats.append(f"{tps:6.1f} tok/s", style="bold #1a1a1a")
    stats.append("  ELAPSED ", style="bold #2a2a2a")
    stats.append(f"{elapsed:5.2f}s", style="bold #1a1a1a")
    return Group(
        Panel(Text(display_text, style="bold #1a1a1a"), title="[bold #2a2a2a] RESPONSE (JSON) [/]", border_style="#5f5f5f", style="on #ffffff"),
        Panel(Align.center(stats), border_style="#eeeeee", style="on #ffffff"),
    )


def ticker(live):
    while not stop_flag.is_set():
        live.update(render())
        time.sleep(0.05)


chunk_count = 0
with Live(render(), console=console, refresh_per_second=15, screen=False) as live:
    t = threading.Thread(target=ticker, args=(live,), daemon=True)
    t.start()
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            stream=True,
            max_tokens=MAX_TOKENS,
            extra_body={"provider": {"only": PROVIDER_ONLY}},
        )
        for chunk in stream:
            chunk_count += 1
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                    log(f"First token at {round((first_token_time - start) * 1000, 2)} ms")
                token_count += count_tokens(text)
                full_text += text
    except Exception as exc:
        stop_flag.set()
        console.print(f"[bold red]Request failed: {exc}[/]")
        log(f"ERROR: {exc}")
        raise
    finally:
        stop_flag.set()
        t.join()

end = time.perf_counter()
ttft_ms = round((first_token_time - start) * 1000, 2) if first_token_time else None
total_s = round(end - start, 2)
gen_s = round(end - first_token_time, 2) if first_token_time else 0
avg_tps = round(token_count / gen_s, 2) if gen_s > 0 else 0

json_valid = False
try:
    json.loads(full_text)
    json_valid = True
except Exception:
    json_valid = False

summary = Text()
summary.append("  TTFT           ", style="bold #2a2a2a")
summary.append(f"{ttft_ms} ms\n", style="bold #1a1a1a")
summary.append("  TOTAL TIME     ", style="bold #2a2a2a")
summary.append(f"{total_s}s\n", style="bold #1a1a1a")
summary.append("  TOKENS         ", style="bold #2a2a2a")
summary.append(f"{token_count}\n", style="bold #1a1a1a")
summary.append("  AVERAGE TPS    ", style="bold #2a2a2a")
summary.append(f"{avg_tps} tok/s\n", style="bold #1a1a1a")
summary.append("  JSON VALID     ", style="bold #2a2a2a")
summary.append(f"{json_valid}", style="bold #1a1a1a")

console.print(Panel(
    summary,
    title="[bold white on #2a2a2a] GENERATION COMPLETE — MERCURY 2 (REAL) [/]",
    border_style="#2a2a2a",
    style="on #ffffff",
))

log(f"AGGREGATE: TTFT={ttft_ms}ms TOTAL={total_s}s TOKENS={token_count} AVG_TPS={avg_tps} JSON_VALID={json_valid}")
log("Mercury 2 diffusion showcase completed")

with open(LOG_FILE, "w") as f:
    f.write("\n".join(log_lines) + "\n")

results = {
    "timestamp": datetime.now().isoformat(),
    "architecture": "Diffusion (parallel decoding)",
    "provider": "inception",
    "model": MODEL,
    "ttft_ms": ttft_ms,
    "tps": avg_tps,
    "total_tokens": token_count,
    "total_time_s": total_s,
    "json_valid": json_valid,
    "chunks_received": chunk_count,
    "response_length_chars": len(full_text),
    "response_preview": full_text[:500],
}
with open("results_mercury_showcase.json", "w") as f:
    json.dump(results, f, indent=2)
with open("results_mercury_showcase_full_response.txt", "w") as f:
    f.write(full_text)

# Hold the final frame for the recording
time.sleep(3)
