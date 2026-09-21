# Notes — `c5a_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-21

## What this batch is

C5-A. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C5-A (`qwen3.8:27b`, prompt A + C2 genome as prompt context + C2 reproduction/mutation). Same maps as `c3a_qwen38_27b_20x200` / `c4a_qwen38_27b_20x200`. Git `d8d8867`.

Seeds 1–18 ran 2026-09-15; seeds 19–20 resumed 2026-09-21. Published aggregate is the full 20.

Question: with the 27B phenotype that harvests under C3-A, does showing the C2 genome and allowing births/mutation change persistence or food vs C1 / C3-A?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-A 27B (other batch) | 100% | 86.0 | 5.0 | 924 | 0.99 |
| C4-A 27B (other batch) | 100% | 70.3 | 3.0 | 517 | 1.24 |
| C5-A 27B llm_evolution | **100%** | **56.2** | **4.0** | **280** | **1.90** |

- **20/20 alive**, **20/20 any birth**. Mean births **3.7** (1–7). Mean max generation **1.5** (median 1) — shallow lineages, not multi-generation selection.
- Paired vs C1: food Δ **−27.0**, CI **[−36.5, −17.4]**, **3/20 higher**. Pop Δ −0.85, CI under 0. Energy Δ **−566**, CI under 0. Survival 20/20 equal.
- Vs C3-A on the same maps (cross-batch): food **56 vs 86**; energy **280 vs 924**; pop 4.1 vs 4.55. Genome+births did **not** improve harvest over plain C3-A.
- Vs C4-A: food **56 vs 70** — worse than memory-only on food, but C5 has births (C4 does not).
- Mid-run mean pop **7.93** (above C1 7.30) then ends thinner: births inflate, deaths ~9.6 absorb most of them.
- First birth: mean 29.9 / median 18 (range 3–102). Invalid **0**. Memory writes **0**.
- Phenotype more mixed than C3-A: entropy **1.90** vs 0.99. Sampled seed 1: EAST 646 / STAY 505 / N 245 / S 238 / W 30. Substantial STAY vs C3’s EAST sweep.
- C0/C1 clones match the earlier 20×200 batches exactly (food 7.2 / 83.2).
- Smoke (seed 1 × 50: food 23 ≈ C1 25) did **not** predict the 200-tick food gap.

## What they do not show

- Not that “evolution” as a pure factor caused the food drop. C5 mixes genome-in-prompt, births, mutation, longer prompts, and extra LLM calls as population grows. Spec: do not read C5−C3 as a pure evolution effect.
- Not that the LLM follows the C2 argmax. The genome is shown and “does not require any action”; decisions remain LLM tokens.
- Not deep genetic adaptation. Median max generation 1 = founders plus one child layer.
- Not that C5 failed to persist. 20/20 alive at 200 with food ≫ C0.
- Not a rescue of C2. C2’s failure was representation + bootstrap under a linear policy; C5 persists because the LLM decides.
- Not 1000-tick persistence. Not emergence. Not a reason to rewrite the C5 prompt in place.
- The aggregate line “No non-reactive survivors” is a summarize artefact: the LLM also survived.

## Decision

C5-A on 27B is closed. Do not retune the world or rewrite prompts. Next is **C5-B** on the same 20 maps (`c5b_qwen38_27b_20x200`, `llm_b_evolution`): does “remain alive” plus genome/births pull toward STAY or thin the remainder further (as C4-B did vs C4-A)? C6 waits until C5 A/B is closed. Optional later: C3-R (LLM + births, no genome) to separate births from genome-in-prompt.
