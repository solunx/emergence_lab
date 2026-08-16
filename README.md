# Emergence Lab

Minimal artificial-life laboratory: **one world, one body, one observation, one action space — swap only the decision controller.**

This is a **mechanistic artificial-life model, not a biological model**. Its scientific value is in the consequences of the specified computational rules, not in biological realism.

Normative rules live in [`spec.md`](spec.md). Milestone 1 is implemented (world, C0–C2, logging, replay, GIFs, analytics). Milestone 2 **C3** is implemented: a local Ollama LLM as the decision function. Model name, endpoint, temperature, and prompt id are **config/CLI only — never hardcoded**. C4 (memory) is not built yet.

## Research question

How much complex and candidate-emergent behaviour can arise from a very small digital world, and how does that behaviour change when the **controller configuration** of individuals is replaced?

The experimental intervention is the controller configuration. Other world and organism mechanics stay constant unless an ablation says otherwise.

Controllers share the same **raw** 5×5 observation. They do not share the same **effective representation**. C1 reasons over full local resource geometry (including diagonals) with a built-in food prior. C2 is a linear policy over 9 features: four cardinal resource bits (N1 and N2 are one bit), four organism bits, and a bias. Diagonal-only food is invisible to C2 (same features as an empty patch). That bottleneck is part of the C2 condition. Do not expand C2 features because C2 failed; a denser C2 is a later named experiment.

Reproduction is **not** a universal world rule in the main matrix. C2 may reproduce; C0 and C1 may not. Do not read C2 vs C0 as “only the decision function changed.” That comparison mixes genetic evolution with population dynamics. Ablations: **C0-R** (`random_r`) and **C1-R** (`reactive_r`) — same decision class, reproduction on, no genome. Diagnostic (not in the main matrix): **C2-oracle** (`evolutionary_oracle` / `evolutionary_oracle_r`) — same 9 features, fixed cardinal genome, no mutation.

## Experimental matrix (v0.1)

| ID | Controller | Genome | Memory | Reproduction | Milestone |
| --- | --- | --- | --- | --- | --- |
| C0 | Random (random-controller baseline) | No | No | No | 1 |
| C0-R | Random + reproduction (`random_r`) | No | No | Yes | 1 ablation |
| C1 | Reactive (hand-coded food seeking) | No | No | No | 1 |
| C1-R | Reactive + reproduction (`reactive_r`) | No | No | Yes | 1 ablation |
| C2 | Evolutionary | Yes | No | Yes | 1 |
| C2-oracle | Fixed cardinal genome, C2 features (`evolutionary_oracle`) | No | No | No | 1 diagnostic |
| C3 | LLM | No | No | No | 2 |
| C4 | LLM + Memory | No | Yes | No | 2 |
| C5 | LLM + Evolution | Yes | No | Yes | 3 |
| C6 | LLM + Evolution + Memory | Yes | Yes | Yes | 3 |

C1 has a food-seeking objective. **C3-A does not** (prompt: pick NORTH/SOUTH/EAST/WEST/STAY from the 5×5 only). They share information, not the same inductive bias. C3-B is a survival-instructed ablation (`llm_b`), not a new matrix ID. C2-oracle is not a C1 clone: it cannot see diagonal food.

Local model **variants are in-scope**. Each Ollama tag is a different `experiment_id` (e.g. `c3a_qwen25_7b` vs `c3a_qwen38_27b`). Do not silently swap models inside one batch.

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

C1 vs C2 is not “same eyes, different brain.” Quantify the feature bottleneck, then test a hand-set cardinal genome on the frozen world (same maps 1–100). Do not retune food or C2 features.

```bash
python -m emergence_lab representability

python -m emergence_lab batch \
  --experiment-id diag_c2_oracle_100x1000 \
  --seeds 1-5 \
  --ticks 1000 \
  --controllers reactive,evolutionary_oracle,evolutionary

python -m emergence_lab batch \
  --experiment-id diag_c2_oracle_100x1000 \
  --seeds 1-100 \
  --ticks 1000 \
  --controllers reactive,evolutionary_oracle,evolutionary
```

`reactive` vs `evolutionary_oracle`: can the C2 phenotype forage without evolution? `evolutionary_oracle` vs `evolutionary`: can random-init evolution match that phenotype? If the oracle lives like C1, follow up with births held fixed:

