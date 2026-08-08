---
date: 2026-07-21T20:36:00Z
title: "Full Duplex Voice Models"
description: "Notes on full duplex voice models — Kyutai Labs' Moshi, OpenAI's GPT Live, and the Unmute CLI. How speech-to-speech models compare to cascade ASR+LLM+TTS pipelines."
draft: true
---

Full duplex voice AI is the new paradigm behind recent voice assistant launches — OpenAI's
ChatGPT Live, Thinking Machines' interaction models, and Kyutai's Moshi. Unlike traditional
voice assistants that operate in a strict turn-taking fashion (you speak, then it speaks),
full duplex models can **listen and speak simultaneously**, enabling natural conversational
dynamics like interruptions, interjections, and overlapping speech — much closer to how real
human conversation works.

---

## The Problem with Cascade Systems

Traditional voice assistants (including the original ChatGPT voice mode) use a **cascade
pipeline**: Voice Activity Detection (VAD) → Automatic Speech Recognition (ASR) → Text LLM →
Text-to-Speech (TTS). This approach has three fundamental limitations:

1. **High latency** — Each stage adds delay, resulting in several seconds between the user
   finishing a sentence and the assistant starting to respond.
2. **Loss of non-linguistic information** — Since text is the intermediate modality, emotion,
   tone, accents, and non-speech sounds are stripped out. The model can't "hear" *how* you
   said something.
3. **Rigid turn-taking** — The system segments conversation into discrete speaker turns. It
   cannot handle interruptions, overlapping speech, or quick interjections like "yeah", "uh
   huh", or "wait".

---

## Moshi — The First Real-Time Full-Duplex Spoken LLM

