# Scratchpad — 001-first-note (Cisco Antares CVE detection post)

## Current state of index.md
- Front matter: date + title only ("Cisco released Fine tuned Models for CVE detection"). No draft/toc/tags yet.
- Body: short intro about Cisco Antares SLMs (based on IBM Granite 4.0), 350M + 4B variants on HF, 3B coming. Runs locally, no internet needed. Author tested via Ollama + vLLM adaptor sandbox, asked about a known Cisco ISE CVE.
- One Mermaid diagram (handDrawn look, custom themeVariables pastel colors) showing antares-net docker network: antares-ollama + antares-cli container (CLI + cloned repo).
- References: Cisco blog + HF antares-1b page.

## Site conventions (from existing blog posts)
- Front matter: title, date, draft, toc, tags.
- Mermaid: %%{init: {'look':'handDrawn','theme':'base','themeVariables':{...pastel...}}}%% flowchart.
- Sections: ## numbered or named. Personal first-person tone.
- References section at end with bullet links.

## Task
- Generate a research markdown file with all details findable about the Antares project.
- Give user a summary of what the post can say.

## TODO / Open questions
- Verify exact model variant sizes (post says 350M & 4B; HF link says antares-1b). Need to confirm.
- Confirm base model = IBM Granite 4.0? (post says Granite 4.0).
- Find Cisco blog details, HF model card details, CLI usage, vLLM endpoint format.

## Research findings (via local Puppeteer + stealth)
### Cisco blog (blogs.cisco.com/ai/...antares...)
- Published July 21, 2026. Author: Amin Karbasi (VP & Chief AI Scientist, Foundation AI). Many collaborators.
- Antares = family of security SLMs for VULNERABILITY LOCALIZATION (pinpointing where known vulns exist in a codebase).
- Releasing Antares-350M and Antares-1B as open-weight on HF. Antares-3B coming soon.
- Outperform many larger closed/open models at fraction of cost; compact enough to run locally (no sending code to cloud).
- Part of broader Cisco effort: Antares (models) + Foundry Security Spec (open spec for agentic security eval) + CodeGuard (secure coding rules/skills) + new Vulnerability Localization Benchmark.
- Inspired by Cisco Foundation AI research: compact models can learn to search/reflect/revise/backtrack. Learned search strategies, not just scale.
- Iterative search pattern like a human investigator: start from vuln description -> search code patterns -> read candidate files -> incorporate evidence -> change direction -> narrow to likely files.
- Outputs: ranked list of source files likely vulnerable + terminal exploration trace.
- Use cases: locate files for a CWE category; triage advisory-driven investigations; augment static analysis; CI/CD triage; local analysis w/ privacy/compliance.
- NOT a replacement for full AppSec toolchain (SCA, secret scanning, DAST, container checks, threat modeling, remediation, expert review).
- Quotes: Reza Shokri (NUS), Amin Saberi (Stanford).

### HF model card: fdtn-ai/antares-1b
- Built on IBM Granite 4.0 1B. Apache 2.0. Org: Cisco Foundation AI (fdtn-ai).
- Architecture: auto-regressive decoder-only transformer, 40 layers, hidden 2048, 16 attn heads, 4 KV heads (GQA), 128K context, 100,352 vocab, SwiGLU, RMSNorm, RoPE. BF16, ~2B params on disk.
- Training: two-stage SFT -> GRPO. SFT data: cybersecurity reasoning, deep-research/reasoning, code-search trajectories. GRPO over full multi-turn agent trajectories w/ multi-component verifiable rewards (file-level localization quality, valid submission, tool-use compliance, exploration behavior). 8xH100 GPUs, AdamW.
- Data cutoff: April 10, 2025. Static model.
- Operates as a TERMINAL AGENT: up to 15 terminal calls, then submit_vulnerable_files or submit_no_vulnerability_found. Uses grep/find/cat/Unix. Structured tool-calling format (reasoning block + tool call block).
- Antares CLI: provided as ZIP in the repo Files section. Packages full agent loop, runs over read-only repo snapshot, connects to user-configured OpenAI-compatible inference endpoint. Supports targeted CWE analyses + repo-wide sweeps. Output: human-readable, JSON, or SARIF.
- Eval: VLoc Bench = 500 tasks, 290 unique real-world repos, 6 package ecosystems, 147 unique CWE categories, 78% entries have CVE IDs. Repo snapshot reconstructed at pre-fix commit; ground truth = files modified in actual security fix PR (excl tests/docs/config). Metric: File F1 (harmonic mean of precision/recall), macro-averaged over 500 tasks, averaged over 3 runs. temp=0.3, top_p=1.0.
- Antares-1B File F1 = 0.209. Beats GLM-5.2 (753B, 0.186), Gemini 3 Pro (0.152), GPT-5 Mini (0.098), Qwen3.5-122B (0.091), GPT-5 (0.048), Llama-3.3-70B (0.012). Granite 4.0 1B base = 0.000.
- Top of leaderboard: GPT-5.5 xhigh 0.229, Antares-3B (GRPO) 0.223, GPT-5.5 0.221, then Antares-1B 0.209.
- 1B completes full 500-task sweep in ~13 min on single H100 w/ 16 parallel workers.
- Limitations: degrades on repos >10MB (15 cmds insufficient); multi-file vulns needing 5+ files underperform; best on grep-able pattern CWEs (CWE-843, CWE-1321), poor on semantic CWEs (CWE-732, CWE-667, CWE-401); no exploit generation, only localization; knowledge cutoff.
- Safety: no standalone RLHF/HarmBench; system-level safeguards (sandbox Docker network=none, 10s cmd timeout, 2 CPU/4GB RAM limits, destroy container after each entry).

### HF model card: fdtn-ai/antares-350m
- Built on IBM Granite 4.0 350M. 28 layers, hidden 1024, 16 attn heads, 4 KV heads (GQA), 32K context, 100,352 vocab, SwiGLU, RMSNorm, RoPE.
- File F1 = 0.135. Beats Gemini 2.5 Flash (0.102), Gemma-4-31B (0.101), GPT-5 Mini (0.098), Qwen3.5-122B (0.091).
- Can serve as SPECULATIVE DRAFT model for 1B/3B (proposes tokens, larger model verifies). Also runs standalone in constrained deployments.
- Completes 500-task sweep in ~11 min on single H100, 16 workers.

### Org page (fdtn-ai)
- Only antares-350m and antares-1b public. 3B NOT on HF yet (confirms post). Also has Foundation-Sec-8B models.

### Corrections to current index.md
- Post says '4B version' -> WRONG. Should be 1B (and 350M). 3B coming.
- Base model IBM Granite 4.0 -> CONFIRMED correct.
- 'trained on existing CVEs' -> more precise: trained via SFT+GRPO on vulnerable repo snapshots with ground-truth files; data cutoff Apr 10 2025. It localizes from CWE descriptions, doesn't look up CVEs from memory.
- vLLM adaptor note: CLI connects to OpenAI-compatible endpoint (vLLM serves OpenAI-compatible API). Ollama provides local serving.

## Next steps
- Write research.md (full details) to note_dir.
- Give user summary of what the post can say.

## DONE
- research.md written to note_dir (15KB, 14 sections + references + leaderboard table).
- Covers: what Antares is, problem, terminal-agent design, CLI, training (SFT+GRPO), architecture table, VLoc Bench + full leaderboard, 350M as speculative draft, intended use, limitations, safety/deployment, broader Cisco ecosystem, how to run, corrections to current draft.
- Awaiting user direction on whether to expand index.md into a full post using this research.
