---
marp: true
theme: uncover
class:
  - lead
  - invert
paginate: true
size: 16:9
style: |
  section.lead h1 {
    font-size: 2.4em;
  }
  section.lead h2 {
    font-size: 1.4em;
    color: #aaa;
  }
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  h2 {
    color: #ff6b35;
    border-bottom: 3px solid #ff6b35;
    padding-bottom: 0.3em;
  }
  h3 {
    color: #00b4d8;
  }
  table {
    margin: 0 auto;
    font-size: 0.8em;
  }
  th {
    background: #ff6b35;
    color: white;
    padding: 8px 14px;
  }
  td {
    padding: 6px 14px;
    border-bottom: 1px solid #444;
  }
  .columns {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .columns3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
  }
  .box {
    border: 2px solid #555;
    border-radius: 12px;
    padding: 1em;
    margin: 0.5em 0;
  }
  .box-orange {
    border-color: #ff6b35;
  }
  .box-blue {
    border-color: #00b4d8;
  }
  .box-green {
    border-color: #2ecc71;
  }
  .big-number {
    font-size: 3em;
    font-weight: bold;
    color: #ff6b35;
  }
  small {
    color: #888;
  }
  ul {
    text-align: left;
  }
  li {
    margin: 0.3em 0;
  }
---

# Three Architectures
# Reshaping AI

**Cerebras · Mercury 2 · Qwen World**

_Speed. Diffusion. Simulation._

---

## The Status Quo

<div class="columns">
<div>

### How We Build AI Today

- GPU clusters — the default for a decade
- Autoregressive models — one token at a time
- Reactive agents — try, observe, try again

</div>
<div>

### The Problems

- **Latency** kills real-time applications
- **Sequential** generation caps throughput
- **Blind** agents can't think ahead

</div>
</div>

---

## Meet the Three Rebels

<div class="columns3">
<div class="box box-orange">

### 🖥️ Cerebras
**Hardware Beast**

Wafer-scale chips —
no inter-chip bottleneck

</div>
<div class="box box-blue">

### 🌊 Mercury 2
**Diffusion Rebel**

Parallel text generation —
not one token at a time

</div>
<div class="box box-green">

### 🧠 Qwen World
**The Simulator**

Predicts consequences
before acting

</div>
</div>

---

# CEREBRAS
## The Hardware Beast

---

## The WSE-3 Wafer-Scale Engine

<div class="big-number">57×</div>
Larger than a standard GPU die

| Metric | WSE-3 | NVIDIA B200 |
|---|---|---|
| **Die size** | 46,225 mm² | ~800 mm² |
| **Transistors** | **4 trillion** | 208 billion |
| **AI cores** | **900,000** | 18,432 CUDA |
| **Memory BW** | **20 PB/s** | ~4 TB/s (HBM3e) |
| **Peak perf** | 125 PF (FP16) | — |

---

## Why Wafer-Scale Matters

<div class="columns">
<div>

### GPU Cluster
```
GPU₁ ↔ GPU₂ ↔ GPU₃
 ↕      ↕      ↕
GPU₄ ↔ GPU₅ ↔ GPU₆
```
- Data spends most time **moving**, not computing
- Interconnect is the bottleneck

</div>
<div>

### Wafer-Scale
```
┌────────────────────┐
│                    │
│   ONE MASSIVE DIE  │
│    (model on-chip) │
│                    │
└────────────────────┘
```
- Zero inter-chip hops
- Sub-second time-to-first-token
- **1000+ tokens/sec**

</div>
</div>

---

## The Yield Problem — Solved

> *"A single defect on a wafer would ruin the whole chip."*

**Cerebras solution:** Redundant cores — defective ones are bypassed.

This was the **key engineering breakthrough** that made wafer-scale viable.

---

## Cerebras: Key Numbers

<div class="columns3">
<div>

### 🚀 Speed
**15× faster** inference vs GPUs

**1000+ tok/s** on large models

</div>
<div>

### ⚡ Latency
**Sub-second** time-to-first-token

Real-time voice agents become viable

</div>
<div>

### 🔋 Efficiency
Less energy wasted on data movement

One chip vs complex multi-GPU topologies

</div>
</div>

**Models on platform:** Llama-4-31B, Kimi K2.6, GLM 4.7, Codex-Spark, and more

---

# MERCURY 2
## The Diffusion Rebel

---

## The Paradigm Shift

<div class="columns">
<div>

