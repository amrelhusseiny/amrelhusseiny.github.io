# AgentWorld Web-Domain Test — Result Report

Real test, real website, real result. This document explains what was
tested, exactly how the backend mechanics work, and what actually
happened — including the messy parts.

---

## 1. What this test is

This tests whether `cryptonaut/Qwen-AgentWorld-35B-A3B-heretic` — a
community "heretic" (abliterated, refusal-training-removed) fine-tune of
the **official** Qwen research model `Qwen-AgentWorld-35B-A3B` — can act
as a **Web World Model**: given a real webpage's current state and a
single browser action, predict what the page will look like *after* that
action, **without ever actually visiting the resulting page**.

This is not an invented test. It uses the model's own official "web"
domain system prompt, verbatim, copied from the model's GitHub repo
(`QwenLM/Qwen-AgentWorld`, paper: arXiv 2606.24597, "Qwen-AgentWorld:
Language World Models for General Agents"). The exact text used is in
`system_prompts/web_world_model_system_prompt.txt` in this folder.

**Key discovery that made this test possible:** `Qwen-AgentWorld-35B-A3B`
is not a randomly-named community model — it's the *official* name given
by the Qwen research team to a model specifically trained to be a
language world model across 7 domains (mcp, search, terminal, swe,
android, web, os). The Featherless-hosted `cryptonaut/...-heretic` variant
is a fine-tune of that exact official model, so its official system
prompts and action-space definitions apply directly.

## 2. Why this is a fair/interesting test

- The target page (`amroelhusseini.vercel.app/blog/...`) is **not** a
  known public benchmark — the model has never seen it during training.
  This tests genuine generalization to a novel website, not memorization
  of a benchmark it may have trained on.
- The model was asked to predict in the **same accessibility-tree
  representation** it was given, per its own documented format
  requirements — no custom prompt engineering beyond following the
  official input contract.
- The comparison is against a **real, actually-executed** browser action
  (via live browser automation), not against another LLM's guess.

## 3. How the backend actually works (what happened, mechanically)

### 3.1 Featherless's model lifecycle: cold / loading / warm

Featherless (the hosting platform) serves hundreds of community models on
shared GPU capacity. Per Featherless's own docs
(`featherless.ai/docs/api-reference-error-codes`), every model is in one
of three states:

- **warm** — a GPU worker already has the model loaded; instant inference.
- **loading** — a worker is in the process of loading the model's weights.
- **cold** — nobody has requested this model recently; no worker has it
  loaded.

This model is tagged `"niche": true` in Featherless's catalog, meaning
it's not kept hot continuously. **Any API request is also what triggers a
cold model to start loading** — there's no separate "load" button/endpoint
we're required to call first; requesting the model IS the load trigger.
While loading (or when capacity is contended), Featherless returns
`HTTP 503 {"code": "capacity_exhausted"}`. Their documented client
guidance: **retry the identical request**; if it still fails after 3
retries, treat the model class as temporarily unavailable. Documented
warm-up time: "as little as 5 minutes for small models, up to an hour for
larger ones" — this is a 35B-parameter model, so the longer end of that
range was plausible going in.

### 3.2 What actually happened, timeline

| Step | Result |
|---|---|
| First warm-up attempt | `503` after 14.6s |
| Attempts 2-18 | All `503`, ~13-29s each, retried every 20s |
| **Attempt 19** | **SUCCESS** — model responded "OK" in 13.77s |
| **Total time to first successful response** | **652.8 seconds (~10.9 minutes)** |
| Immediately tried the real test | `503` again within seconds — the warm window was extremely brief |
| Real test, attempt 1 (max_tokens=4000) | Succeeded in 245.9s, but **ran out of tokens mid-reasoning** (see 3.3) |
| Real test, retry with max_tokens=16000 | 2 more `503`s, then **succeeded in 346.55s** on the 3rd attempt (5,292 completion tokens used) |

Full logs: `warmup_20260809_145748.log`, `run_test_stdout.log`,
`run_test_stdout2.log`.

**Practical takeaway:** this specific niche model has very brief, heavily
contended warm windows (seconds, not minutes) — even right after a
successful warm-up ping, the very next real request went cold again. The
working strategy that got a usable result was: retry the *actual* request
itself (not just a ping) repeatedly, with a generous per-request timeout,
until one lands during a window when a worker is both loaded *and* has
spare concurrency.

### 3.3 The model "thinks" out loud, and that costs tokens

The `cryptonaut` "heretic" variant is a reasoning-enabled fine-tune — it
produces a long, visible chain-of-thought before its final answer (no
`<think>` tag hiding it; it's just plain text reasoning followed by the
`<predicted_observation>` block). On the **first attempt** (max_tokens
capped at 4,000), the model spent the *entire* budget reasoning out loud
and got cut off before ever emitting the closing tag — technically a
format-compliance failure (`format_compliant: false`), but the visible
reasoning was actually track: it correctly worked out, in its own words,
that the predicted title should be *"Creating my Coffee Dripper, with
Antigravity, Blender and MCP // Amro's Blog"* — which turned out to be
**an exact match to the real page title**. It simply ran out of tokens
before formatting that correct answer into the required tag. Raised to
16,000 tokens, the second run completed properly (5,292 completion tokens
used) with a valid `<predicted_observation>` block.

**This is itself a real, reportable finding**: a reasoning-tuned world
model needs meaningfully more output budget than a typical instruct model
for the same task, because a chunk of the budget goes to visible
deliberation before the actual answer.

## 4. The actual test

- **Target page (before):** `https://amroelhusseini.vercel.app/blog/`
  — real accessibility-tree snapshot, `snapshot_before.txt` (1,021 chars,
  2 blog post links visible)
- **Action tested:** `click(bid='e12')` — clicking the first blog post
  link, whose visible (truncated) text was *"Creating my Coffee Dripper,
  with Antigravity, Blender and MCP Intro From non Blender user, to 3d
  Pri…"*
- **Real resulting page (ground truth):** captured by actually performing
  that click in a live browser — `snapshot_after.txt` (5,716 chars, the
  full real article page)
- **Model's prediction:** `model_prediction.txt` (890 chars, extracted
  from the `<predicted_observation>` block in `model_raw_response_final.txt`)

