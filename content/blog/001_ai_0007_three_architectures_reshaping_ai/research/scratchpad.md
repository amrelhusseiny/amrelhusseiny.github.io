# Scratchpad — Three Architectures Reshaping AI

Source: index.md (blog 001_ai_0007_three_architectures_reshaping_ai)
Status: COMPLETE
Last updated: 2026-07-21T05:00:00Z

## Topics
1. CEREBRAS — The Hardware Beast (wafer-scale = instant inference)
2. MERCURY 2 — The Diffusion Rebel (text as diffusion, not next-token)
3. QWEN WORLD — The Simulator (predicts consequences before acting)
+ SYNTHESIS — OpenRouter unified API

## Progress
- [x] Cerebras research
- [x] Mercury 2 research
- [x] Qwen World research
- [x] OpenRouter synthesis
- [x] Showcases built

---

## 1. CEREBRAS RESEARCH

### Core Thesis
Cerebras Systems challenges the conventional GPU-cluster approach to AI compute by building wafer-scale chips — single massive chips the size of a wafer itself — eliminating the inter-chip communication bottleneck that plagues GPU clusters. The result: inference at speeds that make real-time AI applications viable.

### The Chip: WSE-3 (Wafer Scale Engine 3)
- **Die size**: 46,225 mm² (a standard reticle-based GPU is ~800 mm² — Cerebras is ~57× larger)
- **Transistors**: 4 trillion (vs. ~208B on NVIDIA B200)
- **AI cores**: 900,000 (vs. ~18,432 CUDA cores on B200)
- **Peak performance**: 125 petaflops (FP16)
- **Memory on-chip**: 44 GB SRAM directly on the wafer (vs. HBM stacks on GPUs)
- **Memory bandwidth**: 20 PB/sec (petabytes/sec) — ~5,000× more than HBM3e on B200
- **Comparison to NVIDIA B200**: 19× more transistors, 28× more compute, and vastly more memory bandwidth

### Why Wafer-Scale Matters
The fundamental insight: in a GPU cluster, most time is spent moving data between chips (interconnect bottleneck), not computing. By putting the entire model on one wafer, Cerebras eliminates the inter-chip communication overhead. This is why they can achieve 15× faster inference than GPUs — the model never leaves the chip.

### The Yield Problem (Solved)
Historically, wafer-scale chips were considered impossible because a single defect on a wafer would ruin the whole chip. Cerebras solved this with redundant cores — if a core is defective, it's bypassed and the chip still works. This was the key engineering breakthrough that made wafer-scale viable.

### Products & Offerings
- **CS-3 System**: The compute appliance housing the WSE-3
- **Cerebras Cloud (inference.cerebras.ai)**: API access to fast inference
- **Models available on platform**: Llama-4-31B, Kimi K2.6, GLM 4.7, Codex-Spark, and others
- **Pricing**: Competitive with GPU inference but at much lower latency (sub-second time-to-first-token)

### Key Differentiators
1. **Time-to-first-token**: Sub-second, enabling real-time conversational AI
2. **Throughput**: 1000+ tokens/sec on large models (vs. ~50-100 on GPUs)
3. **Energy efficiency**: Less energy wasted on data movement
4. **Simplicity**: One chip vs. complex multi-GPU topologies

### Use Cases
- Real-time voice agents (latency-critical)
- Coding assistants (fast completions)
- Enterprise search and RAG (fast retrieval + generation)
- Interactive AI applications where GPU latency is a dealbreaker

### Sources
- cerebras.ai (homepage, inference page, chip page)
- Wikipedia: Cerebras Systems

## 2. MERCURY 2 RESEARCH

### Core Thesis
Mercury 2 by Inception Labs is the world's first reasoning diffusion LLM. Instead of generating text token-by-token (autoregressive, like GPT/Claude/Gemini), it uses diffusion-based parallel decoding — generating multiple tokens simultaneously. This challenges the entire GPT paradigm that has dominated LLMs since 2018.

