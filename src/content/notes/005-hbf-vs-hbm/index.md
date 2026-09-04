---
date: 2026-08-23T00:00:00Z
title: "HBF vs HBM: A New Memory Tier Between HBM and SSDs"
description: "Notes on High Bandwidth Flash (HBF), SK hynix's NAND-based memory layer positioned between HBM and SSDs, how it compares to HBM, and where the AIN family (P/D/B) fits."
draft: true
---

## HBM, quickly

**High Bandwidth Memory (HBM)** is stacked DRAM (via TSVs) sitting right next to the
compute die on an interposer. It's fast (~1+ TB/s per stack on HBM3E) but capacity-limited
(tens of GB per stack) and volatile — expensive per GB, and it disappears on power loss.

## HBF, the new layer

**High Bandwidth Flash (HBF)** is SK hynix's (with Sandisk) answer to the AI memory
bottleneck: a new tier that sits *between* HBM and SSDs. It reuses NAND (not DRAM), so it
trades some speed for much higher capacity, while still being far faster than a regular SSD.

- Announced as a full standard spec at **FMS 2026** (Aug 4–6, Santa Clara), ~6 months after
  the HBF consortium launched (Feb 2026), building on the Aug 2025 SK hynix + Sandisk
  standardization partnership.
- **Capacity:** up to **512GB**, via two stack configs (8-high / 16-high NAND dies).
- **Bandwidth:** 3 grades, roughly **0.4 TB/s → 3.0 TB/s**.
- **Interconnect:** built on **UCIe** (Universal Chiplet Interconnect Express), so it can
  attach to GPUs or CPUs, not just one vendor's accelerator.
- Published through the **Open Compute Project (OCP)** as an open standard, not a
  proprietary part. Google and Tenstorrent are already in the consortium.
- Framed as part of a "**Tiered Memory**" architecture for agentic AI, where a single
  memory type can no longer cover ingestion → training → inference → archive.

## Where HBF fits: the AIN family

HBF isn't a standalone SK hynix product line — it's the tech behind one piece of a wider
"AI NAND" (AIN) strategy unveiled at OCP 2025:

- **AIN-P (Performance)** — ultra-low latency NAND for speed-critical inference and vector
  search.
- **AIN-D (Density)** — high-capacity, low-power/cost NAND (QLC/PLC-based) for large-scale
  AI storage.
- **AIN-B (Bandwidth)** — the one that actually uses **HBF**; stacks NAND vertically to
  push bandwidth well beyond a normal SSD.

## HBM vs HBF at a glance

| | HBM | HBF |
|---|---|---|
| Base tech | Stacked DRAM | Stacked NAND (flash) |
| Bandwidth | ~1+ TB/s per stack (HBM3E) | ~0.4–3.0 TB/s (Grade 1–3) |
| Capacity | Tens of GB per stack | Up to 512GB per stack |
| Persistence | Volatile | Non-volatile |
| Role | Sits closest to compute | Sits between HBM and SSD |
| Interconnect | Custom PHY on interposer | UCIe (open, chiplet-based) |

## Memory & storage in the AI data pipeline

```
                 Data Ingestion   Data Prep        Training          Inference           Archive
Operation        Capacity int.    Compute int.     Compute int.      Compute/Mem int.    Capacity int.
                 ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ ┌─────────────┐
                 │             │  │             │  │             │  │                  │ │             │
Memory           │             │  │ DDR5        │  │ HBM         │  │ PiM              │ │             │
                 │             │  │ CXL-MEM     │  │ CXL-MEM     │  │                  │ │             │
                 └─────────────┘  └─────────────┘  └─────────────┘  └──────────────────┘ └─────────────┘
Storage          QLC SSD          TLC SSD          TLC              TLC                  QLC SSD
                 └── High Capacity Storage ──┘     └──────── High IOPS & BW Storage ─────┘
```

*(HBF isn't on this slide yet — it would slot in as a new row between "Memory" and
"Storage," covering Training/Inference where HBM alone can't scale capacity.)*

## Is anyone actually deploying this yet?

Not in production, no — everything is still PoC/standard-stage as of today:

- SK hynix + NVIDIA are co-developing an "AI SSD" (NVIDIA calls it **Storage Next**,
  SK hynix calls it **AIN-P**), currently in **proof-of-concept testing**.
- Target: ~25M IOPS on PCIe Gen 6 by **late 2026**, mass production at **100M IOPS by 2027**.
- June 2026: NVIDIA and SK hynix announced a broader **multiyear memory partnership**
  (HBM4, Vera Rubin, Vera CPUs, RTX Spark, Jetson Thor) — the umbrella deal AIN sits under,
  but it's codevelopment/supply, not a live deployment.
- The **HBF spec itself** was only finalized as an open OCP standard on **Aug 4, 2026**,
  with Google and Tenstorrent in the consortium — also standard-stage only.

So: real partners, real timeline, but no shipping product or live deployment anywhere yet.

## Takeaways

- HBF isn't a replacement for HBM — it's a new middle tier to fix the "memory wall":
  HBM gives speed, SSD gives capacity, HBF tries to give a lot of both.
- Because it's UCIe-based and OCP-published, it's positioned as an industry-wide open
  standard rather than one vendor's proprietary silicon.
- Worth revisiting in 2027 when AIN-P/AIN-B are due to hit mass production — that's when
  "deployed" becomes a meaningful question.

## References

- [Beyond SSD — SK Hynix AIN Family: Redefining Storage as the Core Enabler of AI at Scale](https://www.youtube.com/watch?v=s_VQ6czcUcU) — Open Compute Project talk by Chunsung Kim on SK hynix's AIN family
- [SK hynix Unveils First HBF Standard Specifications with Sandisk, Presenting AI Memory Solutions at 'FMS 2026'](https://news.skhynix.com/en/hbf-at-fms-2026/) — official announcement with the spec numbers above
