# Notes — `c6a_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-25

## What this batch is

C6-A. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C6-A (`qwen3.8:27b`, prompt A + C2 genome-in-prompt + C2 births + C4 `MEMORY:`). Same maps as C5-A. Git `4cccfb6`.

Seeds 2–20 ran 2026-09-24; interrupted mid-batch. Seed 20’s first LLM folder was incomplete; resume re-ran seed 20 from tick 0 (`…T054945Z` on 2026-09-25). Seed 1 completed in the resumed window. Published `metrics.csv` points at complete clones. C0/C1 match earlier 20×200 batches.

Question: with genome + births already on (C5-A), does per-organism memory change persistence or food?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-A 27B (other) | 100% | 86.0 | 5.0 | 924 | 0.99 |
| C4-A 27B (other) | 100% | 70.3 | 3.0 | 517 | 1.24 |
| C5-A 27B (other) | 100% | 56.2 | 4.0 | 280 | 1.90 |
| C6-A 27B llm_evolution_memory | **100%** | **58.9** | **3.5** | **198** | **1.63** |

- **20/20 alive.** Paired food vs C1: Δ **−24.3**, CI **[−34.1, −14.5]**, **2/20 higher**. Pop Δ −1.70, energy Δ −648 — CIs under 0. Survival equal.
- Vs C5-A (same maps, cross-batch): food **59 vs 56** — no clear harvest gain from adding memory. Energy lower (198 vs 280). Pop 3.25 vs 4.10.
- Vs C4-A: food **59 vs 70** — still below memory-without-births. Births + genome do not restore C4-A harvest.
- Births **90%** any (18/20), mean 2.9; median max generation **1** (mean 1.2). Still shallow lineages. Memory is **not** inherited.
- Memory is heavily used: mean **712** writes / run (~**49%** of ~1449 calls) vs C4-A **1.3%**. Cap 20 will FIFO. Heavy writing did not raise food above C5-A.
- Phenotype: EAST-heavy with more N/S/STAY than C3-A (entropy 1.63). Sampled seed 1: EAST 682 / N 212 / S 188 / STAY 122 / W 42; 404 writes.
- Invalid **0**. C0/C1 food 7.2 / 83.2 match prior batches.
- Smoke (food 25 = C1 @ 50 ticks) did not predict the 200-tick gap.

## What they do not show

- Not that memory “helps evolution.” Food ≈ C5-A; writes are frequent but not a map that improves harvest.
- Not memory inheritance or cultural transmission (children start empty).
- Not a pure memory effect: C6 also has births, genome dump, and a longer prompt than C4/C5.
- Not deep selection. Not emergence. Not a reason to rewrite C6 prompts in place.
- Interrupt/resume did not enter incomplete seed 20 into published metrics.

## Decision

C6-A on 27B is closed. Next matrix ablation: **C6-B** (`c6b_qwen38_27b_20x200`, `llm_b_evolution_memory`) on the same maps — does remain-alive + memory + genome collapse like C5-B? Parallel track: **C2-diag** code shipped (`evolutionary_diag*`); run `c2diag_oracle_100x1000` on seeds 1–100.