### The Diffusion Difference
- **Autoregressive (GPT et al.)**: Generate token 1, then token 2 (conditioned on token 1), then token 3, etc. Inherently sequential.
- **Diffusion (Mercury 2)**: Start with noise, iteratively denoise to produce multiple tokens in parallel. Like image diffusion (Stable Diffusion) but for text.
- **Result**: 1000+ tokens/sec on standard NVIDIA GPUs — 5-10× faster than autoregressive models of similar size.

### Key Specs
- **Speed**: 1000+ tokens/sec on standard NVIDIA GPUs
- **Latency reduction**: Reasoning latency from ~3 seconds to ~300ms
- **Context window**: 128K tokens
- **Capabilities**: Reasoning, tool use, structured output, function calling
- **API**: OpenAI-compatible (drop-in replacement)

### Pricing
- Input: $0.25 / 1M tokens
- Cached input: $0.025 / 1M tokens
- Output: $0.75 / 1M tokens
- (Significantly cheaper than frontier autoregressive models)

### Use Cases
- Voice agents (sub-300ms latency enables natural conversation)
- Coding assistants (Mercury Edit 2 variant for code)
- Customer support (fast + cheap)
- Enterprise search and RAG

### Products
- **Mercury 2**: General-purpose reasoning diffusion LLM
- **Mercury Edit 2**: Coding-focused diffusion LLM
- **Platform**: platform.inceptionlabs.ai

### Team & Backing
- Founded by researchers from Stanford, UCLA, Cornell
- Team experience: Google DeepMind, Meta AI, Microsoft AI, OpenAI
- Strong academic foundation with multiple research papers

### Research Papers
- Mercury (arxiv 2506.17298) — main paper
- LaViDa (2505.16839) — latent vision diffusion
- d1 (2504.12216) — diffusion reasoning
- Block Diffusion (2503.09573) — block-level diffusion decoding

### Why It Matters
Diffusion for text was considered extremely hard because text is discrete (tokens) while diffusion works naturally on continuous spaces (images). Mercury 2's breakthrough is making diffusion work on discrete text — if this scales, it could fundamentally shift the LLM architecture landscape away from autoregressive dominance.

### Sources
- inceptionlabs.ai (homepage, blog, models page, research page)
- platform.inceptionlabs.ai

## 3. QWEN WORLD (Qwen-AgentWorld) RESEARCH

### Core Thesis
Qwen-AgentWorld is a native language world model — an LLM trained not to chat or write code, but to **simulate environments**. Given the current state of an environment and an agent's action, it predicts what the environment will return. This is predict consequences before acting — the cognitive mechanism needed for truly agentic AI.

### What It Is
- **Full name**: Qwen-AgentWorld: Language World Models for General Agents
- **Paper**: arxiv 2606.24597 (submitted June 23, 2026)
- **GitHub**: QwenLM/Qwen-AgentWorld (854 stars, Apache 2.0)
- **Blog**: qwen.ai/blog?id=qwen-agentworld
- **Released**: 2026-06-24

### Models
- **Qwen-AgentWorld-35B-A3B**: MoE, 35B total / 3B active params, 256K context (open-weight)
- **Qwen-AgentWorld-397B-A17B**: MoE, 397B total / 17B active params (larger variant)

### Seven Unified Domains
The model simulates environments across 7 agent interaction domains in a single model:
1. **MCP** (Model Context Protocol — tool use)
2. **Search** (web/information retrieval)
3. **Terminal** (Linux command line)
4. **SWE** (software engineering — code repos)
5. **Android** (mobile device interaction)
6. **Web** (browser automation)
7. **OS** (operating system interaction)

### Three-Stage Training Pipeline
1. **CPT (Continual Pre-Training)**: Injects general-purpose world modeling capabilities from state transition dynamics and augmented professional corpora
2. **SFT (Supervised Fine-Tuning)**: Activates next-state-prediction reasoning
3. **RL (Reinforcement Learning)**: Sharpens simulation fidelity through hybrid rubric-and-rule rewards
- Trained on 10M+ real-world interaction trajectories across 7 domains

### Key Innovation: Native World Model
Unlike prior approaches that treat world modeling as a post-hoc add-on, Qwen-AgentWorld is a **native world model** — environment modeling is the training objective from the CPT stage onward. This is the fundamental difference.

