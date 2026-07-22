# Research: Cisco Antares — Open-Weight SLMs for Vulnerability Localization

> Research notes compiled for the post `index.md`. All facts sourced from the
> Cisco blog announcement and the Hugging Face model cards (links at the bottom).
> Scraped locally via Puppeteer + stealth plugin.

## 1. What Antares is

Antares is a family of **security small language models (SLMs)** from **Cisco Foundation AI** (Hugging Face org: `fdtn-ai`), purpose-built for one task: **vulnerability localization** — pinpointing *which source files* in a codebase contain a known vulnerability.

- Announced in the Cisco blog on **July 21, 2026**.
- Author: **Amin Karbasi** (VP & Chief AI Scientist, Foundation AI), with a long list of collaborators (Supriti Vijay, Aman Priyanshu, Didier Chapoteau, Arthur Goldblatt, Kimia Majd, Fraser Burch, Jianliang He, Baturay Saglam, Takahiro Matsumoto, Zhuoran Yang, …).
- **Two models released as open-weight on Hugging Face:**
  - `fdtn-ai/antares-350m` — 350M params
  - `fdtn-ai/antares-1b` — 1B params
- **Antares-3B is "coming soon"** — not yet on Hugging Face (confirmed by the org page listing only the two above).
- **License: Apache 2.0.**
- Base model: **IBM Granite 4.0** (350M and 1B backbones respectively). This is confirmed in the model cards and the HF model tree (`ibm-granite/granite-4.0-1b-base` → `granite-4.0-1b` → `antares-1b`).

## 2. The problem it solves

Software security depends on connecting **external vulnerability knowledge** (public DBs, advisories, CWEs) to **internal code**. That work is hard because:

- repositories are large,
- security signals are noisy,
- the relevant evidence is rarely in one obvious place.

Analysts must search unfamiliar code, follow naming conventions, inspect call paths, compare candidate files, and decide whether a weakness is actually present. Traditional **static analysis** is rule-heavy and produces noisy results needing triage. **General-purpose coding models** can reason about code but aren't optimized for security investigation, terminal navigation, or structured vulnerability localization. Antares targets that **middle ground**.

## 3. How it works — terminal agent, not a chatbot

Antares operates as a **terminal agent**. It does **not** retrieve CVEs from memory or query the internet. Instead, given a **CWE identifier + its generic category description** and a repository, it:

1. Starts from the vulnerability description.
2. Issues **shell commands** (`grep`, `find`, `cat`, standard Unix utilities) against a read-only repository snapshot.
3. Reads the output, reasons about it, and decides the next command.
4. Changes direction when a path is unproductive.
5. Narrows toward the files most likely to contain the vulnerability.
6. Terminates by calling either `submit_vulnerable_files` (list of file paths) or `submit_no_vulnerability_found`.

- **Budget: up to 15 terminal calls** per task, then one final submission action.
- Uses a **structured tool-calling format**: an internal reasoning block followed by a tool-call block; the sandbox output is appended as a tool-result message before the next turn.
- **Output:** a ranked list of source files likely to be vulnerable, **plus the terminal exploration trace** that led there.
- It **localizes** vulnerable files — it does **not** generate exploits or explain *why* a file is vulnerable. Internal reasoning guides the search but is not surfaced as an explanation.

This design was inspired by Cisco Foundation AI research showing that **compact models can learn to search, reflect, revise strategy, and backtrack** — i.e., useful retrieval behavior can come from **learned search strategies, not only from model scale**.

## 4. The Antares CLI

To support adoption, Cisco ships the **Antares CLI** as a **ZIP file in the `antares-1b` repository's Files section** on Hugging Face.

