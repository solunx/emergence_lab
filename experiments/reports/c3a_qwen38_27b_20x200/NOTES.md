# Notes — `c3a_qwen38_27b_20x200`

Numbers live in `aggregate.md` (generated, do not edit). This file is interpretation only.

A visually interesting GIF is not evidence of emergence.

**Status:** interpreted 2026-08-17

## What this batch is

C3-A model variant. Seeds 1–20, 200 ticks, m1-v2. Clones of C0 / C1 / C3-A (`qwen3.8:27b`, prompt A). Same maps as `c3a_qwen25_7b_20x200`. Git `e6d17a94`.

Question: with prompt A held fixed, does a larger local model still STAY, or does it persist and forage?

## What the numbers show

| Controller | Alive | Mean food | Med pop | Mean energy | Action entropy |
|---|---:|---:|---:|---:|---:|
| C0 random | 0% | 7.2 | 0 | 0 | ~2.32 |
| C1 reactive | **100%** | 83.2 | 5.0 | 846 | ~2.31 |
| C3-A 7B (other batch) | 0% | 1.6 | 0 | 0 | 0.37 |
| C3-A 27B llm | **100%** | **86.0** | **5.0** | **924** | **0.99** |

- 20/20 alive. Pop 3–6 (C1: 3–8). Food 56–127 (C1: 52–118). Invalid 0.
- Paired vs C1: food Δ +2.8, CI [−5.5, +11.1] (10/20 higher, 10/20 lower) — a **tie**. Pop Δ −0.40, CI includes 0. Vs C0: 20/20 on pop, food, survival.
- C0/C1 clones match the 7B batches.
- Seed 1 continues the smoke: 50 ticks → 29 food / pop 6; 200 ticks → **94 food / pop 4** (C1 on that map: 60 / 3).
- Phenotype is **not** C1. Entropy ~1.0 vs ~2.3. Sampled action logs: mostly EAST, some N/S, WEST ≈ 0, **STAY = 0**. On a torus that eastward sweep plus N/S correction harvests like C1 without the same action mix. Always-MOVE also explains slightly more deaths than C1.
- 7B on the same prompt was STAY until the energy horizon. C3-A is **model-dependent**.

## What they do not show

- Not that prompt A secretly contains a food objective. C1 has that prior; 27B inferred something from the 5×5 (or has an EAST default that hits patches). Same text, different weights.
- Not that 27B *is* C1. Different policy, similar harvest on this world.
- Not 1000-tick persistence (C1 was 97% there). Not C3-B on 27B. Not emergence. Not an intelligence score.
- n=20 is enough for 7B vs 27B and “not worse than C1 on food”; not for rare events.
- The aggregate line “No non-reactive survivors” is a summarize artefact: the LLM also survived.

## Decision

Do not retune the world or rewrite prompt A. Next is **C3-B on `qwen3.8:27b`**, same seeds (`c3b_qwen38_27b_20x200`): does “remain alive” pull this phenotype toward STAY, or keep the eastward sweep?
