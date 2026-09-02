---
title: "Two Architectures Reshaping AI"
date: 2026-08-09T00:00:00Z
draft: false
toc: true
tags:
    - ai
---

Things are moving too fast in the AI space, but the more you get into it, the more you get optimistinc, most of the industry is morphing into alike archeticture by the big labs, OpenAI, Anthropic and Google specially when it comes to inference at scale, but there are more exciting developments elsewhere.

The mostly deployed archeticture, and pardon me , every word of these has a lot meaning to it , something like GPT 4 is a *(1)Decoder Only / (2)Auto regerssive / (3)Transformer model* running on general purpose GPU 

Speed is the key we talk about, demonstrated by the folllowing diagram, dont worry , we will showcase in detail what each of these represent.

Diagram shows the speed comparison between:

1. Cerebras -> Topic No 1.
2. Mercurey -> Topic No 2.
3. Deepinfra ( GPT-OSS 120B ) -> Everyday Auto Regressive Decoder Model.

![race_comparison_v2](/blog/001_ai_0007_three_architectures_reshaping_ai/race_comparison_v2.gif)

## Cerebras , *GPU vs WSE*

> [!NOTE]
>
> During writing of this article, Cerbras have released its new CS-4 chip, but it wont be our scope, however the same concepts here apply.

![image-20260811085039313](/blog/001_ai_0007_three_architectures_reshaping_ai/image-20260811085039313.png)

We already know what GPUs (Graphical Processing Units *- Nvidia,AMD, etc*) are , but WSE (Wafer Scale Enging) uses a 300mm diameter silicon wafer, instead of cutting the Wafer into smaller chips, it just uses the whole thing,

The only limitation previously that these wafer must always have defects, and the manufacturarers workaround was to take the good parts of the wafer and produce the small chips / chiplets (like Nvidea GPUs),

But what Cerebras introduced instead is an algorithm that will disable the cores where these defects exist, so they can always use the whole wafer.

Second feature they added is instead having SRAM ( This is a memory that is even faster than norml HBM VRAM ) shared by all the GPU Cores, on the WSE, each core comes bundled with its SRAM, 

1st the limitation of that is that, Cerebras's WSE can only run a selected number of models and very hard to scale up or out, for now they were onlyn able to offer the following models (As of Aug 2026) :

  - ZAI GLM 4.7
 - OpenAI GPT OSS 120B
 - Google DeepMind Gemma 4 31B

So nothing frontier, but what they lack in size they make up for in Tok/sec, following is a live test using Openrouter's Endpoint for Cerebras / DeepInfra Models to show the diffirence between GPU and WSE inferencing :

| Model        | Cerebras (WSE) | DeepInfra (Nvedea GPU) | Multiplier      |
| ------------ | -------------- | ---------------------- | --------------- |
| gpt-oss-120b | 1,262.4 tok/s  | 12.55 tok/s            | **101× slower** |
| Gemma 4 31B  | 1,040.4 tok/s  | 63.74 tok/s            | **16× slower**  |
| GLM 4.7      | 437.1 tok/s    | 33.08 tok/s            | **13× slower**  |

![cerebras_vs_deepinfra_all_models](/blog/001_ai_0007_three_architectures_reshaping_ai/cerebras_vs_deepinfra_all_models.gif) 

## Mercury 2 , Auto Regression (ARM) vs Text Diffusion*

> [!NOTE]
>
> While working on this article, Inception have released Mercury 2.5 whis is an enhanced version, however all the tests carried out here were on version 2, but the same functionality applies to both.

One of the limitation well known about Auto Regressive models, that they are very sequential, which make it very limited and not in support of parallelism in Pre Training and Post training , Pos training has been the dominate power for the last 3 years, and is responsible for most of the gains we have in the new models, however since its being limiited by the AR (Auto Regressive) models ability to parallelize , then comes, Diffusion Models.

Text diffusion is evolved out of Image diffusion, where its being used extensively, instead of Auto Regressive Models (ARM) which predict the next token, lets say word for now, based on the previous words, 

