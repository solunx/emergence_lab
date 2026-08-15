# Notes — `batch100x1000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-15

## What this batch is

First 100-seed matrix on frozen economy **m1-v2** (food +30, regen 15). Same-world clones of C0, C1, C2. Seeds 1–100, 1000 ticks. Reproduction only on C2. `git_commit` is empty on these result files (pre-repo).

C2 vs C0/C1 is **not** “decision function only.” C2 may birth; C0 and C1 may not.

`time_to_first_birth` / `max_generation` are blank in this batch’s `metrics.csv` (those columns were added after the run). Birth counts and the C2 histogram are still valid. Generation numbers for C2 come from `ablation_c1r_100x1000`, whose C2 clones are identical.

## What the numbers show

- **C0** is a dead controller on this horizon: 0/100 alive, median TTE 105, almost no food.
- **C1** is a stable non-reproducing forager: 97/100 alive, mean pop 2.72, mean food 276, **zero births** (by construction). Three extinctions (seeds 46, 59, 86) are the exception, not the rule.
- **C2** is usually extinct: 6/100 alive, 32/100 any birth, mean births 0.99, mean food 25. Median TTE among the extinct is 129.5 — most of the 94 deaths happen early, not at the 1000-tick wall.
- C2 births are a **lottery tail**, not a typical trajectory: 68 seeds never birth, 22 birth exactly once, 10 birth twice or more. Seed 3 is the boom (23 births, pop 7). The other five survivors are thin (pop 1–3).
- Paired Δ: C1 ≫ C0 on survival, food, energy. C2 ≫ C0 only on births (because C0 cannot birth) and is far behind C1 on everything that is not “did a birth event fire.”

## What they do not show

- Not emergence. Not intelligence. Not “6% of genomes evolve.”
- Not that the world cannot support generations (that test is C1-R).
- Not that extra seeds at 1000 ticks would make typical C2 successful. The rate is a property of the lottery; more tickets find more seed-3-like hits for case study, they do not move the median.

## Decision

Keep the six C2 survivor seeds (3, 16, 40, 88, 92, 99) as named follow-ups. Do not retune food or mutation from this batch. Read `ablation_c1r_100x1000` before changing the world.
