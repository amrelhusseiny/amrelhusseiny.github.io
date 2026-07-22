---
date: 2026-07-22T08:35:00Z
title: "Cisco Antares, 350M/1B Parameter SLMs for CVE detection"
---

Yesterday (21st July), Cisco has released its own fine-tuned models (SLMs) on Hugging Face
(Gated — Access must be approved by Cisco) based on IBM's Granite 4.0, targeted at security
vulnerability scanning of your packages, using its Antares CLI.

2 variants available, **350M parameters** & **1B parameters** versions, a **3B version** is
being released however not on Hugging Face yet, to be released later.

You can run it easily on your local machine, and it does not need internet access to search
for CVEs, it was trained on CWE categories and code patterns.

---

## My Testbed

Using a Production level repo @ https://github.com/indexzero/nconf/tree/v0.11.3 which was
identified in **CVE-2022-21803** *(Prototype Pollution, CWE-1321)*.

The agent was able to identify a vulnerable file indeed (**`lib/nconf/common.js`**), however
it could not point out the main culprit that was mentioned in the CVE which is
(**`lib/nconf/stores/memory.js`**).

```bash
$ docker exec -it antares-cli antares

  Target:   /workspace/repo
  Mode:     query — single CWE-scoped scan
  CWE IDs:  CWE-1321
  Budget:   15 tool calls
  Profile:  antares-ollama (antares-1b · http://antares-ollama:11434/...)
  Reports:  disabled

  ▸ Launch

╭─────────────────────────────── SCAN SUMMARY ────────────────────────────────╮
│ Status                Complete                                               │
│ Findings              1                                                      │
│ Affected files        1                                                      │
│ CWEs checked          1                                                      │
│ CWE IDs with findings CWE-1321                                               │
│ Duration              925.31s (~15 min, CPU only, no GPU)                    │
│ Total tool calls      11 / 15                                                │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────── FINDING ─────────────────────────────────╮
│ Title     Improperly Controlled Modification of Object Prototype Attributes  │
│           ('Prototype Pollution')                                            │
│ File      lib/nconf/common.js                                                │
│ CWE       CWE-1321                                                           │
│ Rank      1                                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## Verdict

Still gonna run more tests, but it's a good start for Cisco I think, however, I don't believe
baking the existing CVE patterns into the model's training is the way to go, since these things
need to be updated and shipped regularly *(cutoff date for knowledge was **April 2025**)*,
tool use is the identified best practice now, or Cisco can offer a **Vector Database** for the
model to refer to so it can get up to date info.

---

## References

- [Antares Technical Report (PDF)](https://cisco-foundation-ai.github.io/antares/technical-report.pdf) — the actual research paper behind the model
- [CVE-2022-21803 on GitHub Advisory Database](https://github.com/advisories/GHSA-6xwr-q98w-rvg7) — direct link to the CVE used in the test
- [nconf v0.11.3 → v0.11.4 fix (PR #397)](https://github.com/indexzero/nconf/pull/397) — shows exactly what the fix was (`memory.js`), useful context for why the model missed it
