# AgentWorld Web-Domain Test — Result Report

_This file is being written progressively as the test runs. Placeholders
marked `[PENDING]` will be filled in once the model responds._

---

## 1. What this test is

This tests whether `cryptonaut/Qwen-AgentWorld-35B-A3B-heretic` — a
community "heretic" (abliterated) fine-tune of the **official** Qwen
research model `Qwen-AgentWorld-35B-A3B` — can act as a **Web World
Model**: given a real webpage's current state and a single browser action,
predict what the page will look like *after* that action, **without ever
actually visiting the resulting page**.

This is not a made-up test. It uses the model's own official "web" domain
system prompt, verbatim, from the model's GitHub repo
(`QwenLM/Qwen-AgentWorld`, paper: arXiv 2606.24597). See
`system_prompts/web_world_model_system_prompt.txt` in this folder for the
exact text used.

## 2. Why this matters / what makes it a fair test

- The target page (`amroelhusseini.vercel.app/blog/...`) is **not** a
  known public benchmark — the model has never seen it during training,
  so this tests genuine generalization, not memorization.
- The model is asked to predict in the **same accessibility-tree
  representation** it's given (per its own format requirements) - no
  custom prompt engineering on our side beyond following its documented
  input contract.
- We compare its prediction against a **real, actually-executed** browser
  action, captured via live browser automation - not against another
  LLM's guess.

## 3. How the backend actually works (plain-English)

1. **The model is not "always on."** Featherless (the hosting platform)
   serves hundreds of community models on shared GPU capacity. Popular
   models stay "hot" (a live worker is loaded and ready); niche/rarely-used
   models like this one are `cold` most of the time, and Featherless's own
   docs confirm this: any request "loads" the model, but this can take
   "as little as 5 minutes for small models, up to an hour for larger
   ones."
2. **What a request does under the hood:** we send a normal OpenAI-style
   chat completion (`POST /v1/chat/completions`) with a `model` field
   naming the exact HF repo. Featherless's router looks up whether a GPU
   worker already has that model's weights loaded. If not, it schedules a
   load (downloading/initializing the weights onto a GPU) and, in the
   meantime, returns `503 capacity_exhausted` to any request that arrives
   before a worker is ready.
3. **Why we retry instead of failing immediately:** Featherless's own docs
   say the correct client behavior is to retry the *same* request; repeated
   503s are the visible symptom of "still loading," not a permanent error.
4. **What "the model's own context" means for the actual test:** once
   warm, our request is just text in, text out — there's no browser, no
   tool use, no image on the model's side. It only ever sees the
   accessibility-tree text we hand it and a description of an action; it
   has to *imagine* the resulting page purely from its trained
   understanding of how web UIs behave. That's the entire "world model"
   claim being tested.

## 4. Warm-up process log (this run)

- Model: `cryptonaut/Qwen-AgentWorld-35B-A3B-heretic`
- Started: `[PENDING - see warmup_result.json]`
- Total attempts before success (or budget exhaustion): `[PENDING]`
- Total elapsed time to become available: `[PENDING]`
- Full log: `warmup_*.log` in this folder

## 5. The actual test

- **Target page (before):** `https://amroelhusseini.vercel.app/blog/`
  (real accessibility-tree snapshot, saved as `snapshot_before.txt`)
- **Action tested:** `click(bid='e12')` — clicking the first blog post
  link ("Creating my Coffee Dripper, with Antigravity, Blender and MCP")
- **Real resulting page (ground truth):** captured by actually performing
  that click in a live browser, saved as `snapshot_after.txt`
- **Model's prediction:** `[PENDING - see model_prediction.txt]`

## 6. Result

`[PENDING - see test_result.json and diff_real_vs_predicted.txt]`

### Scorecard (manual checklist, since a full LLM-judge pipeline like the
official AgentWorldBench's 5-dimension scoring was out of scope for a
single demo)

| Check | Result |
|---|---|
| Predicted the correct new page title? | `[PENDING]` |
| Predicted the correct new heading? | `[PENDING]` |
| Predicted plausible new body content (even if not verbatim)? | `[PENDING]` |
| Preserved the unrelated parts of the page (nav, footer) correctly? | `[PENDING]` |
| Hallucinated anything that doesn't exist on the real page? | `[PENDING]` |
| Followed the required `<predicted_observation>` output format? | `[PENDING]` |

## 7. Files in this folder

| File | Purpose |
|---|---|
| `system_prompts/web_world_model_system_prompt.txt` | Official prompt, verbatim |
| `warmup.py` | Polls/retries Featherless until the model responds |
| `run_web_test.py` | Sends the before-state + action, parses the prediction, diffs vs. real |
| `snapshot_before.txt` | Real accessibility-tree snapshot (ground truth, pre-action) |
| `snapshot_after.txt` | Real accessibility-tree snapshot (ground truth, post-action) |
| `action.txt` | The single action tested |
| `model_prediction.txt` | The model's predicted next-page-state |
| `diff_real_vs_predicted.txt` | Unified diff: real vs. predicted |
| `test_result.json` | Structured metrics (similarity ratio, diff line count, timing) |
| `warmup_*.log` / `warmup_result.json` | Warm-up process log |