Diffusion works by generating a paragraph of text with a predetermined size, like 256 Token in Google's Gemma case, these are random words at 1st, by generating noise , (Following is a real Run with Inception's Mercurey 2 model with their trial API Key, which you cabn get @  https://platform.inceptionlabs.ai/auth/login?callbackUrl=/ ), with the "diffusing": true key , you can see the noising and denoising happening in realtime , here is the **Forward Diffusion - Noising** :

![diffusion_noising_mercury](/blog/001_ai_0007_three_architectures_reshaping_ai/diffusion_noising_mercury.gif)

Then **Reverse Diffusion - Denoising**, this makes the 2 paths : 

![diffusion_denoising_mercury](/blog/001_ai_0007_three_architectures_reshaping_ai/diffusion_denoising_mercury.gif)

Another part of the text diffusion models, since it has a full paragraph of tokens, that it iterats on , all at once, then its able to see the future and the past tokens, unlike Auto Regressions where it only looks at past tokens to prdict the future ones, 

In text diffusion, the model will look once in forward path , and once in backwards *(Bidirectional Reasoning / Self correction)*, in order to predicta token, so this gives it more versatility, since it runs 2 way to predict the token (this is where predicting from past and future at the same time) .

The model can also do in place editing , just like image diffusion, since it can see all the tokens before and after, its able to idnetify what do you need to edit in text, and only fix/update those tokens, instead of having to regenerate the whole answer again jsut to fix the part you need.

Low latency is another advantage, where it can jam < To Continue >

Also with auto regressions, once it produces a token, it cannot take it back , unlike Diffusion, which can change an earlier value if it sees it was previoulsy wrong.

Limitations with Diffusion models, first is it requires 16x Compute power for training compared to Auto regressive models.

AR indictaes the end of response using EOS (End of sequence) to stop the generation process, while Diffusion depends on having a predifined Bucket size to stick too in generation.

### Extras,

We are already  witnessing the combining ifr *Block Text Diffusion* with AR in new models (DFlash & Spark) in order to achieve faster inference, speceilly with Speculative Decoding, so the Diffusion model generates Draft Tokens very quickly, and the AR model verifies each token, so you get the low latency/ throughput of Diffusion, with AR accuracy [12][12].

Following are the current soup of Diffusion models, between research, open and API served models, as of Aug 2026 ,

| Model                                   | Provider                | Release Date   | Parameters                                           | Context Window                                 |
| --------------------------------------- | ----------------------- | -------------- | ---------------------------------------------------- | ---------------------------------------------- |
| **LLaDA-MoE-7B-A1B**                    | Ant Group / inclusionAI | 11 Sep 2025    | 7B total / 1.4B active (MoE)                         | 4K native, 8K annealed                         |
| **TraDo-8B-Instruct / Thinking**        | Gen-Verse               | 8 Sep 2025     | 8B                                                   | 32,768 (32K)                                   |
| **LLaDA2.0-mini**                       | Ant Group / inclusionAI | Dec 2025       | 16B total / 1.4B active (MoE)                        | 32,768 (32K), extendable to 64K                |
| **LLaDA2.0-flash**                      | Ant Group / inclusionAI | Dec 2025       | 100B total / 6.1B active (MoE)                       | 32,768 (32K), extendable to 64K                |
| **WeDLM-8B-Instruct**                   | Tencent (WeChat AI)     | 28 Dec 2025    | 8B                                                   | 32,768 (32K)                                   |
| **Stable-DiffCoder-8B**                 | ByteDance Seed          | 22 Jan 2026    | 8B                                                   | 8,192 (8K)                                     |
| **LLaDA2.1-mini / LLaDA2.1-flash**      | Ant Group / inclusionAI | ~Feb 2026      | 16B / 100B (MoE, same as 2.0)                        | 32,768 (32K)                                   |
| **Mercury 2** *(API, not open-weight)*  | Inception Labs          | 24 Feb 2026    | Not disclosed                                        | 128,000 (128K)                                 |
| **Nemotron-Labs-Diffusion (3B/8B/14B)** | NVIDIA                  | 22–23 May 2026 | 3B / 8B / 14B (dense, Base & Instruct each)          | 262,144 (256K, via YaRN scaling from 16K base) |
| **Nemotron-Labs-Diffusion-VLM-8B**      | NVIDIA                  | 22–23 May 2026 | ~9B (8B text backbone + vision encoder)              | 262,144 (256K)                                 |
| **Nemotron-TwoTower-30B-A3B**           | NVIDIA                  | 25 Jun 2026    | 60B total (2×30B towers, MoE) / ~3B active per token | 128,000 (128K)                                 |
| **DiffusionGemma 26B-A4B**              | Google DeepMind         | 10 Jun 2026    | 25.2B total / 3.8B active                            | 256,000 (256K)                                 |