### Performance (AgentWorldBench)
Qwen-AgentWorld-397B-A17B achieves the highest overall score (58.71), outperforming:
- GPT-5.4 (58.25)
- Claude Opus 4.6 (57.80)
- Claude Opus 4.8 (56.59)
- Claude Sonnet 4.6 (56.04)
- Gemini 3.1 Pro (54.57)
- DeepSeek-V4-Pro (52.97)
- GLM-5.1 (51.31)

Qwen-AgentWorld-35B-A3B (56.39) shows +8.66 improvement over Qwen3.5-35B-A3B (47.73) without LWM training.

### Two Paradigms for Agent Enhancement
1. **As a decoupled environment simulator**: Supports scalable, controllable simulation of thousands of real-world environments for agentic RL. Training in simulated environments **surpasses** training in real environments alone.
   - Sim RL on 4k OOD OpenClaw environments: +4.3 Claw-Eval, +7.1 QwenClawBench
   - Controlled perturbations (MCP): +12.3 MCPMark
   - Fictional-world construction (Search): +16.29 F1 Item improvement

2. **As a unified agent foundation model**: World-model training acts as a highly effective warm-up that improves downstream performance across 7 agentic benchmarks.
   - Terminal-Bench 2.0: +6.30
   - SWE-Bench Verified: +3.39
   - SWE-Bench Pro: +5.24
   - WideSearch F1 Item: +12.79
   - BFCL v4: +8.96

### AgentWorldBench
- Comprehensive benchmark from real-world interactions of 5 frontier models on 9 established benchmarks
- Evaluates on 5 dimensions: Format, Factuality, Consistency, Realism, Quality
- Open-source on HuggingFace

### Why It Matters
This is the path to truly agentic AI. Current agents act blindly — they try actions and observe results. With a world model, an agent can **imagine** the consequences of its actions before executing them, then choose the best action. This is analogous to how humans think through consequences before acting. Qwen-AgentWorld makes this practical by showing that:
1. A single model can simulate 7 different environment types
2. Training in simulated environments can beat training in real environments
3. World-model training transfers to better agent performance

### Deployment
- Supported by SGLang and vLLM
- OpenAI-compatible API
- Domain-specific system prompt templates for all 7 domains
- HuggingFace: Qwen/Qwen-AgentWorld-35B-A3B

### Sources
- arxiv.org/abs/2606.24597 (paper)
- github.com/QwenLM/Qwen-AgentWorld (code, README, benchmarks)
- qwen.ai/blog?id=qwen-agentworld (blog)
- huggingface.co/Qwen (model weights)
---

## 4. SHOWCASE RECOMMENDATIONS

### 4a. CEREBRAS -- The Hardware Beast (Wafer-Scale = Instant Inference)

**Showcase Type:** Interactive side-by-side latency race (visual comparison dashboard)

**What it would show:**
A real-time animated "race" between Cerebras and a standard GPU-hosted model serving the same prompt. The reader types a prompt or selects a preset, then watches two progress bars race -- Cerebras finishes in a fraction of the time. Below the race, a hardware-comparison diagram (not to scale, metaphorical) shows the size contrast: a tiny GPU die vs. the wafer-scale chip (57x larger), with animated data-flow arrows showing inter-chip communication on the GPU side vs. zero-chip-hops on Cerebras.

**How it could be built:**
- Two OpenAI-compatible API calls in parallel (one to openrouter.ai targeting a Cerebras-hosted model like cerebras/llama-3.1-8b, one to openrouter.ai targeting the same model on a GPU provider like octoai/llama-3.1-8b). Timing measured client-side with performance.now() / Date.now().
- Frontend: A single HTML page with vanilla JS or a framework like Astro/Next.js (consistent with the Hugo-based blog). Uses fetch() to both endpoints, renders two animated progress bars, and records time-to-first-token + total tokens/sec.
- Diagram: SVG/CSS-animated comparison chart showing GPU cluster with interconnects vs. single wafer-scale chip. Could use D3.js or pure SVG animation.
- Data needed: The reader needs an OpenRouter API key (or the blog author pre-loads demo results as fallback GIF/video). If running live, requires a credits-loaded OpenRouter account. Fallback: pre-recorded results shown as an auto-playing video/GIF comparison.