```bash
python -m emergence_lab batch \
  --experiment-id diag_c2_oracle_r_100x1000 \
  --seeds 1-100 \
  --ticks 1000 \
  --controllers reactive_r,evolutionary_oracle_r,evolutionary
```

Tracked reports: [`docs/lab_log.md`](docs/lab_log.md) and [`experiments/reports/`](experiments/reports/). Economy **m1-v2** is frozen (food +30, regen 15). M1 C0/C1/C2 + oracle diagnostics are done. Next is **C3-A** on the same frozen world — small N first, then model variants. Not more C2 lottery tickets, not expanding C2 features in place.

Later, if a candidate pattern appears, extra Python tests (permutation, survival curves, genome/lineage on hits) can argue it is not a controller bias. Those are **not** in the default summarize path. Descriptive stats stay automatic; causal claims stay manual.

## C3 — local LLM (Ollama)

C3 is a **decision adapter**. The simulator does not know the model. There is **no inference cache** (that would turn C3 into a lookup table). Wall-clock latency is not sim time. Parse failure → `INVALID_ACTION` + `STAY`; raw output is always kept in `LLM_CALL` events.

Need a running Ollama daemon. Controllers: `llm` / `llm_a` (prompt A, default) and `llm_b` (survival prompt). No genome, no reproduction.

Survival at a fixed tick is **not** the only C3 metric. Also look at food consumed, action distribution, invalid-action rate, time-to-extinction, and whether actions point toward visible food. C3-A matching C1 would be surprising (C1 has a food prior; C3-A does not).

```bash
# Smoke: one seed, few ticks, a small local model. Ollama must be up.
python -m emergence_lab batch \
  --experiment-id c3a_qwen25_7b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm \
  --llm-model qwen2.5:7b \
  --prompt-id llm_a

# After smoke: still small N (20–50 seeds, 200–1000 ticks), model tag in the id.
python -m emergence_lab batch \
  --experiment-id c3a_qwen25_7b_50x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm \
  --config experiments/configs/c3_ollama.yaml \
  --llm-model qwen2.5:7b
```

Cost: **10 organisms × ticks sequential HTTP calls** per seed. A 32B model on every tick is a long wall-clock run. Smoke with 7B/8B first.

### RTX 3090 (24 GB) — which Qwen3.8?

Community + Ollama library (mid-August 2026): **`qwen3.8:27b`** (alias `qwen3.8:latest`), default **Q4_K_M ~18 GB**. That is the 24 GB sweet spot: weights fit, ~6 GB left for KV cache at normal C3 context (the prompt is a 5×5, not 128K). Command once you are ready: `ollama pull qwen3.8:27b`. Needs Ollama **≥ 0.32.12**.

| Card budget | Tag / quant | Notes |
| --- | --- | --- |
| 3090 24 GB (recommended) | `qwen3.8:27b` Q4_K_M | Official default; intended 24 GB home |
| 3090, more quality, short context | Q5_K_M (~20 GB) | Tight; keep `num_predict` small |
| 3090, do **not** | Q8_0 (~29 GB) | Offload / thrash |
| C3 **smoke** (now) | `qwen2.5:7b` or `llama3.1:8b` | Already on disk; cheap sequential calls |

Qwen3.8 has **thinking on by default**. The lab sends `think: false` and strips `<think>` before parse. Do not treat chain-of-thought as inner reasoning.

You already have several 14B–32B tags (`qwen2.5:32b`, `qwen3:32b`, `qwen3.5:27b`, `mistral-small:24b`, `gemma3:27b`, …). Those are valid **later variants**, each with its own `experiment_id`. Do not make 32B the C3-A default: sequential calls are slow, and smoke should stay cheap. Waiting for community quant feedback is reasonable; the default 27B Q4 is still the one I would pull for a 3090.

## Project layout

```text
src/emergence_lab/          simulator, analytics, visualization, llm adapter
docs/lab_log.md             chronological interpretation (tracked)
experiments/configs/        YAML configs (including `c3_ollama.yaml`)
experiments/results/        raw runs (gitignored)
experiments/reports/        aggregate.md + CSVs + NOTES (tracked)
tests/                      world, invariants, verification controllers, replay, C3 parse
spec.md                     implementation specification
```
