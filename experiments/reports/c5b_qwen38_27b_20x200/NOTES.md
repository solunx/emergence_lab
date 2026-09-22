# Notes — `c5b_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-22

## What this batch is

C5-B. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C5-B (`qwen3.8:27b`, prompt B + C2 genome as prompt context + C2 reproduction/mutation). Same maps as `c5a_qwen38_27b_20x200`. Git `09b0f80`.

Partial run paused mid-batch after seed 15; resumed later for seeds 16–20 (and any incomplete seed). Published aggregate is the full 20.

Question: on the model that persists under C5-A, does “remain alive” plus genome/births pull toward STAY, thin the population, or reduce survival?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-B 27B (other batch) | 100% | 82.4 | 4.0 | 664 | 0.99 |
| C4-B 27B (other batch) | 100% | 34.5 | 2.0 | 195 | 1.59 |
| C5-A 27B (other batch) | 100% | 56.2 | 4.0 | 280 | 1.90 |
| C5-B 27B llm_b_evolution | **60%** | **22.6** | **1.0** | **97** | **0.77** |

- **12/20 alive** (8 extinct). Mean TTE among extinct: **146.5** (126–185). First 27B main-matrix condition that fails to persist 20/20.
- Paired vs C1: food Δ **−60.6**, CI **[−71.1, −50.0]**, **0/20 higher**. Survival Δ **−0.40**, CI under 0. Pop Δ −3.0, energy Δ −749 — all CIs under 0.
- Vs C5-A on the same maps: alive 60% vs 100%; food **23 vs 56**; pop 1.95 vs 4.10; energy 97 vs 280. B is a **strong** ablation once genome+births are on (on C3-B alone, B still tied C1 harvest).
- Vs C4-B: C4-B stayed 20/20 with food 35; C5-B dies more often and harvests less. Births do not rescue STAY.
- Any birth **70%** (14/20), mean births 2.8. Median max generation still **1**. Seed 5 is an outlier (11 births, pop 11, food 75) — not the typical phenotype.
- Extinct seeds take almost no food (2–10). Survivors are thin: final pop distribution `{0:8, 1:4, 2:2, 3:3, 5:1, 6:1, 11:1}`.
- Phenotype is STAY-dominant. Sampled seed 1: STAY 1290 / N 98 / E 78 / S 37 / W 28 (entropy 0.92). Seed 15 extinct: STAY 977 of ~1022 actions, food 2. Invalid **0**.
- C0/C1 clones match earlier 20×200 batches (food 7.2 / 83.2).
- Smoke (STAY ~83%, food 14) foreshadowed the direction correctly.

## What they do not show

- Not that B “teaches survival.” Alive at 200 with pop 1 is a thin remainder; 40% go extinct.
- Not a pure B effect or pure evolution effect. C5-B = remain-alive + genome dump + births + longer prompt.
- Not that C3-B’s mild B effect generalizes: without memory/genome, B still harvested; with C5 machinery, B collapses foraging.
- Not deep selection (median max gen 1). Not emergence. Not a reason to rewrite A/B in place.
- Seed 5’s high-birth survivor is an outlier for GIFs, not evidence of a working policy.
- The aggregate line “No non-reactive survivors” is a summarize artefact when some LLM runs die.

## Decision

C5 A/B on 27B is **closed**. Do not retune the world or rewrite prompts. Next matrix cell is **C6** (LLM + evolution + memory) — needs code first (combine C5 genome/births with C4 `MEMORY:`). Optional later ablation: **C3-R** (LLM + births, no genome) to separate births from genome-in-prompt — also needs code. Neither is a silent config flip.
