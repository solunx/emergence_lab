# Notes — `persist_c2_c1r_100x10000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-15

## What this batch is

Same seeds 1–100, frozen m1-v2, clones of **C1-R** and **C2**, **10000 ticks**. Git `0deb1f9c08314363dcf9643f6348fdb8d6c1d8a8`.

Pre-registered question: do the six C2 hits from 1000 ticks persist, and does C1-R stay up on the same maps?

## What the numbers show

- **C2: 0/100 alive.** Median TTE 134; longest extinction is seed 92 at tick 1946. Nobody reaches 2000.
- The 1000-tick “survivors” (3, 16, 40, 88, 92, 99) were flashes. All dead by 1946. Seed 3 (the boom: 23 births, pop 7 at tick 1000) dies at 1423 with 29 births and max generation 8.
- Extra time does **not** recruit new C2 birth loops. Any-birth stays 32%. Birth histogram still `{0: 68, 1: 22, …}`; only the existing tail adds a few births. Latest C2 first birth is tick 224.
- **C1-R can support long lineages** on this economy: mean 332 births, mean max generation 46 (max 87), median first birth 4. Survival falls 95% → 68% (32 late extinctions, median TTE ~4107). Greedy+births is persistent on most maps, boom-bust on some — not immortal.
- Paired, same seed: C2 loses on pop/food/generation on ~98–100/100 maps. The 32 survival ties are maps where C1-R also died.

## What they do not show

- Not emergence. Not intelligence. Not “C2 works 6% of the time.”
- Not that the ecology is dead (C1-R mean generation 46).
- Not that more 1000-tick seeds, or 50k ticks, would make typical C2 persist. The mechanism is early failure, not a slow climb.
- Not genome *direction*. BIRTH events do not log weights; typical C2 has 0–1 births. Seed 3’s generation-8 flash is not a selection time series.

## Decision

Keep m1-v2 frozen. Do not retune C2 mutation, init, food, or threshold to look better.

Next observation: **C0-R** (`random_r`) on the same maps — reproduction on, random decisions, no genome — to separate “births exist” from “greedy foraging + births.” Do not start C3 until that control exists. Do not implement the emergence-stats checklist; there is still no candidate.
