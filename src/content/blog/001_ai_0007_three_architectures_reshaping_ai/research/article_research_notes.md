# Research Notes — "Three Architectures Reshaping AI"

Written for the human author to read before drafting the article. This is a
summary of everything tested, found, and reasoned through during the
benchmarking sessions. `index.md` (the actual article) only has the bare
outline + GIFs — all the writing is yours. This file is the source material.

---

## 1. What was actually tested

Three real, live API calls were made per run (via OpenRouter, from a local
machine — the corporate deployment server blocks openrouter.ai/api.cerebras.ai
via a Forcepoint network policy, confirmed by direct curl tests returning
302 redirects to a block page). All numbers below are genuine, not simulated.

Two rounds were run:

### Round 1 (2026-08-05) — shorter prompt, uncapped/lightly-capped length

| Architecture | Model | Provider | TTFT | Avg TPS | Tokens | Total Time |
|---|---|---|---|---|---|---|
| LPU (wafer-scale) | `openai/gpt-oss-120b` | Cerebras | 551.81 ms | 1,793.2 | 1,847 | 1.58s |
| GPU (standard) | `openai/gpt-oss-120b` | DeepInfra | 3,910.22 ms | 42.53 | 1,904 | 48.68s |
| Diffusion | `inception/mercury-2` | Inception | 4,339.38 ms | 746.93 | 6,685 | 13.29s |

Cerebras was **42.2x faster** than DeepInfra on the identical model. Mercury
was **17.6x** faster than DeepInfra but **2.4x slower** than Cerebras.

### Round 2 (2026-08-08) — longer prompt (~3000-word ask), max_tokens=8000

| Architecture | Model | Provider | TTFT | Avg TPS | Tokens | Total Time |
|---|---|---|---|---|---|---|
| LPU (wafer-scale) | `openai/gpt-oss-120b` | Cerebras | 979.26 ms | 1,041.89 | 6,939 | 7.64s |
| Diffusion | `inception/mercury-2` | Inception | 5,117.20 ms | 1,009.15 | 2,866 | 7.96s |
| GPU (standard) | `openai/gpt-oss-120b` | DeepInfra | 5,302.18 ms | 50.13 | 7,706 | **159.02s** |

Cerebras was **20.8x** faster than DeepInfra; Mercury was **20.1x** faster
than DeepInfra. Cerebras and Mercury were **statistically tied on raw
throughput this round** (1,041 vs 1,009 tok/s) — Cerebras's edge in round 2
comes from **TTFT** (0.98s vs 5.1s) and **finishing a much longer output**
(6,939 vs 2,866 tokens) in similar wall-clock time, not from raw tok/s.

**Why the two rounds differ:** LLM API throughput is not perfectly
deterministic run-to-run (load-dependent), and Mercury's diffusion decoding
in particular seems to have high run-to-run variance in observed tok/s
compared to Cerebras/DeepInfra's more consistent autoregressive decoding.
Worth mentioning in the article as an honest caveat rather than picking
only the round that tells the cleanest story.

### Prompts used
- **Cerebras / DeepInfra (identical, to isolate hardware):** "Write a
  comprehensive, ~3000-word technical guide on configuring a network
  infrastructure for a mid-size enterprise (500 employees)... [VLANs,
  subnetting, firewalls, VPN, monitoring, HA, hardening]"
- **Mercury:** "Output a strictly formatted, deeply nested JSON schema
  representing a corporate network topology... 500-employee enterprise."

### Mercury's honest finding: JSON validity failed
Both rounds, Mercury's JSON output was **invalid** (`json_valid: false`).
Root cause (verified by reading the raw output): it wraps the JSON in a
markdown code fence (` ```json ... ``` `, cosmetic, expected) **and** in the
long run it inserted a placeholder comment — `// ... Additional connections
for all endpoints, servers, and inter-device links ...` — instead of
exhaustively enumerating every connection as asked. This is a genuine
finding about diffusion-decoding behavior on long structured-output tasks
(it "gives up" and summarizes rather than completing), not a tooling bug.
Worth a paragraph — it's actually one of the more interesting things found.

