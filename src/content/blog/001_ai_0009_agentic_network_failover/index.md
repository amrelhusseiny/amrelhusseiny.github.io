---
title: "Using Jev/RLCD Model (AKA: Decision Model) for network failover"
description: ""
date: 2026-09-20T00:00:00+02:00
tags:
    - ai
    - networks
    - automation
draft: false
---
Jev compared to GPT style models in a jeffy, 

Most of Jev showcases online focuses on Evals, or on how fast and cheap can you run AI API call to it, however , this is not useful for me a network engineer, 

In this one, am utilizing 2 Model types to acheves some cool test case, 

1) Diffusion model @ Mercurey 2.5 from Iception, which is capable of generating 1000Toks/sec - will be used for configuration changes and taking actual actions.
2) RLCD Model @ Jev from Typeface, will be used as the monitor of the topology and the trigger for the failover.

Why are doing this, instead of using a Dynamic routing protocol , i wnated to see if using models ,w e can acheive the same smartness and fast failover process,

And also for fun,

# Quick primer about Jev

System1 Models / RLCD learning model, or whatever you will hear on the internet about that, is not a new type of model, its been popularized by Jev, 

Instead of traditional models, it does not generate text, no next token prediction, 

<iframe src="/blog/jev_compitable_quesionts.html" width="100%" height="590" loading="lazy" scrolling="no" style="border:0;display:block" title="Jev Options"></iframe>

It reads MUST srtuctured data, which must be one of the following : 
    1. Choice (Most popular) : Pick one choice out of the list you gave it. (Example, which team should handle this , billing, purchasing , .. ?)
    2. Score : a score assigned to each cell of the list, you define the range. 
    3. Noul : Is it true ! questions (yes/no, True/False).

You need to fine rune your question to have very specific answer, dont ask compound questions.

# Lab topology
so the lab is as follows : 

![lab_topology](image.png)

Its pretty simple, we have 2 paths, primary is used with Static routes, the Linux Monitoring the routers is connected to all these routers which are FRR, and waiting for a failure to happen, then it will trigger the Actions agent running the Mecurey 2.5 model , to actually take the actions and validate.

Some show commands, so you can understand the current things running : 

> **_NOTE:_**  -Not a promotion- This lab was deployed on WWT's Kubernetes Sandbox lab on the WWT ATC Platform, its a nice way to try stuff out.

## Failover replay - OSPF vs agent stack

Identical failure (R1 pod deleted) injected into both labs. The animation runs on the real wall-clock timestamps recorded in each run log, with the node highlighted at the moment its log line appears.

<iframe src="/blog/ospf-failover-replay.html" width="100%" height="475" loading="lazy" scrolling="no" style="border:0;display:block" title="OSPF vs agent failover replay"></iframe>

# Refernces
- https://www.langchain.com/blog/building-a-harness-with-jev
- https://typesafe.ai/blog/introducing-system-one-models-and-jev
-
