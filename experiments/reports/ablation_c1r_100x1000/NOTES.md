# Notes — `ablation_c1r_100x1000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-15

## What this batch is

Same seeds 1–100, same 1000 ticks, same m1-v2 world as `batch100x1000`. Clones of **C1**, **C1-R** (`reactive_r`: same greedy food policy, reproduction ON, no genome), and **C2**. Git `77753cea747983af8747e4ddb20e7d24926333ba`.

This is the ablation that `batch100x1000` could not do: hold the birth rule fixed, swap only the decision class (C1-R vs C2), and separately hold the decision class fixed, swap only births (C1 vs C1-R).

## What the numbers show

- **C1 vs C1-R, survival:** almost the same (97% vs 95%; 94/100 ties). Reproduction does not kill the reactive forager on this horizon.
- **C1 vs C1-R, population:** births are cheap enough that C1-R is a different ecology. Mean pop 2.72 → 8.48, mean births 0 → 38, mean max generation 0 → 7.17, median first birth tick 4, mean food 276 → 527. Final energy is *lower* for C1-R (mean 1588 → 602) because energy is spent into children — not because they fail to feed.
- **The world can support multiple generations.** That was the freeze criterion. m1-v2 stays.
- **C2 vs C1-R, same birth rule:** C2 loses on nearly every map (pop 94 losses / 5 ties / 1 win; births 97 losses; survival 89 losses / 11 ties / 0 wins). Mean max generation 0.48 vs 7.17.
- **C2 is the same clone as `batch100x1000`:** same 6% alive, same six seeds. Determinism, not a new sample.
- C2 first birth (among the 32 that birth) is later than C1-R (median 25 vs 4). C2 is slow to enter the loop and usually never does.

## What they do not show

- Not that C2 genomes are “worse intelligence.” They are random-init linear argmax policies that usually do not harvest, over a **narrower** feature set than C1 (no diagonal food).
- Not that one C2 birth is evolution. 22/32 birthing C2 seeds have exactly one birth.
- Not that 1000 more seeds would flip the typical outcome. They would estimate the 6% rate more tightly and collect more hits.
- Not persistence: 1000 ticks does not say whether seed 3’s pop 7 is a flash or a lineage that lasts.

## Decision

**Freeze 30/15.** Do not add food. Do not retune C2 mutation or init to look better.

Next run is persistence, not more 1000-tick lottery tickets: same maps 1–100, **10000 ticks**, C1-R + C2.