## 5. Result

### Quantitative

| Metric | Value |
|---|---|
| Format compliance (valid `<predicted_observation>` tag) | ✅ Yes (on the 16k-token run) |
| Real page length | 5,716 chars |
| Predicted page length | 890 chars |
| Character-level similarity ratio (`difflib.SequenceMatcher`) | 0.2355 |
| Diff lines (added/removed) | 100 |
| Total tokens used (final successful call) | 6,518 (1,226 prompt + 5,292 completion) |

The raw similarity number (~24%) sounds unimpressive in isolation, but
the qualitative diff (below) tells a much more interesting story than
the number alone.

### Qualitative — what it got right vs. wrong

**Correct:**
- **Exact page title match**, including the site's `// Amro's Blog`
  suffix convention: `"Creating my Coffee Dripper, with Antigravity,
  Blender and MCP // Amro's Blog"`.
- **Correctly preserved every untouched element verbatim** — the entire
  nav bar (Blog/Notes/About/CV, Light mode button, GitHub/LinkedIn links)
  and the footer links, exactly matching the real post-click page. This
  is precisely the "preserve untouched subtrees verbatim" instruction
  from the system prompt, followed correctly.
- **Correctly inferred the page-type transition** (list page → article
  page) and produced a plausible `article` / `heading` structure matching
  the real page's actual top-level structure.
- **Correctly predicted the visible `h1` heading** — again an exact
  string match to the real page: `"Creating my Coffee Dripper, with
  Antigravity, Blender and MCP"`.
- **Correctly used the only clue it had** — the truncated preview text
  from the link's accessible name (*"...Intro From non Blender user, to
  3d Pri"*) — to open the article body with a paragraph starting "Intro
  From non Blender user, to 3d Printer...", which is a reasonable, honest
  extrapolation rather than a fabrication.

