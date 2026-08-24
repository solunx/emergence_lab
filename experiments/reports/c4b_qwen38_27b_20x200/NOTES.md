# Notes — `c4b_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-24

## What this batch is

C4-B. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C4-B (`qwen3.8:27b`, prompt B + optional `MEMORY:` writes). Same maps as `c4a_qwen38_27b_20x200`. Git `0a85cc5`.

Question: on the model that already persists under C4-A, does “remain alive” plus memory pull toward STAY, change write rate, or keep the C4-A harvest?

**Interrupt:** seed 11 was killed mid-run (GPU contention from another local job). The first `llm_b_memory_seed11_20260823T200557Z` folder has snapshots only — no `events.jsonl`, no metrics. Resume re-ran seed 11 from tick 0 (`…T204817Z`). Published numbers are that complete clone. C0/C1 on every seed match the earlier 20×200 batches. Invalid 0. The crash did not enter the stats.

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-B 27B (other batch) | 100% | 82.4 | 4.0 | 664 | 0.99 |
| C4-A 27B (other batch) | 100% | 70.3 | 3.0 | 517 | 1.24 |
| C4-B 27B llm_b_memory | **100%** | **34.5** | **2.0** | **195** | **1.59** |

- 20/20 alive, but thin: pop 1–4 (9 seeds end at 1). Food 20–57. Invalid 0. ~19k calls, ~1.40 s/call.
- Paired vs C1: food Δ **−48.6**, CI **[−55.8, −41.4]**, **0/20 higher**. Pop Δ −3.15, energy Δ −651 — all CIs under 0. Survival still 20/20.
- Vs C4-A on the same maps: food 35 vs 70; pop 1.80 vs 3.45. Prompt B is a **strong** ablation here (on C3-B without memory it was a tie with C1).
- Memory is used: mean **191** writes / run (median 184, range 49–434), **20%** of decisions vs C4-A **1.3%**. Cap 20 will FIFO. Writes did not raise food (seed 17: 434 writes, food 22).
- Phenotype is not C4-A’s EAST sweep and not 7B-STAY. Sampled logs: seed 1 NORTH 508 / EAST 244 / STAY 52; seed 2 uses all five actions (STAY 98). Entropy 1.59 vs C4-A 1.24 vs C3-B 0.99.
- C0/C1 clones match the earlier batches.

## What they do not show

- Not that the GPU interrupt corrupted the batch. Seed 11 was fully re-run; leftover snapshots are not in `metrics.csv`.
- Not that B “teaches survival.” Alive at 200 with pop 1 is a thin remainder, not a better policy.
- Not a pure memory effect, and not a pure B effect. C4-B is B + memory + a longer prompt than C3-B.
- Not 7B-style STAY-until-death (food 35 ≫ C0 7; invalid 0).
- Not 1000-tick persistence. Not emergence. Not a reason to rewrite A/B in place.
- The aggregate line “No non-reactive survivors” is a summarize artefact: the LLM also survived.

## Decision

C4 A/B on 27B is closed. Do not retune the world or rewrite prompts. Next matrix cell is **C5 (LLM + evolution)** — genome as prompt context, reproduction/mutation like C2, LLM still decides. That needs code first; no C5 batch until a smoke exists. 7B-C4 and 1000-tick C4 are later variants.