### Autoregressive (GPT et al.)
```
Token₁ → Token₂ → Token₃ → Token₄
```
- **Sequential** — each token depends on the previous
- ~50–100 tokens/sec
- Inherent latency floor

</div>
<div>

### Diffusion (Mercury 2)
```
        ┌─ Token₁ ─┐
Noise → ┼─ Token₂ ─┼→ Refined text
        └─ Token₃ ─┘
```
- **Parallel** — multiple tokens generated simultaneously
- **1000+ tokens/sec**
- Like Stable Diffusion — but for text

</div>
</div>

---

## Mercury 2 Specs

| Capability | Detail |
|---|---|
| **Speed** | 1000+ tok/s on standard GPUs |
| **Latency** | ~3s → **~300ms** (reasoning) |
| **Context** | 128K tokens |
| **API** | OpenAI-compatible (drop-in) |
| **Capabilities** | Reasoning, tool use, structured output, function calling |

<div class="box box-blue">

### Pricing
- Input: **$0.25/M** · Cached: **$0.025/M** · Output: **$0.75/M**
- Significantly cheaper than frontier autoregressive models

</div>

---

## Products & Research

<div class="columns">
<div>

### Models
- **Mercury 2** — general-purpose reasoning
- **Mercury Edit 2** — coding-focused

**Team:** Stanford, UCLA, Cornell → Google DeepMind, Meta AI, OpenAI

</div>
<div>

### Published Papers
- **Mercury** — arxiv 2506.17298
- **d1** — diffusion reasoning (2504.12216)
- **Block Diffusion** — block-level decoding (2503.09573)
- **LaViDa** — latent vision diffusion (2505.16839)

</div>
</div>

---

## Why Text Diffusion Was Hard

> *"Text is discrete — diffusion works naturally on continuous spaces (images)."*

| Images | Text |
|---|---|
| Continuous pixels | Discrete tokens |
| Natural for denoising | No "partially correct" token |

**Mercury 2's breakthrough:** Making diffusion work on discrete text.

If this scales → **fundamental shift** away from autoregressive dominance.

---

# QWEN WORLD
## The Simulator

---

## What Is Qwen-AgentWorld?

> *"A language model trained not to chat or write code — but to **simulate environments**."*

Given a **state** + an **action**, it predicts what the environment will return.

**Paper:** arxiv 2606.24597 · **Released:** 2026-06-24 · **License:** Apache 2.0

<div class="box box-green">

### Two Model Sizes
- **Qwen-AgentWorld-35B-A3B** — MoE, 3B active params, 256K context (open-weight)
- **Qwen-AgentWorld-397B-A17B** — MoE, 17B active params (larger variant)

</div>

---

## Seven Unified Domains

A **single model** simulates environments across 7 agent interaction domains:

<div class="columns">
<div>

1. 🔧 **MCP** — Model Context Protocol / tool use
2. 🔍 **Search** — web/information retrieval
3. 💻 **Terminal** — Linux command line
4. 🛠️ **SWE** — software engineering repos

</div>
<div>

5. 📱 **Android** — mobile device interaction
6. 🌐 **Web** — browser automation
7. 🖥️ **OS** — operating system interaction

</div>
</div>

---

## Three-Stage Training

| Stage | What | Goal |
|---|---|---|
| **1. CPT** | Continual Pre-Training | Inject world-modeling capabilities from state-transition data |
| **2. SFT** | Supervised Fine-Tuning | Activate next-state-prediction reasoning |
| **3. RL** | Reinforcement Learning | Sharpen fidelity via hybrid rubric + rule rewards |

Trained on **10M+ real-world interaction trajectories** across all 7 domains.

**Key innovation:** World modeling is the training objective from CPT stage onward — not a post-hoc add-on.

---

## Beats Frontier Models at World Modeling

**AgentWorldBench** — comprehensive benchmark from 5 frontier models on 9 benchmarks:

| Model | Score |
|---|---|
| **Qwen-AgentWorld-397B-A17B** | **58.71** 🥇 |
| GPT-5.4 | 58.25 |
| Claude Opus 4.6 | 57.80 |
| Claude Opus 4.8 | 56.59 |
| Claude Sonnet 4.6 | 56.04 |
| Gemini 3.1 Pro | 54.57 |
| DeepSeek-V4-Pro | 52.97 |
| GLM-5.1 | 51.31 |

*Qwen-AgentWorld-35B-A3B: 56.39* (vs. 47.73 without LWM training → **+8.66**)

---

