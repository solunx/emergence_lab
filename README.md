# Emergence Lab

Minimal artificial-life laboratory: **one world, one body, one observation, one action space — swap only the decision controller.**

This is a **mechanistic artificial-life model, not a biological model**. Its scientific value is in the consequences of the specified computational rules, not in biological realism.

Normative rules live in [`spec.md`](spec.md). Milestone 1 is implemented: world, C0 random, C1 reactive, C2 evolutionary, logging, replay, GIFs, and offline analytics. No LLM dependency.

## Research question

How much complex and candidate-emergent behaviour can arise from a very small digital world, and how does that behaviour change when the **controller configuration** of individuals is replaced?

The experimental intervention is the controller configuration. Other world and organism mechanics stay constant unless an ablation says otherwise.

Reproduction is **not** a universal world rule in the main matrix. C2 may reproduce; C0 and C1 may not. Do not read C2 vs C0 as “only the decision function changed.” That comparison mixes genetic evolution with population dynamics. Ablations: **C0-R** (`random_r`) and **C1-R** (`reactive_r`) — same decision class, reproduction on, no genome.

## Experimental matrix (v0.1)

| ID | Controller | Genome | Memory | Reproduction | Milestone |
| --- | --- | --- | --- | --- | --- |
| C0 | Random (random-controller baseline) | No | No | No | 1 |
| C0-R | Random + reproduction (`random_r`) | No | No | Yes | 1 ablation |
| C1 | Reactive (hand-coded food seeking) | No | No | No | 1 |
| C1-R | Reactive + reproduction (`reactive_r`) | No | No | Yes | 1 ablation |
| C2 | Evolutionary | Yes | No | Yes | 1 |
| C3 | LLM | No | No | No | 2 |
| C4 | LLM + Memory | No | Yes | No | 2 |
| C5 | LLM + Evolution | Yes | No | Yes | 3 |
| C6 | LLM + Evolution + Memory | Yes | Yes | Yes | 3 |

C1 has a food-seeking objective. C3-A will not. They share information, not the same inductive bias.

## What counts as evidence

A behaviour is a **candidate** emergent phenomenon when it is a persistent system-level pattern that is **not** encoded as a global rule in the controller or the environment, and that **replicates across seeds**.

Pipeline: visual observation → quantitative metric → cross-seed replication → ablation.

Comparisons are **paired by seed** (same-world clones):

```text
Δ_i = metric(C2, seed_i) − metric(C0, seed_i)
```

Report median, mean, sd, confidence interval, and effect size of Δ. 100 seeds is an initial budget, not a magic sample size.

## What does NOT count as evidence

- **A visually interesting GIF is not evidence of emergence. It is a hypothesis-generating observation.**
- One run, one seed, or anecdotal clustering
- A pattern already written into the controller (C1 walking toward visible food)
- LLM self-reported rationales (those are model outputs, not inner reasoning)
- “C2 is smarter” or any intelligence score

## World (Milestone 1, economy m1-v2)

- 32×32 **torus**, one organism per cell
- Simultaneous decisions: all actions on tick T use world state T
- 20 fixed food patches, cooldown regen, **no spawn under an organism**
- Actions: N / S / E / W / STAY. STAY costs 1, MOVE costs 2, food is **+30**
- `regen_delay = 15` (was 25). A single-patch harvest cycle is then energy-positive (~+13), so reproduction is reachable
- Egocentric 5×5 observation: no global coordinates, no agent IDs
- Movement conflicts: hash lottery, not energy, not ID
- Seeds vs clones: seed 1 and seed 77 are different maps; clones of seed 1 start from the same tick-0 snapshot

## Install

Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## How to reproduce

```bash
pytest

# Same-world clones of C0, C1, C2
python -m emergence_lab compare --seed 123456 --ticks 1000 --gif --invariants
```

Each compare writes a **new** folder:

```text
experiments/results/compare_seed123456_ticks1000_<timestamp>/
```

Per-controller run directories are also timestamped. Raw events, snapshots, `metrics.csv`, and GIFs are not overwritten.

Comparison GIFs show three panels with **white gutters**, **controller labels**, and a **tick / population** banner.

Replay and GIFs are built from stored events plus the tick-0 snapshot, not by re-simulating:

```bash
python -m emergence_lab gif path/to/run_dir
```

One command runs a seed range, creates folders, writes stats, and publishes reports. Interrupted batches **resume** (skip `seed_N` if `metrics.csv` exists). After the numbers exist, the only manual step is interpretation in `NOTES.md` and `docs/lab_log.md`.

```bash
python -m emergence_lab batch \
  --experiment-id ablation_c0r_100x1000 \
  --seeds 1-100 \
  --ticks 1000 \
  --controllers random,random_r,reactive_r
```

That writes `experiments/results/<experiment-id>/seed_N/` (gitignored) and copies `aggregate.md` plus CSVs into `experiments/reports/<experiment-id>/`. Stubs for `NOTES.md` and the lab log are created if missing and **never overwritten**.

Use `--seeds 1-5` as a smoke run first. `--force` re-runs a seed that already has metrics. `--no-publish` keeps stats next to the batch only. Single-seed debug remains `compare`.

Tracked reports: [`docs/lab_log.md`](docs/lab_log.md) and [`experiments/reports/`](experiments/reports/). Economy **m1-v2** is frozen (food +30, regen 15). M1 C0/C1/C2 ablations are done. Next matrix cell is C3 on this frozen world (milestone 2), or a write-up — not more C2 lottery tickets, not retuning food.

Later, if a candidate pattern appears, extra Python tests (permutation, survival curves, genome/lineage on hits) can argue it is not a controller bias. Those are **not** in the default summarize path. Descriptive stats stay automatic; causal claims stay manual.

## Project layout

```text
src/emergence_lab/          simulator, analytics, visualization
docs/lab_log.md             chronological interpretation (tracked)
experiments/configs/        YAML configs
experiments/results/        raw runs (gitignored)
experiments/reports/        aggregate.md + CSVs + NOTES (tracked)
tests/                      world, invariants, verification controllers, replay
spec.md                     implementation specification
```
