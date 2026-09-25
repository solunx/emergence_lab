# Notes — `c6a_qwen38_27b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-25

## What this batch is

Pipeline check: seed 1, 50 ticks, C0 / C1 / C6-A (`qwen3.8:27b`, prompt A + genome + memory + births). Same map as prior 27B smokes. Git `4cccfb6`.

## What the numbers show

- Adapter works: 560 calls, invalid 0, ~1.73 s/call, **177** memory writes (~32%).
- Food: C1 25 / C0 4 / C6-A **25**. Pop **11** (2 births). EAST-heavy (408), almost no STAY (2).
- Flags: genome + repro + memory; `m3-c6-v1`; `num_predict` 128.
- C0/C1 clones match prior 27B smokes.

## What they do not show

- Not 200-tick persistence. Write rate on one short seed does not predict C4-like sparsity (full batch ~49% writes).

## Decision

Same condition, seeds 1–20 × 200 (`c6a_qwen38_27b_20x200`).