**Key insight to highlight:** Time-to-first-token goes from seconds (GPU) to sub-second (Cerebras). The reader feels the difference, not just reads about it.

---

### 4b. MERCURY 2 -- The Diffusion Rebel (Text as Diffusion, Not Next-Token)

**Showcase Type:** Generative process visualization with token-unfolding animation

**What it would show:**
A split-panel animation contrasting autoregressive generation (GPT-style: tokens appear one by one, left to right) vs. diffusion generation (Mercury 2 style: a block of "noisy" placeholder tokens refines into coherent text in parallel). The user submits a prompt and both generate the same response -- the autoregressive side shows token-by-token typing, while the diffusion side shows blocks of text "snapping into focus" simultaneously. A speed counter shows tokens/sec for each. Below: an animated explanatory diagram showing the diffusion process at a conceptual level -- noise -> partial text -> refined text.

**How it could be built:**
- API calls: Two parallel calls via OpenRouter -- one to inception/mercury-2 (diffusion), one to any autoregressive model of comparable capability (e.g., openai/gpt-4o-mini).
- Frontend rendering: The diffusion side is the interesting part. Mercury 2 streams tokens, but since diffusion works on blocks, the visual presentation could simulate the "block refinement" effect: show a block of gray/placeholder text that resolves into real words, then a second pass improves it. This can be done by rendering the streamed content with CSS transitions that reveal/refine character blocks.
- Diagram: An SVG animation depicting the diffusion process -- (1) input prompt -> (2) noise/token cloud -> (3) iterative denoising steps -> (4) coherent output. Tools: SVG + CSS animations, or Lottie for pre-built animation.
- Data needed: OpenRouter API key with access to Mercury 2 model. The diffusion visualization is primarily conceptual -- actual Mercury 2 API still streams tokens (it doesn't expose intermediate diffusion states), so the block-refinement effect is a pedagogical visualization, not literal.

**Key insight to highlight:** The paradigm shift -- from "think one word at a time" (autoregressive) to "think in parallel, then refine" (diffusion). The speed difference (1000+ vs ~50-100 tok/s) is the emotional hook.

---

### 4c. QWEN WORLD -- The Simulator (Predicts Consequences Before Acting)

**Showcase Type:** Interactive "what-if" simulator with prediction-vs-reality comparison

**What it would show:**
Three panels side by side:
1. Action selector: User picks an agent action from a dropdown (e.g., "run git status in a dirty repo", "search for climate change statistics 2026", "open Android calculator app").
2. Prediction panel: Qwen-AgentWorld simulates what the environment will return -- shows the predicted terminal output, search results, or system response.
3. Reality panel: A real agent (or pre-recorded real environment response) shows what actually happened.

Below the panels, a side-by-side diff highlighting where the world model got it right and where it diverged. A score meter shows "simulation fidelity" -- how well the world model's prediction matched reality.

**How it could be built:**
- HuggingFace Inference API or self-hosted endpoint running Qwen-AgentWorld-35B-A3B via SGLang/vLLM. The model is open-weight (Apache 2.0), so it can be deployed on any GPU server.
- The 7 domain-specific system prompt templates are provided in the Qwen-AgentWorld repo (prompts/{domain}/system_prompt.txt). Each prompt configures the model for a specific environment domain (Terminal, SWE, Search, MCP, Android, Web, OS).
- For "reality" comparison: Pre-recorded ground-truth environment responses from the AgentWorldBench dataset can be loaded. For a truly live demo, the "reality" panel calls a real tool/API (e.g., actual bash in a sandbox, actual web search API).
- Frontend: Tabbed interface for the 7 domains, with preset scenarios per domain. Terminal domain is the easiest to demo -- run a real shell command in a Docker sandbox for the "reality" side and compare against Qwen-AgentWorld's prediction.
- Libraries: SGLang or vLLM for model serving, HuggingFace Transformers for inference, Docker for sandboxed command execution. Frontend: vanilla JS or React/Vue for the comparison UI with diff highlighting (using a library like diff or jsdiff).
- Data needed: ~70GB+ GPU VRAM to run Qwen-AgentWorld-35B-A3B (4x A100 or equivalent). Alternatively, use a hosted API if one becomes available through OpenRouter or HuggingFace Inference Endpoints.

**Key insight to highlight:** The model doesn't just answer questions -- it imagines consequences. This is the cognitive leap from "reactive agent" to "planning agent." The diff between prediction and reality is the money shot.

---

### 4d. SYNTHESIS -- OpenRouter: One API, Radically Different Brains

**Showcase Type:** "Unified router" interactive picker -- same prompt, three architectures, three results

**What it would show:**
A single text input. One "Send" button. Three simultaneous responses from three different architectures, each going through OpenRouter's unified API:
- Cerebras column: Speed-optimized, blazing-fast inference, time-to-first-token highlighted.
- Mercury 2 column: Diffusion-powered, high-throughput parallel generation, tokens/sec highlighted.
- Qwen World column: Environment simulation -- the model doesn't just answer, it predicts what would happen if you acted on the answer. (For Qwen World, the prompt is framed as an agent action: "Given this state and action, predict the environment observation...")

Each response is annotated with: architecture type, provider name, time-to-first-token, tokens/sec, and a one-line summary of the architectural difference.

**How it could be built:**
- OpenRouter API: Three parallel calls to three model slugs (e.g., cerebras/llama-3.1-8b, inception/mercury-2, and Qwen-AgentWorld via either a custom provider on OpenRouter or a self-hosted endpoint). All use the same OpenAI-compatible POST /v1/chat/completions format.
- Frontend: Clean dashboard with three columns, color-coded to each architecture (Cerebras = orange/amber for hardware, Mercury = blue/cyan for diffusion, Qwen = green for world simulation). Response cards expand as they stream. Each card has architecture-specific metrics visible.
- Cost comparison: A small cost-counter accumulates in real-time for each model, showing the reader that different architectures have dramatically different cost profiles for the same task.
- Libraries: OpenRouter SDK (JS or Python) on the backend, or direct fetch() calls if client-side only. No special libraries needed -- OpenRouter's OpenAI compatibility is the key enabler.

**Key insight to highlight:** The blog's thesis made concrete -- one API key, one endpoint format, three fundamentally different ways of computing intelligence. The reader can literally see that "thinking" has multiple paths.

---

## 5. IMPLEMENTATION NOTES FOR THE BLOG AUTHOR

### Recommended priority order for building showcases:
1. SYNTHESIS (OpenRouter picker) -- highest impact, pulls all three topics together, technically simplest (just 3 API calls), can be built entirely client-side with OpenRouter.
2. CEREBRAS race -- second simplest (2 parallel API calls), high visual impact, reinforces the "instant inference" claim.
3. MERCURY 2 diffusion visualization -- requires creative frontend work for the block-refinement animation but the API integration is straightforward.
4. QWEN WORLD simulator -- most complex (requires GPU inference or hosted endpoint for the open-weight model), but also the most unique and academically substantive showcase.

### Common infrastructure:
- All showcases can share a single OpenRouter API key.
- All can be embedded as static HTML/JS widgets within the Hugo blog post (Hugo supports raw HTML in markdown).
- For readers without an API key: provide pre-recorded demos as GIF/MP4 fallbacks.
- Credential management: use a serverless function (e.g., Cloudflare Worker, Vercel Edge Function) as a proxy to avoid exposing the API key in client-side code, or use OpenRouter's OAuth PKCE flow for user-managed keys.

### Alternative: "Demo mode" approach
Instead of requiring reader API keys, the blog author runs each showcase once, records the results, and embeds the visualizations as auto-playing comparisons. This is simpler for the reader and avoids API key logistics, but loses the interactivity of "type your own prompt."

### Visualization tool recommendations:
- Animated diagrams/conceptual illustrations: D3.js, SVG + CSS animations, or Motion (Framer Motion if using React)
- Comparison charts/race animations: Chart.js with animation plugin, or custom canvas/SVG
- Code comparison/diff views: Prism.js or Shiki for syntax highlighting + a diff library
- Terminal simulation: xterm.js (for Qwen World terminal domain)
- Pre-built animations: Lottie (After Effects to Lottie JSON) for high-quality explanatory animations

---

Last updated: 2026-07-21T05:00:00Z

TASK_COMPLETE