- Packages the **complete Antares agent loop**.
- Runs analyses over a **read-only repository snapshot**.
- Connects to a **user-configured OpenAI-compatible inference endpoint** (this is the key detail for the post's sandbox: vLLM exposes an OpenAI-compatible `/v1/chat/completions` API, and Ollama can serve the model locally).
- Supports:
  - **targeted CWE analyses**, and
  - **repository-wide sweeps**.
- Returns candidate vulnerable files in **human-readable, JSON, or SARIF** formats for analyst review.

## 5. Training

Two-stage pipeline, identical recipe for the whole family:

**Stage 1 — Supervised Fine-Tuning (SFT)** on a proprietary corpus across three categories:
1. cybersecurity reasoning (vulnerability concepts, CWE/CVE reasoning, threat modeling, advisory interpretation, security analysis),
2. deep-research and general reasoning (multi-step reasoning, evidence aggregation, instruction following),
3. code-search trajectories (terminal-based repository exploration, file inspection, iterative search).

**Stage 2 — GRPO (Group Relative Policy Optimization)** — reinforcement learning over **complete multi-turn agent trajectories** using vulnerable repository snapshots curated through proprietary data-generation/filtering pipelines. Each task includes a complete codebase with a known vulnerability and ground-truth labels (the affected implementation files). Rewards are **multi-component and verifiable**: file-level localization quality, valid submission behavior, tool-use compliance, and exploration behavior.

- Optimizer: **AdamW**.
- Compute: **8× H100 GPUs** on Cisco Foundation AI's internal cluster.
- **Data cutoff: April 10, 2025.** Static model trained on an offline dataset; future versions will use updated data.

## 6. Model architecture details

| | Antares-350M | Antares-1B |
|---|---|---|
| Base | IBM Granite 4.0 350M | IBM Granite 4.0 1B |
| Layers | 28 | 40 |
| Hidden dim | 1024 | 2048 |
| Attention heads | 16 | 16 |
| KV heads (GQA) | 4 | 4 |
| Context window | 32K | 128K |
| Vocab | 100,352 | 100,352 |
| Activation | SwiGLU | SwiGLU |
| Norm | RMSNorm | RMSNorm |
| Positional encoding | RoPE | RoPE |
| On-disk (BF16) | — | ~2B params |

Both are auto-regressive decoder-only transformers.

## 7. Evaluation — VLoc Bench (Vulnerability Localization Benchmark)

Cisco built a new benchmark because general coding benchmarks (SWE-Bench Verified/Pro/Lite, used by the adjacent **CodeScout** work) measure whether an agent can find code relevant to a *software issue/dev task*, not whether it can localize vulnerable files from CWE-style security descriptions.

**VLoc Bench:**
- **500 tasks** drawn from **290 unique real-world repositories**.
- **6 package ecosystems**, **147 unique CWE categories**.
- **78% of entries carry assigned CVE identifiers.**
- Each entry = a repository snapshot **reconstructed at the pre-fix commit**, paired with ground-truth files (those modified in the actual security fix PR, excluding tests, docs, and config).
- The agent gets **only a generic CWE category description** — no advisory text, no file hints, no severity.
- Budget: **15 terminal commands** + one final submission.
- **Metric: File F1** — harmonic mean of task-level precision and recall. Precision = fraction of submitted files in ground truth; recall = fraction of ground-truth files submitted. A task with no valid submission scores zero. Macro-averaged across 500 tasks, then averaged across **3 independent runs**.
- Generation settings: `temperature=0.3`, `top_p=1.0`.

### Leaderboard (Phase A — File F1)

| Model | Params | File F1 ↑ | Precision | Recall |
|---|---|---|---|---|
| GPT-5.5 (xhigh) | Frontier | 0.229 | 0.310 | 0.221 |
| **Antares-3B (GRPO)** | 3B | 0.223 | 0.303 | 0.221 |
| GPT-5.5 | Frontier | 0.221 | 0.305 | 0.211 |
| **Antares-1B (GRPO)** | 1B | 0.209 | 0.262 | 0.224 |
| Antares-3B (SFT) | 3B | 0.198 | 0.240 | 0.228 |
| Antares-1B (SFT) | 1B | 0.188 | 0.263 | 0.179 |
| GLM-5.2 | 753B | 0.186 | 0.226 | 0.186 |
| Gemini 3 Pro | Frontier | 0.152 | 0.190 | 0.153 |
| **Antares-350M (GRPO)** | 350M | 0.135 | 0.136 | 0.178 |
| Antares-350M (SFT) | 350M | 0.108 | 0.149 | 0.101 |
| Gemini 2.5 Flash | Frontier | 0.102 | 0.132 | 0.098 |
| Gemma-4-31B | 31B | 0.101 | 0.131 | 0.097 |
| GPT-5 Mini | Frontier | 0.098 | 0.115 | 0.096 |
| Gemini 3.1 Flash Lite | Frontier | 0.095 | 0.131 | 0.090 |
| Qwen3.5-122B-A10B | 125B MoE | 0.091 | 0.124 | 0.083 |
| GPT-5 | Frontier | 0.048 | 0.062 | 0.048 |
| GPT-5 Nano | Frontier | 0.024 | 0.038 | 0.021 |
| Llama-3.3-70B | 70B | 0.012 | 0.016 | 0.014 |
| Granite 4.0 1B (base) | 1B | 0.000 | — | — |

**Takeaways:**
- The 1B Antares beats GLM-5.2 (753B), Gemini 3 Pro, GPT-5 Mini, Qwen3.5-122B, GPT-5, Llama-3.3-70B — all many times its size.
- The 350M beats Gemini 2.5 Flash, Gemma-4-31B, GPT-5 Mini, Qwen3.5-122B.
- The untrained Granite 4.0 1B base scores **0.000** — i.e., the localization ability comes entirely from the Antares training, not the base model.
- GRPO consistently beats SFT within each size (1B: 0.209 vs 0.188; 350M: 0.135 vs 0.108; 3B: 0.223 vs 0.198).

### Throughput
- **Antares-1B** completes the full 500-task VLoc Bench sweep in **~13 minutes** on a **single H100 GPU** with 16 parallel workers.
- **Antares-350M** does it in **~11 minutes** on the same setup.

## 8. The 350M as a speculative draft model

Within the family, **Antares-350M can serve as a speculative draft model** for the larger 1B/3B variants: it proposes candidate tokens that the larger model verifies, **accelerating inference while preserving the larger model's localization quality**. It can also run standalone in resource-constrained deployments.

## 9. Intended use cases

- **Vulnerability localization** from a CWE identifier + generic category description.
- **Shift-left security** — integrate into CI/CD to surface vulnerable files early; both models run on a single GPU.
- **Advisory-driven triage** — use CWE identifiers (including those mapped from CVE or GHSA records) to guide multi-step terminal exploration.
- **Local deployment** for data security, regulatory compliance, and operational control — code never leaves the machine.

### Out of scope
- Generating malware / phishing / attack plans.
- Critical security decisions without human oversight.
- Legal or medical advice.
- **General-purpose chat or instruction following** — it's specifically trained for terminal-based vulnerability localization and may not perform well on general tasks.
- Standalone safety evaluation (e.g., HarmBench) — it's meant to run inside an agentic terminal loop, not as a chat assistant.

## 10. Limitations

- **Terminal budget:** performance degrades on large repos (>10MB) where 15 commands are insufficient; multi-file vulnerabilities needing 5+ files of context underperform.
- **Pattern dependence:** best on vulnerability types with distinctive, grep-able code patterns (e.g., CWE-843 Type Confusion, CWE-1321 Prototype Pollution). Poor on CWEs requiring semantic understanding (e.g., CWE-732 Incorrect Permissions, CWE-667 Improper Locking, CWE-401 Memory Leak).
- **Knowledge cutoff (April 10, 2025):** may not recognize vulnerabilities/patterns introduced after that date.
- **No exploitation functionality:** localizes files only; no PoC exploits, no explanation of *why*.
- **No external retrieval:** requires no vector database, but performance is bounded by the quality of its terminal exploration within the command budget.
- **Potential biases** toward vulnerability types/languages prevalent in training data.
- **Security risks:** cannot verify user identity/intent; adversarial prompting may bypass safety if exposed without system-level guardrails.

## 11. Safety & deployment recommendations

No standalone RLHF/HarmBench alignment was performed — safety is meant to be handled **at the system level**:

- Run the agent inside an **isolated sandbox** (e.g., Docker container with `network=none`).
- **Command timeout** (10 seconds recommended).
- **Resource limits** (2 CPU cores, 4GB RAM).
- **Destroy the container after each evaluation entry.**
- System-level **access controls** restricting use to authorized security personnel.
- **Human oversight** over outputs before any remediation action.
- Monitoring/auditing of agent trajectories in high-risk workflows.

## 12. The broader Cisco ecosystem

Antares is one piece of a larger Cisco effort:

- **Foundry Security Spec** — a model-agnostic blueprint for building agentic security evaluation systems (clear roles, guardrails, reviewable outputs).
- **CodeGuard** — secure-by-default rules and skills that guide AI coding agents toward safer software development.
- **Antares** — compact security models + the VLoc Bench benchmark for repository-level vulnerability localization.

The stated goal: move AI in security beyond one-off demos toward systems practitioners can **evaluate, govern, and improve** — open specs, reusable security knowledge, compact deployable models, and measurable benchmarks.

## 13. How to run it (relevant to the post's sandbox)

From the HF model card, the supported serving paths:

- **vLLM** (OpenAI-compatible API — this is what the Antares CLI expects):
  ```bash
  pip install vllm
  vllm serve "fdtn-ai/antares-1b"
  # then call http://localhost:8000/v1/chat/completions (OpenAI-compatible)
  ```
- **SGLang** (also OpenAI-compatible).
- **Transformers** direct load (`AutoModelForCausalLM`).
- **Docker Model Runner:** `docker model run hf.co/fdtn-ai/antares-1b`.
- Quantizations available for **llama.cpp / Ollama / LM Studio**.

The **Antares CLI** connects to any user-configured **OpenAI-compatible endpoint**, which is why the post's setup (Ollama serving the model locally + a vLLM-style endpoint for the CLI to talk to) works.

> Note: the model repos are gated — you must request access and agree to share contact info before downloading weights.

## 14. Corrections to the current `index.md` draft

- The draft says "4B version" — **incorrect**. The released sizes are **350M and 1B**; the **3B** is the one "coming soon" and is not on Hugging Face yet.
- "trained on the existing [CVEs]" — more precisely: trained via SFT + GRPO on **vulnerable repository snapshots with ground-truth file labels** (data cutoff Apr 10 2025). It **localizes** from CWE descriptions using a terminal; it does **not** look up CVEs from memory or need internet access.
- Base model = IBM Granite 4.0 — **confirmed correct**.
- The vLLM-adaptor detail is right: the CLI talks to an **OpenAI-compatible** endpoint, and vLLM exposes exactly that.

## References

- Cisco blog: <https://blogs.cisco.com/ai/introducing-antares-the-most-efficient-open-weight-ai-models-for-vulnerability-localization>
- Antares-1B on Hugging Face: <https://huggingface.co/fdtn-ai/antares-1b>
- Antares-350M on Hugging Face: <https://huggingface.co/fdtn-ai/antares-350m>
- Cisco Foundation AI org on HF: <https://huggingface.co/fdtn-ai>
- Technical report (cited in model card): Vijay, Priyanshu, et al. *"Antares: Foundation Models for Agentic Vulnerability Localization."* Foundation AI, Cisco, 2026.
- Model card contact: <https://fdtn.ai/contact>