## Two Paradigms for Agent Enhancement

<div class="columns">
<div class="box box-green">

### 1. Decoupled Environment Simulator
Training in simulated environments **surpasses** training in real ones:
- Sim RL (4k OOD environments): **+4.3** Claw-Eval
- Controlled perturbations (MCP): **+12.3** MCPMark
- Fictional-world construction (Search): **+16.29** F1 Item

</div>
<div class="box box-green">

### 2. Unified Agent Foundation Model
World-model training as warm-up improves downstream performance:
- Terminal-Bench 2.0: **+6.30**
- SWE-Bench Verified: **+3.39**
- SWE-Bench Pro: **+5.24**
- WideSearch F1 Item: **+12.79**
- BFCL v4: **+8.96**

</div>
</div>

---

## Why It Matters

<div class="columns">
<div>

### Today: Reactive Agents
```
Try action → Observe → Try again
```
Agents act **blindly** — no ability to think ahead.

</div>
<div>

### Tomorrow: Planning Agents
```
Imagine → Evaluate → Choose → Act
```
With a world model, an agent can **simulate consequences** before execution.

</div>
</div>

> *"This is the cognitive leap from reactive to planning agents."*

---

# SYNTHESIS
## One API · Three Brains

---

## OpenRouter: The Unifying Layer

```
┌──────────────────────────────────────┐
│           OPENROUTER API              │
│    POST /v1/chat/completions          │
│    (OpenAI-compatible)                │
├──────────┬───────────┬───────────────┤
│ Cerebras │ Mercury 2 │ Qwen World    │
│  (fast)  │(diffusion)│ (simulation)  │
└──────────┴───────────┴───────────────┘
```

**One API key. One endpoint format. Three radically different ways of computing intelligence.**

---

## The Synthesis Dashboard

<div class="columns3">
<div class="box box-orange">

### 🖥️ Cerebras
**Speed Wins**

- Time-to-first-token: **sub-200ms**
- Throughput: **1000+ tok/s**
- Best for: real-time voice, coding

</div>
<div class="box box-blue">

### 🌊 Mercury 2
**Parallel Wins**

- Tokens/sec: **1000+**
- Latency: **~300ms**
- Best for: bulk reasoning, cheap output

</div>
<div class="box box-green">

### 🧠 Qwen World
**Prediction Wins**

- Environment simulation
- Consequence modeling
- Best for: planning, agentic workflows

</div>
</div>

**One prompt → Three columns → Three fundamentally different answers**

---

## The Tradeoffs at a Glance

| | Cerebras | Mercury 2 | Qwen World |
|---|---|---|---|
| **Core idea** | Wafer-scale hardware | Diffusion for text | World simulation |
| **Speed** | Sub-second TTFT | 1000+ tok/s | N/A (batch) |
| **Paradigm** | Hardware innovation | Algorithmic innovation | Training innovation |
| **Cost** | Competitive w/ GPU | $0.25/$0.75 per M | Self-host (open-weight) |
| **Best for** | Real-time interaction | High-throughput gen | Agentic planning |

---

## Why Three Architectures, Not One

> *"We're entering an era where 'the best model' depends on **what you're building**."*

- **Real-time voice agent?** → Cerebras (sub-second latency)
- **Bulk content generation?** → Mercury 2 (1000+ tok/s, cheap)
- **Complex agentic system?** → Qwen World (predict, then act)

The future is **multi-architecture** — and OpenRouter makes it seamless.

---

## The Big Picture

<div class="columns">
<div>

### Old World
- One architecture (Transformer)
- One training paradigm (autoregressive)
- One deployment pattern (GPU cluster)
- One optimization target (perplexity)

</div>
<div>

### New World
- **Wafer-scale chips** for instant inference
- **Diffusion models** for parallel generation
- **World models** for consequence prediction
- **Unified APIs** bridging architectures

</div>
</div>

<br>

## The era of architectural diversity has begun.

---

## Where to Learn More

| Topic | Links |
|---|---|
| **Cerebras** | cerebras.ai · inference.cerebras.ai |
| **Mercury 2** | inceptionlabs.ai · platform.inceptionlabs.ai |
| **Qwen World** | github.com/QwenLM/Qwen-AgentWorld · qwen.ai/blog |
| **OpenRouter** | openrouter.ai |
| **Papers** | arxiv: 2506.17298, 2503.09573, 2606.24597 |

---

# Thank You

*Three architectures. One API. The future of AI is multi-paradigm.*