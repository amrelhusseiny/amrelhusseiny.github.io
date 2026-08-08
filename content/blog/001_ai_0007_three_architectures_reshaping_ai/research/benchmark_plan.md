
---

## RESULTS — LONG RUN (Recorded 2026-08-08)

> Second, longer run to make the race between architectures more visible.
> Extended ~3000-word prompt for Cerebras/DeepInfra (same model and prompt,
> hardware-only difference) and `max_tokens=8000` for all three. This run
> also produced the **light-mode** terminal recordings
> (`demo_cerebras.gif`, `demo_deepinfra.gif`, `demo_mercury.gif`).

### Summary Comparison (Long Run)

| Architecture | Model | Provider | TTFT (ms) | Avg TPS | Tokens | Total Time (s) |
|---|---|---|---|---|---|---|
| **LPU (wafer-scale)** | `openai/gpt-oss-120b` | Cerebras (via OpenRouter) | **979.26** | 1,041.89 | 6,939 | 7.64 |
| **Diffusion (parallel decoding)** | `inception/mercury-2` | Inception (via OpenRouter) | 5,117.20 | 1,009.15 | 2,866 | 7.96 |
| **GPU (standard cluster)** | `openai/gpt-oss-120b` | DeepInfra (via OpenRouter) | 5,302.18 | **50.13** | 7,706 | **159.02** |

**Speed multipliers (this run):**
- Cerebras **20.8x** faster than DeepInfra on the identical model (1,041.89 vs 50.13 tok/s).
- Mercury **20.1x** faster than DeepInfra (1,009.15 vs 50.13 tok/s).
- Cerebras and Mercury effectively tied on throughput this run (1.0x).

**Notable change vs the 2026-08-05 run:** Mercury's sustained throughput
came in far higher this time (~1,009 tok/s vs ~747 tok/s earlier), bringing
it level with Cerebras on tokens/sec. The still-decisive differentiators for
Cerebras are TTFT (0.98s vs Mercury's 5.1s) and completing a much longer
output (6,939 vs 2,866 tokens). DeepInfra remains the dramatic laggard —
**159s for 7,706 tokens** vs Cerebras finishing 6,939 tokens in 7.6s.

### Notes
- Mercury's JSON output remained **invalid** (`json_valid: false`) — it
  wraps output in markdown fences and inserts placeholder comments instead
  of exhaustively enumerating connections. Consistent finding across runs.
- Full raw responses saved as `results_*_showcase_full_response.txt`.
- Race animation `race_comparison_v2.gif` (light, monochrome) built from
  this run's data.
