# Notes — `diag_c2_oracle_100x1000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

Same seeds 1–100, 1000 ticks, m1-v2. Clones of **C1**, **C2-oracle** (same 9 features, fixed cardinal genome, no reproduction, no mutation), and **C2**. Git `823cc1aa23329d56ac86709cad5ec9167013d16b`.

Question: if we hand-set “food on axis → walk that way,” does the C2 phenotype forage like C1?

## What the numbers show

- C1 97% alive, mean food 276 (clone of earlier batches). C2 6% alive, mean food 25 (same clone).
- Oracle: **32% alive**, mean food **89**, mean pop 0.34, no births (by construction). Pop `{0:68, 1:30, 2:2}`.
- Oracle ≪ C1 (food 98/100 losses; survival 66 losses / 33 ties). Oracle ≫ C2 on food (94/100) and censored TTE (83/100).
- Representability already showed on-axis agreement 100% and diagonal-only ~20%. This batch shows that gap **costs persistence**, not just action match.

## What they do not show

- Not that the oracle is a C1 clone. Diagonal food stays invisible.
- Not that C2 “cannot evolve.” That needs the same phenotype with births (`diag_c2_oracle_r_100x1000`).
- Not emergence.

## Decision

Do not expand C2 features in v0.1. The 9-bit phenotype is strictly weaker than C1.
