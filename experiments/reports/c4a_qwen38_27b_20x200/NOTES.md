# Notes — `c4a_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-23

## What this batch is

C4-A. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C4-A (`qwen3.8:27b`, prompt A + optional `MEMORY:` writes). Same maps as `c3a_qwen38_27b_20x200`. Git `e865cc9`.

Question: with the 27B phenotype that already harvests under C3-A, does per-organism `list[str]` memory change persistence or food vs C1 / C3-A?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-A 27B (other batch) | 100% | 86.0 | 5.0 | 924 | 0.99 |
| C4-A 27B llm_memory | **100%** | **70.3** | **3.0** | **517** | **1.24** |

- 20/20 alive. Pop 2–5 (C1: 3–8; C3-A: 3–6). Food 33–99 (C1: 52–118). Invalid ≈ 0 (one seed, ~2 tokens). ~26.5k calls, ~1.13 s/call.
- Paired vs C1: food Δ **−12.8**, CI **[−22.8, −2.8]** (7/20 higher, 13 lower) — **below C1**, not a tie. Pop Δ −1.50, CI under 0. Energy Δ −329, CI under 0. Survival 20/20 equal.
- Vs C3-A 27B on the same maps (cross-batch, same seeds): food 70 vs 86; pop 3.45 vs 4.55; energy 517 vs 924. C4-A is the first 27B condition that does **not** match C1 harvest.
- Seed 1 continues the smoke: 50 ticks → 16 food / pop 9; 200 ticks → **33 food / pop 3** (C3-A on that map: 94 / 4; C1: 60 / 3).
- Memory is sparse: mean **17** writes / run (median 7, range **0–78**), **1.3%** of decisions. Seed 13 wrote nothing. Cap 20 is not the bottleneck.
- Phenotype stays EAST-heavy, but WEST/STAY appear more than C3-A (entropy 1.24 vs 0.99). Sampled logs: seed 1 EAST 730 / WEST 359 / STAY 0; seed 16 EAST 600 / WEST 146 / STAY 15 and the most writes (74) with food 61 vs C3-A 127. More writing did not mean more food.
- C0/C1 clones match the earlier 20×200 batches.

## What they do not show

- Not that “memory” as a pure factor caused the harvest drop. C4 is also a longer prompt / more tokens even when the list is empty. Spec: do not read C4−C3 as a pure memory effect.
- Not that agents used memory as a map. Writes are rare; empty memory is the typical prompt.
- Not that C4 *is* C1, or that C4 failed to persist. 20/20 alive at 200 with food ≫ C0.
- Not 1000-tick persistence. Not emergence. Not an intelligence score. Not a reason to rewrite the memory prompt in place to look better.
- n=20 is enough to say “C4-A on this model is worse on food than C1/C3-A and barely writes”; not for rare events.
- The aggregate line “No non-reactive survivors” is a summarize artefact: the LLM also survived.

## Decision

Do not retune the world or the C4 prompt to rescue harvest. Next is **C4-B** on the same 20 maps (`c4b_qwen38_27b_20x200`): does “remain alive” plus memory pull this mix toward STAY, or leave the weaker EAST/WEST phenotype? C5 (genome in the prompt) waits until C4 A/B is closed. 7B-C4 is still a later variant.
