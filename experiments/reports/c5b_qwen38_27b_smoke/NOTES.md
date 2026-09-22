# Notes — `c5b_qwen38_27b_smoke`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-09-22

## What this batch is

Pipeline check: seed 1, 50 ticks, C0 / C1 / C5-B (`qwen3.8:27b`, prompt B + genome + births). Same map as C5-A smoke. Git `09b0f80`.

## What the numbers show

- Adapter works: 556 calls, invalid 0, ~1.33 s/call, 0 memory writes.
- Food: C1 25 / C0 4 / C5-B **14** (C5-A smoke: 23). Pop **12** (2 births). Energy 768.
- Phenotype is **STAY-heavy**: STAY 459 / EAST 41 / N·S 20 / W 16 (~83% STAY). Entropy **1.00** vs C5-A smoke 1.58.
- C0/C1 clones match prior 27B smokes.

## What they do not show

- Not 200-tick persistence. Not a 20-seed result. STAY bias is a hint that B will hurt harvest (full batch: 60% alive, food 23).

## Decision

Same prompt B + genome + births, seeds 1–20 × 200 (`c5b_qwen38_27b_20x200`).
