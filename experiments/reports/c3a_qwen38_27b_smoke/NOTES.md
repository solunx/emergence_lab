# Notes — `c3a_qwen38_27b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

Pipeline / latency check: seed 1, 50 ticks, C0 / C1 / C3-A (`qwen3.8:27b`, prompt A). Same map as the 7B smoke.

## What the numbers show

- Adapter works: 500 calls, invalid-action rate 0, mean latency ~931 ms (~3× `qwen2.5:7b`).
- Food: C1 25, C0 4, C3-A **29**. Energy 870 vs C1 837 vs 7B-A 496.
- End pop 6 (4 deaths). Action mix is almost all EAST (465/500), no STAY — opposite of 7B (~93% STAY, 1 food).
- Survival 10/10 is still uninformative at 50 ticks for C0/C1; the 4 LLM deaths are movement cost, not parse failure.

## What they do not show

- Not persistence to tick 200. Not a 20-seed result. EAST on one map may be torus luck.

## Decision

Same prompt A, same seeds 1–20 × 200 ticks (`c3a_qwen38_27b_20x200`).
