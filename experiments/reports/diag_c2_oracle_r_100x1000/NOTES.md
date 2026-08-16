# Notes — `diag_c2_oracle_r_100x1000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

Same seeds 1–100, 1000 ticks, m1-v2. Clones of **C1-R**, **C2-oracle_r** (same 9 features, fixed cardinal genome, reproduction ON, no mutation/genome), and **C2**. Git `823cc1aa23329d56ac86709cad5ec9167013d16b`.

Question: with the birth rule held fixed, is C2’s failure “evolution cannot find cardinal phototaxis” or “even that phototaxis cannot hold a lineage”?

## What the numbers show

- C1-R 95% alive, mean births 38, mean max gen 7.17 (clone). C2 6% / 32% any-birth / gen 0.48 (clone).
- Oracle_r: **96% any-birth** (enters the loop like C1-R) but only **17% alive**, mean births 8.1, mean max gen **3.0**, median first birth 21 vs C1-R’s 4. 83% extinct, median TTE 433.
- Vs C2: oracle_r has more births (88/100), more food (92/100), higher max gen (83/100). Survival only 17 vs 6 (79 ties).
- Stacked failure: (1) 9 bits cannot be C1; (2) random-init C2 rarely matches the oracle (32% vs 96% any-birth); (3) the oracle lineage itself is weak (17% vs 95%).

## What they do not show

- Not that adding diagonal features would yield C1-R. Untested; that would be a new named C2.
- Not emergence. Mean generation 3 with 17% alive is not a persistent evolved population.

## Decision

M1 answer to “why C2 fails”: **representation ceiling plus bootstrap failure**, not a dead world and not “reproduction is too expensive.” Keep m1-v2 and the C2 feature set frozen. Next matrix cell is **C3-A** on this frozen world. Do not silently change C2 features.