[Moshi](https://github.com/kyutai-labs/moshi), developed by [Kyutai](https://kyutai.org/)
(a non-profit AI research lab in Paris), is the first real-time full-duplex spoken dialogue
model. It was open-sourced in late 2024 along with its research paper
([arXiv:2410.00037](https://arxiv.org/abs/2410.00037)).

### Architecture

Moshi casts spoken dialogue as **speech-to-speech generation**. Instead of converting speech
to text first, it works directly with audio tokens:

- **Two parallel audio streams** — Moshi models two streams simultaneously: one for its own
  speech output and one for the user's speech input. At inference time, the user's stream is
  taken from the audio input, and Moshi's stream is sampled from the model's output. This
  removes explicit speaker turns entirely.
- **Inner Monologue** — Along with the audio streams, Moshi predicts text tokens corresponding
  to its own speech. This "inner monologue" acts as a time-aligned prefix to the audio tokens,
  significantly improving the linguistic quality of generated speech. As a side benefit, it
  provides streaming ASR and TTS for free.
- **Mimi codec** — Moshi uses [Mimi](https://github.com/kyutai-labs/moshi), a streaming
  neural audio codec that processes 24 kHz audio down to a **12.5 Hz** representation at just
  **1.1 kbps**, with an 80 ms frame-level latency. Mimi adds Transformers in both the encoder
  and decoder (building on SoundStream and EnCodec), uses a WavLM distillation loss so the
  first codebook captures semantic information, and relies solely on adversarial training with
  feature matching.
- **Dual Transformer design** — A small **Depth Transformer** models inter-codebook
  dependencies at each time step, while a large **7B-parameter Temporal Transformer** handles
  temporal dependencies across time.

### Latency

- **Theoretical latency: 160 ms** (80 ms Mimi frame size + 80 ms acoustic delay)
- **Practical latency: ~200 ms** on an L4 GPU

This is a dramatic improvement over cascade systems that typically incur several seconds of
delay.

### Model Variants & Implementations

Kyutai released three models under **CC-BY 4.0**: Moshiko (male voice), Moshika (female
voice), and Mimi (the codec). The codebase provides three inference backends:

| Backend | Use case | Language | Quantization |
|---------|----------|----------|--------------|
| **PyTorch** | Research & tinkering | Python | bf16, int8 (needs ~24GB VRAM) |
| **MLX** | On-device (iPhone/Mac) | Python | int4, int8, bf16 |
| **Rust/Candle** | Production | Rust | int8, bf16 |

The Rust backend with CUDA (or Metal on macOS) is recommended for production deployments.

### Related Kyutai Models

- **Hibiki** — simultaneous speech translation using a similar multi-stream architecture
- **Delayed Streams Modeling** — Kyutai's standalone STT and TTS models (used by Unmute)

---

## OpenAI GPT Live

OpenAI's [GPT Live](https://openai.com/index/introducing-gpt-live/) represents the
commercial manifestation of full duplex voice AI — the "Her" experience (referencing the
Spike Jonze film). It moved away from the cascade approach of the original ChatGPT Advanced
Voice Mode toward an end-to-end speech model that can handle real-time, interruptible,
emotionally expressive conversation.

Key characteristics as discussed in the community and demonstrated by OpenAI:

- **End-to-end speech modeling** — rather than ASR → LLM → TTS, the model processes and
  generates audio directly, preserving emotional tone and non-verbal cues.
- **Barge-in / interruption support** — users can interrupt the assistant mid-sentence, and
  the model responds naturally, just like a human would.
- **Emotional expressiveness** — the model can convey and respond to emotion, pacing, and
  tone because it never reduces the conversation to plain text.

> **Note:** The OpenAI page was not directly accessible from this environment (blocked by a
> web filter), so the above is summarized from the referenced video discussion and publicly
> available information. The YouTube video *"How far are we from 'Her'?"* provides a good
> comparative analysis of GPT Live alongside Moshi and Thinking Machines' interaction models.

---

## Unmute — Open-Source Voice for Any Text LLM

[Unmute](https://github.com/kyutai-labs/unmute), also from Kyutai, takes a different and
pragmatic approach. Rather than training an end-to-end speech-to-speech model, it **wraps any
existing text LLM** with Kyutai's low-latency STT and TTS models. You can try it live at
[unmute.sh](https://unmute.sh).

### How It Works

```
User Browser → Backend → [STT → LLM → TTS] → Audio back to user
```

1. The user's browser sends audio over a WebSocket connection to the backend.
2. The backend streams audio to the **Speech-to-Text** server for real-time transcription.
3. When the user stops speaking, the backend queries an **LLM** (via OpenRouter, vLLM, Ollama,
   or any OpenAI-compatible server) for a response.
4. As the text response streams in, it's fed to the **Text-to-Speech** server and the
   generated audio is sent back to the user.

### Key Properties

- **Model-agnostic** — works with any text LLM. Default local setup uses Gemma 3 1B;
  production uses GPT OSS 120B via OpenRouter. You can swap in any OpenAI-compatible endpoint.
- **Low latency but not full-duplex** — Unmute is a cascade system (STT → LLM → TTS), so it
  doesn't do simultaneous listening/speaking. It's optimized for low latency within that
  paradigm. Multi-GPU setups (separate GPUs for STT, TTS, LLM) reduce TTS latency from ~750 ms
  to ~450 ms.
- **OpenAI Realtime API compatibility** — the backend/frontend protocol is based on the
  OpenAI Realtime API (ORA), with some extensions. The goal is a single frontend that can talk
  to either Unmute or OpenAI's Realtime API.
- **Tool calling** — not yet built-in; the recommended approach is to handle it inside the LLM
  server layer (e.g., a FastAPI wrapper around vLLM) so it's invisible to Unmute itself.

### Deployment

- **Docker Compose** (recommended) — single command, needs 1+ CUDA GPU with ≥16 GB VRAM
- **Dockerless** — manual service startup, 1–3 GPUs across 1–5 machines
- **Docker Swarm** — production scaling (how unmute.sh itself is deployed)

Requirements: Linux or WSL (no native Windows or macOS support), x86_64 only, CUDA 12.1+.

---

## Cascade vs. End-to-End: The Trade-off

| | Cascade (ASR + LLM + TTS) | End-to-End Speech-to-Speech |
|---|---|---|
| **Latency** | Higher (seconds) | Lower (Moshi: ~200 ms) |
| **Non-verbal info** | Lost (text bottleneck) | Preserved (emotion, tone) |
| **Interruptions** | Hard / awkward | Natural (full duplex) |
| **Interjections** | Not supported | Supported ("yeah", "uh huh") |
| **LLM flexibility** | Any text LLM (Unmute) | Needs dedicated speech model |
| **Tool calling** | Trivial (text domain) | Harder, still maturing |
| **Cost / compute** | Composable, cheaper | Single large model, pricier |
| **Open source** | Unmute (Apache/MIT) | Moshi (MIT/Apache, CC-BY weights) |

The core tension: end-to-end models like Moshi deliver the "Her" experience but are
expensive, harder to control, and less flexible. Cascade systems like Unmute are cheaper and
more flexible but can't do true full-duplex conversation. As noted in the video, **tool
calling in full-duplex models** remains an open challenge — it's trivial in text/cascade
systems but requires new approaches when the model operates purely in audio space.

---

## Why Aren't Full-Duplex Models Everywhere Yet?

Despite Moshi being open-sourced, full-duplex voice AI hasn't gone mainstream. The reasons
discussed:

- **Compute cost** — running a 7B speech model in real-time requires significant GPU resources
  (24 GB+ VRAM for PyTorch Moshi).
- **Controllability** — text LLMs can be steered with prompts, system messages, and tools.
  Speech-to-speech models are harder to constrain — you can't easily insert a "system prompt"
  in audio.
- **Evaluation** — measuring quality of generated speech (especially emotion, naturalness,
  correctness) is harder than evaluating text.
- **Tool use & RAG** — integrating external knowledge or tool calls into an audio-native model
  is an active research area (Moshi RAG: [arXiv:2604.12928](https://arxiv.org/abs/2604.12928)).

---

## Verdict

We're getting close to "Her", but not there yet. Moshi proved that real-time full-duplex
spoken dialogue is feasible at ~200 ms latency with an open-source model. OpenAI's GPT Live
brought the experience to consumers. Unmute offers a pragmatic middle ground — open-source,
model-agnostic, but fundamentally still a cascade. The next frontier is combining the
naturalness of end-to-end speech models with the controllability and tool-use capabilities of
text LLMs.

---

## References

- [Moshi — GitHub (kyutai-labs/moshi)](https://github.com/kyutai-labs/moshi) — open-source full-duplex speech-text foundation model
- [Moshi paper (arXiv:2410.00037)](https://arxiv.org/abs/2410.00037) — "Moshi: a speech-text foundation model for real-time dialogue"
- [How far are we from "Her"? — YouTube](https://www.youtube.com/watch?v=kOD9rMhn4f4) — video discussion of full duplex models with Moshi founder Neil Zeghidour
- [OpenAI — Introducing GPT Live](https://openai.com/index/introducing-gpt-live/) — OpenAI's announcement of full-duplex voice mode
- [Unmute — GitHub (kyutai-labs/unmute)](https://github.com/kyutai-labs/unmute) — open-source voice wrapper for any text LLM
- [Moshi RAG paper (arXiv:2604.12928)](https://arxiv.org/abs/2604.12928) — retrieval-augmented generation for full-duplex models
- [Thinking Machines — Interaction Models](https://thinkingmachines.ai/blog/interaction-models/) — multi-stream voice interaction design
- [Kyutai Delayed Streams Modeling](https://github.com/kyutai-labs/delayed-streams-modeling) — standalone Kyutai STT/TTS models used by Unmute