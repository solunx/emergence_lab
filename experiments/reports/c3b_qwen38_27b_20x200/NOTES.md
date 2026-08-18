# Notes — `c3b_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-18

## What this batch is

C3-B model variant. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C3-B (`qwen3.8:27b`, prompt B: remain alive, then pick NORTH/SOUTH/EAST/WEST/STAY). Same maps as `c3a_qwen38_27b_20x200`. Git `1fd55fe`.

Question: on the model that already forages under prompt A, does “remain alive” pull the phenotype toward STAY, or keep the eastward sweep?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-A 7B (other batch) | 0% | 1.6 | 0 | 0 | 0.37 |
| C3-B 7B (other batch) | 0% | 1.3 | 0 | 0 | 0.16 |
| C3-A 27B (other batch) | 100% | 86.0 | 5.0 | 924 | 0.99 |
| C3-B 27B llm_b | **100%** | **82.4** | **4.0** | **664** | **0.99** |

- 20/20 alive. Pop 3–7 (C1: 3–8). Food 61–111 (C1: 52–118). Invalid 0. ~910–960 ms/call.
- Paired vs C1: food Δ **−0.75**, CI [−9.3, +7.8] (9/20 higher, 11/20 lower) — a **tie**. Pop Δ −0.55, CI includes 0. Survival 20/20 equal.
- Vs C3-A 27B on the same maps: food 82 vs 86; entropy both ~0.99. Not a second phenotype.
- Sampled action logs stay EAST-dominant, but B uses a little **STAY and WEST** (A had STAY=0, WEST≈0). “Remain alive” did not turn 27B into the 7B STAY policy.
- End energy is the B-specific gap: 664 vs C1 846 (Δ **−182**, CI under 0, 15/20 poorer) and vs A 924. Similar harvest, thinner cash.
- C0/C1 clones match the earlier 20×200 batches.

## What they do not show

- Not that prompt B unlocks foraging. On 7B it tightened STAY; on 27B it barely moves the A phenotype.
- Not that 27B-B *is* C1. Same harvest class, different mix, lower final energy.
- Not 1000-tick persistence. Not emergence. Not an intelligence score. Not a reason to rewrite A/B in place.
- n=20 is enough to say “B is not the 27B failure mode and not a STAY switch”; not for rare events.
- The aggregate line “No non-reactive survivors” is a summarize artefact: the LLM also survived.

## Decision

C3 on 7B/27B × A/B is done. Do not retune the world or rewrite prompts to rescue 7B. Next is **C4 (LLM + Memory)** on `qwen3.8:27b` prompt A — the phenotype that already handles this world — after the write path exists. 7B-C4 is a later variant, not the first C4 batch.
