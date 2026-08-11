# Cerebras vs DeepInfra — All 3 Models

Real test: same 3 models, same identical prompt (~3000-word network-infra
guide), `max_tokens=8000`, run via OpenRouter on both Cerebras and
DeepInfra. Cerebras numbers reused from the earlier same-session run
(`research/cerebras_all_models_test/`); DeepInfra numbers are fresh from
this run.

## Results

| Model | Provider | TTFT | TPS | Tokens | Total Time | Multiplier |
|---|---|---|---|---|---|---|
| gpt-oss-120b | Cerebras | 1.77s | 1,262.4 | 7,991 | 8.10s | — |
| gpt-oss-120b | DeepInfra | **75.87s** | 12.55 | 7,461 | 670.22s | **101x slower** |
| Gemma 4 31B | Cerebras | 0.71s | 1,040.4 | 2,934 | 3.53s | — |
| Gemma 4 31B | DeepInfra | 0.97s | 63.74 | 3,414 | 54.53s | **16x slower** |
| GLM 4.7 | Cerebras | 4.98s | 437.1 | 4,388 | 15.02s | — |
| GLM 4.7 | DeepInfra | 61.46s | 33.08 | 4,141 | 186.65s | **13x slower** |

## Takeaway

Cerebras wins on every single model, but the margin varies a lot -
13x to 101x. The gpt-oss-120b DeepInfra run is a notable outlier: TTFT of
75.9 seconds is unusually high (an earlier, separate DeepInfra run of the
same model had TTFT of only 5.3s) — real evidence of DeepInfra's load
variance. GLM 4.7 also had a slow TTFT (61.5s) on DeepInfra this run.
Worth being transparent in the article that standard GPU-cluster serving
has meaningfully higher variance run-to-run than Cerebras's wafer-scale
serving showed across all our tests so far.

## Files

- `run_provider_model.py` — generalized script (`--provider`, `--model`, `--label`)
- `results_deepinfra_*.json` — structured metrics per model (DeepInfra, fresh)
- `response_deepinfra_*.txt` — full real response per model (DeepInfra)
- `cerebras_vs_deepinfra_all_models.gif` — grouped-bar comparison visual
- Cerebras-side data reused from `../cerebras_all_models_test/results_cerebras_*.json`