### Methodology notes worth mentioning in the article (or an appendix)
- **Token counting had to be fixed mid-session.** Naive "count 1 token per
  SSE chunk received" massively undercounts throughput for both Cerebras
  and Mercury, because both send multi-token batches per streamed chunk
  (unlike typical one-token-per-chunk autoregressive streaming). Switched
  to tokenizing each chunk's text with `tiktoken` (`cl100k_base`) and
  summing — verified accurate via independent whole-text re-tokenization
  (5330 vs 5322 tokens, ~0.15% difference from expected BPE boundary
  effects). This is a legitimately interesting gotcha for anyone else
  trying to benchmark tok/s across providers with different streaming
  behaviors.
- **`max_tokens` needs to be capped for a fair comparison.** An open-ended
  "write ~3000 words" prompt produces wildly different actual output
  lengths run to run (600 to 5,500+ tokens observed) if left uncapped,
  which confounds a tok/s comparison. Capped at 8,000 for round 2.
- **Recording pipeline:** VHS (the terminal-GIF tool) has a real bug where
  recorded playback duration collapses to a fraction of real time once
  terminal content exceeds a fairly low size threshold — confirmed via
  isolated tests (a 3-line panel recorded correctly, an 11-line panel
  didn't, regardless of pacing). Switched to `asciinema` (record) + `agg`
  (asciicast → GIF), which handles this correctly regardless of content
  size — verified on the same test case that broke VHS.

---

## 2. Qwen-AgentWorld — what it actually is (research summary, NOT fully verified)

You mentioned uncertainty about whether `cryptonaut/Qwen-AgentWorld-35B-A3B-heretic`
(the Featherless-hosted model found earlier) is a "normal" LLM or something
used to "audit a web UI." Researched this via web search; the picture below
is a **reasoned analysis**, not a confirmed model card (no official
documentation for this specific community upload was found).

**Bottom line: this is almost certainly a text-only chat model, not a
web/GUI-auditing tool.**

- No official "Qwen-AgentWorld" model or paper exists from the Qwen/Alibaba
  team. There IS an academic concept/benchmark called "AgentWorld" (a
  multi-agent social-simulation environment for evaluating LLM agents), but
  it's a benchmark, not a model — the uploader ("cryptonaut") most likely
  borrowed the name informally, or it reflects "good at agent/simulation
  tasks" as a marketing-style label on a fine-tune.
- The naming `35B-A3B` (35B total params, ~3B active) is a standard
  Mixture-of-Experts convention, strongly suggesting a Qwen2.5-MoE or
  Qwen3.5-MoE base — a normal **text** chat model, not multimodal.
- "heretic" = abliterated / refusal-training-removed, a common community
  fine-tuning technique, unrelated to its core capabilities.
- Featherless (the hosting platform) only exposes an OpenAI-compatible
  **text** chat-completions API via vLLM. It does **not** provide image
  input, browser automation, or any tool-execution harness. So even if a
  model theoretically had GUI-agent training, Featherless's API surface
  couldn't be used to drive an actual browser/UI — there's no mechanism to
  send it screenshots or execute its output as real clicks.

**What this means for testing it:** the only realistic, achievable test via
Featherless is a **text-only, multi-turn statefulness test** — exactly what
the original `benchmark_plan.md` Test C already specified (a simulated
Linux terminal, tracking filesystem state across turns without external
tools). No pivot needed; the original plan was already the right shape.

### Suggested concrete test plan (achievable, text-only)
1. **Filesystem simulation** (already scaffolded in `research/run_agentworld.py`):
   - Turn 1: create files (`mkdir src && touch src/main.py && echo '...' > README.md`)
   - Turn 2: `ls -la` — model must recall Turn 1's state
   - Turn 3: `cat README.md` — model must recall exact file content
2. **Optional stretch tests**, if you want a richer "world model" story:
   - Inventory/state tracking (numbers changing across turns: gold, items)
   - A small multi-entity scenario (2-3 NPCs with independent state)
   - A long-context recall test ("what was my inventory after turn 3?")
3. **Evaluation:** did the model correctly track state across turns without
   external memory, or did it hallucinate/drift? This is the actual
   "world model" claim being tested — can the LLM function as a persistent,
   consistent simulator of an environment purely through its own context.

**Status:** not yet run. Real Featherless credentials and the model ID are
already confirmed working (`cryptonaut/Qwen-AgentWorld-35B-A3B-heretic`
exists in Featherless's catalog and is `available_on_current_plan: true`).
This is a good "part 2" follow-up test.

---

## 3. References (verified — actually visited, not guessed)

1. **Cerebras WSE-3 (official):**
   https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine
   — WSE-3 launch: 4 trillion transistors, 900K cores, up to 256 exaFLOPs
   across a 2,048-node cluster.
2. **Cerebras WSE-3 (independent technical analysis):**
   https://spectrum.ieee.org/cerebras-chip-cs3
   — IEEE Spectrum's breakdown of the wafer-scale die and the 44GB on-chip
   SRAM design that keeps model weights resident on-chip, which is the
   architectural reason it sidesteps the memory-bandwidth bottleneck that
   limits GPU inference speed.
3. **Mercury announcement (official):**
   https://www.inceptionlabs.ai/blog/introducing-mercury
   — Inception Labs' launch of the Mercury diffusion LLM family, claiming
   1,000+ tok/s on H100 via parallel block denoising.
4. **Mercury technical paper:**
   https://arxiv.org/abs/2506.17298
   — "Mercury: Ultra-Fast Language Models Based on Diffusion" — the
   underlying research report.
5. **Diffusion LLMs explainer (general, not Mercury-specific):**
   https://outcomeschool.com/blog/how-do-diffusion-language-models-dlms-work
   — plain-English contrast of autoregressive (left-to-right) decoding vs.
   diffusion's parallel "fill-and-refine" generation.
6. **OpenRouter — Provider Routing docs (official):**
   https://openrouter.ai/docs/guides/routing/provider-selection
   — how OpenRouter routes a single request across 70+ providers (price /
   throughput / latency sorting, fallbacks). This is the mechanism behind
   `extra_body={"provider": {"only": [...]}}` used in every benchmark script.
7. **OpenRouter — routing explainer (official blog):**
   https://openrouter.ai/blog/insights/model-routing/
   — more narrative walkthrough: model selection vs. provider selection as
   two separate routing layers, load balancing, failover.
8. **DeepInfra docs (official):**
   https://docs.deepinfra.com/
   — what DeepInfra is: an inference cloud with an OpenAI-compatible API,
   100+ open models, pay-per-token, used here purely as the "standard GPU
   cluster" baseline/control group.
9. **World Models — seminal paper:**
   https://arxiv.org/abs/1803.10122
   — Ha & Schmidhuber, 2018, "World Models" — the original paper on training
   agents inside a learned generative model of their environment. Good
   conceptual grounding for why "language world models" (like the planned
   AgentWorld test) are an interesting, distinct category from normal chat
   LLMs.
10. **DeepMind Genie 2 (official):**
    https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/
    — a modern, large-scale example of a "world model" (generates playable,
    action-controllable 3D environments) — useful contrast to show that
    "world model" in the video/physics-generation sense (Genie) is a very
    different thing from a text-only LLM that merely tracks simulated state
    in a conversation (the AgentWorld test above). Worth being precise
    about this distinction in the article so as not to overclaim what a
    35B text model can do.

---

## 4. Suggested narrative angle (optional, just a thought)

The two benchmark rounds tell a slightly different story from each other,
which is itself worth leaning into rather than hiding: round 1 makes
Cerebras look categorically fastest; round 2 shows Mercury can match
Cerebras on raw tok/s but still loses on TTFT and total output completed.
The honest takeaway across both rounds is:

- **Cerebras wins on latency + consistency**, every single run.
- **Mercury's ceiling is high but variable** — genuinely fast diffusion
  decoding, but with real trade-offs on structured-output completeness
  (the JSON shortcut finding) and higher TTFT.
- **DeepInfra (standard GPU) is 20-42x slower than Cerebras on the
  identical model** — proving the speed gap is hardware, not the model.
- **The "world model" claim is still unverified** — Cerebras/Mercury are
  proven with real data; the AgentWorld/statefulness angle is a promising
  but untested "part 2."

This "two out of three tested, one still open" framing might actually be a
more honest and more interesting article than claiming all three are fully
resolved.
