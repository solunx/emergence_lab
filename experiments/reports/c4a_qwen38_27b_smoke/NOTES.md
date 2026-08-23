# Notes — `c4a_qwen38_27b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-23

## What this batch is

Pipeline / latency check: seed 1, 50 ticks, C0 / C1 / C4-A (`qwen3.8:27b`, prompt A + memory). Same map as the C3 27B smoke. Git `e865cc9`.

## What the numbers show

- Adapter works: 500 calls, invalid 0, ~984 ms/call, **2** `MEMORY_WRITE`s.
- Food: C1 25, C0 4, C4-A **16** (C3-A smoke on this seed: 29). Energy 625 vs C1 837 vs C3-A 870.
- End pop 9 (1 death). Mix: EAST 291, WEST 132, NORTH 72, SOUTH 5, STAY 0. Not a STAY policy; more WEST than C3-A smoke (then almost all EAST).
- C0/C1 clones match the C3 27B smoke. Survival 10/10 at 50 ticks is uninformative for C0/C1.

## What they do not show

- Not persistence to tick 200. Not a 20-seed result. Not that memory helps or hurts (n=1, 2 writes).

## Decision

Same prompt A + memory, seeds 1–20 × 200 ticks (`c4a_qwen38_27b_20x200`).