## Close

There are a lot of money being pured into trying to solve a lot of the limitations faced by the current models, but these solutions have not been scaled largely yet, but at the same in later articles , we will discuss how the current everyday AR models have been morphing into hybrids borrowing some of the features from these technologies, to plug in the gaps.

## Further reads

- Block Diffusion models ( Combining Diffusion and AR to make the Token Block dynamic in size, just like AR, example is GemmaDiffusion ), it also enable KV Caching for Diffusion.
- Masked vs Uniform Diffusion.
- AR, vs Diffusion vs Self-Speculation ( Combining Diffusiong Parallel Generation with AR Validation ).
- Nvidia Nested Models (Getting smaller models in Post training instead of in Pre training) + Elastic Budget for models (Example, using 12B SLM for thinking then 30B for Final answer)
- Groq LPUs (Large Processing Unit, this is comapred to GPUs / WSE) - Used by Nvedea for Prefil accelration on the new Vera Rubin NVL 72 deployments.
- Dense vs MOE models - old but gold concept.

## References

[1]: [Umar Jamil — Stable Diffusion from Scratch in PyTorch](https://youtu.be/MqjvfJTCuqw?si=w1vIgLqRE5iDc15f) — Detailed video breakdown covering the math, architecture, and step-by-step PyTorch implementation of diffusion models.

[2]: [YouTube — Diffusion Language Models Overview](https://www.youtube.com/watch?v=bmr718eZYGU&list=PL4bm2lr9UVG3SN79Y6WBe4OOlEiO88vie&index=2) — Video presentation explaining discrete diffusion techniques applied to natural language processing tasks.

[3]: [Outcome School — How Do Diffusion Language Models (DLMs) Work?](https://outcomeschool.com/blog/how-do-diffusion-language-models-dlms-work) — Technical blog post providing an overview of adapting diffusion processes to non-autoregressive text generation.

[4]: [Google Developers — DiffusionGemma: The Developer Guide](https://developers.googleblog.com/en/diffusiongemma-the-developer-guide/) — Official developer guide introducing Google's diffusion-based language model architecture and implementation details.

[5]: [YouTube — Diffusion Models for Language Generation](https://www.youtube.com/watch?v=r305-aQTaU0) — Video lecture exploring continuous and discrete diffusion mechanisms for sequence modeling.

[6]: [ByteDance SEED Research — SEED-Diffusion Preview Released](https://seed.bytedance.com/en/blog/seed-research-seed-diffusion-preview-released-a-diffusion-language-model-delivering-breakthrough-2-146-tokens-s-inference-speed) — Announcement detailing a high-speed diffusion language model achieving fast inference benchmarks.

[7]: [YouTube — Advanced Discrete Diffusion for Text](https://www.youtube.com/watch?v=UYVObn1HUeU&t=165s) — Video discussion focusing on discrete sequence diffusion, sampling strategies, and generation speed.

[8]: [YouTube — Understanding Non-Autoregressive Diffusion LLMs](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D1fUSw9Jgvog) — Instructional video covering the fundamentals of sequence-based diffusion algorithms for language.

[9]: https://research.nvidia.com/publication/2026-05_nemotron-labs-diffusion-tri-mode-language-model-unifying-autoregressive
[10]: https://arxiv.org/html/2601.14041v1
[11]: https://www.cerebras.ai/blog/introducing-cerebras-cs-4
[12]: https://leoniemonigatti.com/blog/speculative-decoding.html
