# Notes — `c5a_qwen38_27b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-21

## What this batch is

Pipeline / latency check: seed 1, 50 ticks, C0 / C1 / C5-A (`qwen3.8:27b`, prompt A + genome, C2-like births). Same map as the C3/C4 27B smokes. Git `d8d8867`.

## What the numbers show

- Adapter works: 580 calls (pop grew), invalid 0, ~1.32 s/call, **0** memory writes.
- Food: C1 25, C0 4, C5-A **23**. Energy 726 vs C1 837 vs C3-A smoke 870.
- End pop **12** (3 births, 1 death, max gen 2). Mix: EAST 337 / STAY 156 / N·S / little WEST — not 7B-STAY.
- C0/C1 clones match prior 27B smokes on this seed.

## What they do not show

- Not persistence to tick 200. Not a 20-seed result. Food ≈ C1 here is a short-horizon artefact (full batch: food **56** vs C1 **83**).

## Decision

Same prompt A + genome + births, seeds 1–20 × 200 ticks (`c5a_qwen38_27b_20x200`).
