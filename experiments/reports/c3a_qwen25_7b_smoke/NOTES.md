# Notes — `c3a_qwen25_7b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

Pipeline check: seed 1, 50 ticks, clones of C0 / C1 / C3-A (`qwen2.5:7b`, prompt A). Too short to measure persistence.

## What the numbers show

- Adapter works: 500 LLM calls, invalid-action rate 0.
- Survival 10/10 for all three is uninformative. STAY costs 1/tick from energy 100, so nobody can die by tick 50.
- Food: C1 25, C0 4, C3-A **1**. Final energy: C1 837, C3-A 496, C0 218.
- C3-A energy matches almost-all-STAY (466/500 STAY). Conserves energy by not moving; does not forage.

## What they do not show

- Not that C3-A persists. Need ticks > 100 (STAY-only death horizon).
- Not a model comparison.

## Decision

Keep m1-v2. Next: same prompt and model, 20 seeds × 200 ticks (`c3a_qwen25_7b_20x200`).
