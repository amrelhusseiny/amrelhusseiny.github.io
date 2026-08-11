# All Cerebras Models — Findings

Real, same-session test: 3 different models, all routed exclusively to
Cerebras via OpenRouter (`extra_body={"provider":{"only":["cerebras"]}}`),
identical prompt (~3000-word network-infra guide), `max_tokens=8000`.

Complementary to the earlier "same model, different hardware" test — this
one holds hardware constant and varies the model.

## Results

| Model | Provider | TTFT | Avg TPS | Tokens | Total Time |
|---|---|---|---|---|---|
| `openai/gpt-oss-120b` | Cerebras | 1.77s | **1,262.4** | 7,991 | 8.10s |
| `google/gemma-4-31b-it` | Cerebras | **0.71s** | 1,040.4 | 2,934 | 3.53s |
| `z-ai/glm-4.7` | Cerebras | 4.98s | 437.1 | 4,388 | 15.02s |

## Takeaway

Same wafer-scale hardware, **2.9x spread in throughput** between the
fastest (gpt-oss-120b) and slowest (GLM 4.7) model. Gemma had the lowest
TTFT (fastest to first token) despite not having the highest sustained
TPS. This confirms model architecture/size still matters even when
hardware is held constant — Cerebras raises the ceiling, but doesn't
equalize every model to the same speed.

## Files

- `run_cerebras_model.py` — parameterized script (`--model`, `--label`)
- `results_cerebras_*.json` — structured metrics per model
- `response_cerebras_*.txt` — full real response per model
- `cerebras_all_models_race.gif` — race-style comparison visual
