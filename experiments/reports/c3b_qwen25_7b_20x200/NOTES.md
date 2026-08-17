# Notes — `c3b_qwen25_7b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

C3 prompt-B ablation. Same seeds 1–20, 200 ticks, m1-v2, `qwen2.5:7b`. Clones of C0 / C1 / **C3-B** (`llm_b`: remain alive as long as possible, then pick NORTH/SOUTH/EAST/WEST/STAY). Git `99ab557`.

C0/C1 numbers match `c3a_qwen25_7b_20x200` (deterministic clones). The intervention is the survival sentence only.

Question: does telling the model to stay alive induce foraging, or more sitting?

## What the numbers show

| Controller | Alive | Mean food | Med TTE | Action entropy |
|---|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 101.5 | ~2.32 |
| C1 reactive | 100% | 83.2 | 200 | ~2.31 |
| C3-A (other batch) | 0% | 1.6 | 124.5 | 0.37 |
| C3-B llm_b | **0%** | **1.3** | **127** | **0.16** |

- Still 0/20 alive. Food `{0:5, 1:7, 2:5, 3:3}` — slightly **less** eating than A, still below C0 on 20/20.
- Entropy **lower** than A (0.16 vs 0.37): more STAY, not more exploration. Example: seed 11 is 994 STAY / 3 EAST / 0 food / TTE 100.
- TTE is the same story as A: a bit longer than C0 via metabolism (STAY −1 vs MOVE −2), dead by ~tick 100–150.
- Invalid-action rate 0.

Prompt B did not unlock C1-like foraging on this model. “Remain alive” is locally consistent with STAY.

## What they do not show

- Not that survival instructions never matter. This is `qwen2.5:7b` at temperature 0. A larger model is a different `experiment_id`.
- Not a reason to rewrite prompt A/B in place to look better. That would be a new named condition.
- Not emergence.

## Decision

7B C3-A and C3-B are both STAY policies on m1-v2. Next was a model variant with prompt A held fixed (`qwen3.8:27b`). That run is done: see `c3a_qwen38_27b_20x200`.
