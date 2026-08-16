# Notes — `ablation_c0r_100x1000`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-16

## What this batch is

Same seeds 1–100, 1000 ticks, frozen m1-v2. Clones of **C0**, **C0-R** (`random_r`: random decisions, reproduction ON, no genome), and **C1-R**. Git `0deb1f9c08314363dcf9643f6348fdb8d6c1d8a8`.

Question: is C1-R’s multi-generation ecology “births exist”, or “greedy foraging + births”?

## What the numbers show

- **C0-R does not persist.** 0/100 alive. 6/100 have exactly one birth (seeds 7, 26, 48, 55, 86, 94); none reach generation 2. Median TTE 103.5, same order as C0 (105).
- On the 94 maps with no birth, C0 and C0-R are identical. Reproduction never fires, so the extra flag does nothing.
- The six births slightly *shorten* TTE (mean Δ −2.2 vs C0). Paying 75 energy without better foraging is a tax.
- **C1-R is the same clone as `ablation_c1r_100x1000`:** 95% alive, mean pop 8.48, mean births 38.4, mean max generation 7.17. Same five extinctions.
- Against earlier C2 on these maps: C2 any-birth 32% > C0-R 6%, but C2 still fails to persist (0/100 at 10k). Random-init linear policies hit the birth loop more often than a random walk, and still do not keep it.

## What they do not show

- Not that reproduction is useless. It is useless *without a policy that can harvest*.
- Not emergence. Not that C2 should be retuned toward C1.
- Not a new ecology: C1-R numbers match the previous ablation.

## Decision

Keep m1-v2 frozen. The M1 C0/C1/C2 ablation story is complete: greedy without births survives; random with births dies; greedy with births runs generations; C2 flashes and dies.

Do not add seeds or ticks for C2. Next matrix cell is **C3** (LLM, no memory, no reproduction) on this frozen world — milestone 2 — or stop and write up. Do not hunt food/mutation/init.
