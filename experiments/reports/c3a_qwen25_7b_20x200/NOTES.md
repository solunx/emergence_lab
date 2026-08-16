# Notes — `c3a_qwen25_7b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

First C3 matrix run. Seeds 1–20, 200 ticks, m1-v2. Clones of **C0**, **C1**, **C3-A** (`qwen2.5:7b`, prompt A: pick one of NORTH/SOUTH/EAST/WEST/STAY from the 5×5 only). No reproduction. Git `99ab557`.

Question: without a food or survival instruction, does a small local LLM persist or forage on the frozen world?

## What the numbers show

| Controller | Alive | Mean food | Med TTE | Action entropy |
|---|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 101.5 | ~2.32 |
| C1 reactive | **100%** | **83.2** | 200 (censored) | ~2.31 |
| C3-A llm | **0%** | **1.6** | 124.5 | **0.37** |

- C1 pop at tick 200 is 3–8 (mean 5). The world supports foraging.
- C3-A food `{0:4, 1:7, 2:6, 3:1, 4:1, 6:1}`. Max is seed 15 with 6. C0 is 3–12.
- Paired food: C3-A −5.6 vs C0 (19/20 lower); −82 vs C1 (20/20).
- Paired TTE: C3-A **+15** vs C0 (15/20 longer) because STAY costs 1 and MOVE costs 2, not because C3-A eats more.
- Invalid-action rate 0 on all 20. Parse is not the failure mode.
- Phenotype is **STAY** (entropy 0.06–0.91). Zero-food seeds die at ticks 98–100 (energy-100 / STAY−1). WEST is essentially unused; leftover motion is mostly EAST.
- Seed 1 matches the smoke: still 1 food, TTE 121 ≈ one harvest of +30 after the STAY horizon.

## What they do not show

- Not that “the LLM is unintelligent.” Prompt A has no survive/food objective. C1 has a food prior. Same raw 5×5, different inductive bias.
- Not prompt B, not a larger model, not emergence.
- n=20 is enough for this contrast (food Δ vs C0 CI entirely below 0), not for rare-event rates.

## Decision

Do not retune the world or the C3-A prompt in place. Next is the spec ablation: **C3-B** (`llm_b`) on the same 20 maps (`c3b_qwen25_7b_20x200`).