**Incorrect / incomplete:**
- **URL slug guessed wrong**: predicted
  `/blog/creating-my-coffee-dripper-with-antigravity-blender-and-mcp/`
  (a sensible title-based slugification) vs. the real
  `/blog/001_ai_0003_ai_generated_functional_prints/` (this site actually
  uses internal numbered codenames as slugs, not title-derived slugs —
  arguably unguessable without prior knowledge of the site's specific
  convention).
- **Did not invent the actual article body** — the real article is ~90
  lines long (full prose, numbered lists, a JSON config snippet, ~7
  images, a References section). The model produced a single short
  placeholder paragraph instead. **Notably, it did not hallucinate fake
  specific content** (no invented image filenames, no fabricated code, no
  made-up references) — it gave a short, honest, generic continuation
  rather than confidently making things up. Whether that's "good"
  (honest under uncertainty) or "bad" (incomplete/low-value prediction)
  depends on what you want a world model for.
- Missing structural details the real page has: byline ("November 20,
  2025 · 2 min read"), a `#ai` tag link, a "Table of Contents" element,
  and a title image.

### Scorecard

| Check | Result |
|---|---|
| Predicted the correct new page title? | ✅ Exact match |
| Predicted the correct new heading? | ✅ Exact match |
| Predicted plausible new body content (even if not verbatim)? | ⚠️ Partial — plausible opening, but far shorter than reality and missing most real sections |
| Preserved the unrelated parts of the page (nav, footer) correctly? | ✅ Verbatim match |
| Hallucinated anything that doesn't exist on the real page? | ❌ No fabricated specifics detected — it under-generated rather than confabulated |
| Followed the required `<predicted_observation>` output format? | ✅ Yes, on the properly-budgeted run (16k tokens); ❌ failed on the first attempt (4k tokens, ran out of budget mid-reasoning) |

## 6. Overall take

This is a genuinely useful result for the article precisely *because* it's
mixed. The model demonstrates real structural/navigational world-modeling:
it gets page identity, titles, headings, and untouched-subtree
preservation exactly right — the "boring but correct" parts a naive
pattern-matcher might get wrong. Where it falls short is unknowable
specific content (the actual unique article text), which is arguably an
unfair ask for *any* model, human included, without visiting the page.
The interesting nuance is that it fails safely — by writing less rather
than fabricating more.

Separately, the operational story (very niche/cold model, ~11 minutes to
first response, retries needed even after warming up, chain-of-thought
eating the token budget) is itself worth a paragraph or two in the
article — it's an honest, unglamorous part of working with long-tail
open-weight models that's rarely shown in cleaner benchmark write-ups.

## 7. Files in this folder

| File | Purpose |
|---|---|
| `system_prompts/web_world_model_system_prompt.txt` | Official prompt, verbatim |
| `warmup.py` | Polls/retries Featherless until the model responds to a lightweight ping |
| `run_web_test.py` | Sends the before-state + action (with internal retry-until-success), parses the prediction, diffs vs. real |
| `snapshot_before.txt` | Real accessibility-tree snapshot (ground truth, pre-action) |
| `snapshot_after.txt` | Real accessibility-tree snapshot (ground truth, post-action) |
| `action.txt` | The single action tested: `click(bid='e12')` |
| `model_prediction.txt` | The model's predicted next-page-state (extracted) |
| `model_raw_response_final.txt` | Full raw response including visible chain-of-thought |
| `model_raw_response_first_attempt_truncated.txt` | The first (4k-token) attempt that ran out of budget mid-reasoning — kept as evidence for the token-budget finding |
| `diff_real_vs_predicted.txt` | Unified diff: real vs. predicted |
| `test_result.json` | Structured metrics (similarity ratio, diff line count, timing, token usage) |
| `warmup_*.log`, `warmup_result.json` | Warm-up process log |
| `run_test_stdout*.log` | Full stdout from both test attempts |
