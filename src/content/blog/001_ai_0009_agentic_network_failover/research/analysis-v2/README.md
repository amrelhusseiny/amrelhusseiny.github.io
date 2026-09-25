# analysis-v2 — technical analysis of the OSPF vs Agent failover comparison

Generated 2026-09-25 from the raw run artifacts in `../lab-compare/`.
Read this before writing the article.

## Files

| File | Purpose |
|---|---|
| `01-scenario-ospf.md` | OSPF run: mechanism, annotated timeline, verbatim log snippets, time budget, strengths/weaknesses |
| `02-scenario-agents.md` | Agent run: same structure, plus the full rendered plan and both agent transcripts |
| `03-comparison-and-findings.md` | **Start here.** Scoreboard, honest framing, and findings F1–F5 |
| `snippets/` | Copies of every raw artifact referenced by the analysis |

## The one-paragraph version

Identical failure (R1 pod deleted) was injected into two Kubernetes/FRR labs.
OSPF restored forwarding in **62.2 s**; the agent stack restored it in **49.7 s**
(`repaired: true`, `applied_clean: true`, cost **$0.000705**). But 30.4 s of the
OSPF number is the k8s termination grace period, not OSPF. Measured from actual
pod death the contest is **OSPF ~31.8 s vs agents ~15.9 s** — the agents are
roughly 2x faster, at the cost of a 12.0 s LLM render step in the critical path
and a dependency on an external inference API that a routing protocol does not have.

## Five things to know before you write

1. **F1** — the agent scenario did **not** start from a clean Path 1. `before.txt`
   shows rc1 already on `gre-r3` (Path 0) while the header claims Path 1. The lab
   was in a forward/return split state, and the agent's real job was reconciling
   that. This contradicts REPORT-V2's baseline claim.
2. **F3** — the classify LLM returned `EMPTY` yet still emitted `confidence: 0.9`.
   The 0.9 is not model-derived; classification fell back to deterministic rules.
3. **F4** — no TypeSafe Jev in either run. Detect = `inception/mercury-2`,
   repair = `inception/mercury-2.5`.
4. **F2** — `gre-r1 up=True` was reported 23 s after the pod died. Do not quote
   that field as a signal.
5. **F5** — only the OSPF run has a per-second watch log, so the agent run's true
   outage start is unobservable and its 33.8 s detect may be inflated.

## Raw data provenance

All numbers in the analysis are traceable to files in `snippets/`, which are
byte-for-byte copies of `../lab-compare/v2-ospf/` and `../lab-compare/v2-agents/`.
Epoch values: OSPF T0 `1790279792.5129786`, agents T0 `1790280808.0`.
