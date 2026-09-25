# Emergence Lab

Minimal artificial-life laboratory: **one world, one body, one observation, one action space — swap only the decision controller.**

This is a **mechanistic artificial-life model, not a biological model**. Its scientific value is in the consequences of the specified computational rules, not in biological realism.

Normative rules live in [`spec.md`](spec.md). Milestone 1 is implemented (world, C0–C2, logging, replay, GIFs, analytics). Milestone 2 **C3** (LLM) and **C4** (LLM + per-organism `list[str]` memory) are implemented. Milestone 3 **C5** (LLM + genome + births) is measured on `qwen3.8:27b` (A/B). **C6** (C5 + memory) is implemented; no C6 batch yet. Model name, endpoint, temperature, and prompt id are **config/CLI only — never hardcoded**.

## Research question

How much complex and candidate-emergent behaviour can arise from a very small digital world, and how does that behaviour change when the **controller configuration** of individuals is replaced?

The experimental intervention is the controller configuration. Other world and organism mechanics stay constant unless an ablation says otherwise.

Controllers share the same **raw** 5×5 observation. They do not share the same **effective representation**. C1 reasons over full local resource geometry (including diagonals) with a built-in food prior. C2 is a linear policy over 9 features: four cardinal resource bits (N1 and N2 are one bit), four organism bits, and a bias. Diagonal-only food is invisible to C2 (same features as an empty patch). That bottleneck is part of the C2 condition. Do not expand C2 features because C2 failed; a denser C2 is a later named experiment.

Reproduction is **not** a universal world rule in the main matrix. C2, C5, and C6 may reproduce; C0, C1, C3, and C4 may not. Do not read C2 vs C0 (or C5 vs C3) as “only the decision function changed.” Those comparisons mix genetic evolution with population dynamics. Ablations: **C0-R** (`random_r`) and **C1-R** (`reactive_r`) — same decision class, reproduction on, no genome. Diagnostic (not in the main matrix): **C2-oracle** (`evolutionary_oracle` / `evolutionary_oracle_r`) — same 9 features, fixed cardinal genome, no mutation. A later **C2-diag** (diagonal features) is a new experiment version, not an edit of v0.1 C2.

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

C1 has a food-seeking objective. **C3-A does not**. C3-B / C4-B / C5-B / C6-B are survival-instructed ablations, not new matrix IDs. C4 is C3 plus optional `MEMORY:` writes. C5 is C3 plus genome-in-prompt and C2 births. **C6 is C5 + C4 memory**; memory is **never inherited** (only the mutated genome passes to children). Do not read C4−C3, C5−C3, or C6−C5 as single-factor contrasts. C2-oracle cannot see diagonal food; expanding C2 features is **C2-diag**, a later named experiment.

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

Tracked reports: [`docs/lab_log.md`](docs/lab_log.md) and [`experiments/reports/`](experiments/reports/). Economy **m1-v2** is frozen. C5-A food **56**; C5-B **12/20 alive**, food **23**. C6-A: **20/20 alive**, food **59** (≈ C5-A), memory writes **~49%**. Next: C6-B; parallel **C2-diag** (`evolutionary_diag*`).

Later, if a candidate pattern appears, extra Python tests (permutation, survival curves, genome/lineage on hits) can argue it is not a controller bias. Those are **not** in the default summarize path. Descriptive stats stay automatic; causal claims stay manual.

## C3 — local LLM (Ollama)

C3 is a **decision adapter**. The simulator does not know the model. Model tag, endpoint, temperature, and prompt id come from config or CLI (`--llm-model`, `--prompt-id`). There is **no inference cache**. Wall-clock latency is not sim time. Parse failure → `INVALID_ACTION` + `STAY`; raw output is stored in `LLM_CALL` events. Thinking traces are disabled (`think: false`) and `<think>` tags are stripped before parse.

Controllers: `llm` / `llm_a` (prompt A: choose one of NORTH/SOUTH/EAST/WEST/STAY from the observation only) and `llm_b` (same action list, plus a stay-alive instruction). No genome, no reproduction, no memory. Each model tag is its own `experiment_id`. Changing prompt or model while reusing an id will **resume** and skip finished seeds.

Survival at a fixed tick is not the only C3 metric. Report food consumed, action distribution, invalid-action rate, and time-to-extinction. C3-A and C1 share the raw 5×5, not a food objective: C1 has a hard-coded prior; C3-A does not. Harvest rates can still match, as with `qwen3.8:27b`.

Cost: **10 organisms × ticks sequential HTTP calls** per seed. Interrupted batches resume if `seed_N/metrics.csv` exists.

### Models

| Ollama tag | Role |
| --- | --- |
| `qwen2.5:7b` | C3-A and C3-B, seeds 1–20 × 200 ticks — STAY, 0/20 alive |
| `qwen3.8:27b` | C3-A/B: food ≈ C1 (86 / 82). C4-A: food **70**. C4-B: food **35**. C5-A: food **56**, births 100%. C5-B: **12/20 alive**, food **23**, STAY-heavy |

Further tags are in-scope as later named batches, not silent swaps.

On `qwen2.5:7b`, both prompts are **STAY** policies (food 1.6 / 1.3 vs C0 7.2 vs C1 83). On `qwen3.8:27b`, A and B both persist 20/20 with food **86 / 82** (ties with C1 83); sampled logs are EAST-dominant (entropy ~1.0 vs C1 ~2.3). B does not switch 27B to STAY; end energy is lower (664 vs A 924). Same prompts, different model. Numbers: [`docs/lab_log.md`](docs/lab_log.md), [`c3a_qwen25_7b_20x200`](experiments/reports/c3a_qwen25_7b_20x200/), [`c3b_qwen25_7b_20x200`](experiments/reports/c3b_qwen25_7b_20x200/), [`c3a_qwen38_27b_20x200`](experiments/reports/c3a_qwen38_27b_20x200/), [`c3b_qwen38_27b_20x200`](experiments/reports/c3b_qwen38_27b_20x200/).

```bash
# Requires a running Ollama daemon.
python -m emergence_lab batch \
  --experiment-id c3a_qwen25_7b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm \
  --llm-model qwen2.5:7b \
  --prompt-id llm_a

python -m emergence_lab batch \
  --experiment-id c3b_qwen25_7b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_b \
  --llm-model qwen2.5:7b

python -m emergence_lab batch \
  --experiment-id c3a_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a

python -m emergence_lab batch \
  --experiment-id c3b_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_b \
  --llm-model qwen3.8:27b
```

## C4 — LLM + memory

C4 is C3 plus a per-organism `list[str]` (cap 20, 200 chars, FIFO, not inherited). The LLM may append one `MEMORY:` line per decision, including on invalid/fallback. Writes apply at end of tick T and are visible in `decide` from T+1. No embeddings, no RAG. Empty / omitted `MEMORY:` = no write.

Controllers: `llm_memory` / `llm_a_memory` (prompt A + memory) and `llm_b_memory` (prompt B + memory). Same action list as C3; the extra instruction is optional persistence, not a food objective. C4 prompts are longer than C3 even with empty memory.

Default `num_predict` for C4 configs is 128 (C3 stays 64) so a short memory line is not truncated by the sampler.

On `qwen3.8:27b` prompt A, C4 persists 20/20 with mean food **70** vs C1 83 vs C3-A 86 (paired vs C1: Δ −12.8, CI excludes 0). Writes are rare (mean 17 / run, 1.3% of calls). Prompt B on the same maps: food **35**, pop 1.80, writes **20%** of calls (paired vs C1: Δ −48.6, 0/20). Numbers: [`c4a_qwen38_27b_20x200`](experiments/reports/c4a_qwen38_27b_20x200/), [`c4b_qwen38_27b_20x200`](experiments/reports/c4b_qwen38_27b_20x200/).

```bash
# Requires a running Ollama daemon.
python -m emergence_lab batch \
  --experiment-id c4a_qwen38_27b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_memory \
  --llm-num-predict 128

python -m emergence_lab batch \
  --experiment-id c4a_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_memory \
  --llm-num-predict 128

python -m emergence_lab batch \
  --experiment-id c4b_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_b_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_b_memory \
  --llm-num-predict 128
```

## C5 — LLM + evolution

C5 is C3 plus the C2 genome (45 weights, 9 features × 5 actions) as compact prompt context, with C2 reproduction and mutation. The LLM remains the decision maker: the genome **does not require any action** (no argmax instruction, no “seek food”). Same mutation probability, strength, and init range as C2. No memory (that is C6).

Controllers: `llm_evolution` / `llm_a_evolution` (prompt A + genome) and `llm_b_evolution` (prompt B + genome). The genome dump is five action lines plus C2 feature names (`resource_N` … `bias`). `num_predict` stays 64 (output is still one action token).

Do not read C5−C3 as “only evolution.” C5 has births, mutation, a longer prompt, and population dynamics. Births also mean more LLM calls than a same-tick C3/C4 run. Same-seed C2 and C5 clones share founder genomes (evolution RNG after layout).

On `qwen3.8:27b` prompt A, C5 persists 20/20 with mean food **56** vs C1 83 vs C3-A 86 vs C4-A 70 (paired vs C1: Δ −27, CI excludes 0). Every seed births (mean 3.7); median max generation is **1**. Energy **280**. Entropy **1.90** (more STAY/mix than C3-A). Prompt B on the same maps: **12/20 alive**, food **23**, med pop 1, entropy **0.77** (STAY-dominant) — first 27B matrix condition that fails full persistence. Numbers: [`c5a_qwen38_27b_smoke`](experiments/reports/c5a_qwen38_27b_smoke/), [`c5a_qwen38_27b_20x200`](experiments/reports/c5a_qwen38_27b_20x200/), [`c5b_qwen38_27b_smoke`](experiments/reports/c5b_qwen38_27b_smoke/), [`c5b_qwen38_27b_20x200`](experiments/reports/c5b_qwen38_27b_20x200/).

```bash
# Requires a running Ollama daemon. Keep the GPU exclusive (C4-B seed 11 was killed by another local job).
python -m emergence_lab batch \
  --experiment-id c5a_qwen38_27b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm_evolution \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_evolution

python -m emergence_lab batch \
  --experiment-id c5a_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_evolution \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_evolution

python -m emergence_lab batch \
  --experiment-id c5b_qwen38_27b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm_b_evolution \
  --llm-model qwen3.8:27b \
  --prompt-id llm_b_evolution

python -m emergence_lab batch \
  --experiment-id c5b_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_b_evolution \
  --llm-model qwen3.8:27b \
  --prompt-id llm_b_evolution
```

C5 A/B on 27B is closed.

## C6 — LLM + evolution + memory

C6 is C5 plus C4 memory: genome-in-prompt, C2 births/mutation, and optional `MEMORY:` writes (visible T+1, cap 20, FIFO). Controllers: `llm_evolution_memory` / `llm_a_evolution_memory` (A) and `llm_b_evolution_memory` (B). Default `num_predict` 128.

**Memory is never inherited.** Children start with an empty list; only the mutated genome is passed on. Do not expect “parent notes → child policy.”

Do not read C6−C5 as a pure memory effect (longer prompt + write option) or C6−C3 as pure evolution+memory.

```bash
# Requires a running Ollama daemon. Keep the GPU exclusive.
python -m emergence_lab batch \
  --experiment-id c6a_qwen38_27b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm_evolution_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_evolution_memory \
  --llm-num-predict 128
```

No 20×200 until that smoke exists.

On `qwen3.8:27b` prompt A, C6 persists 20/20 with mean food **59** vs C1 83 vs C5-A 56 vs C4-A 70. Memory writes **~49%** of decisions (vs C4-A 1.3%) without lifting harvest above C5-A. Births 90%; median max generation 1. Numbers: [`c6a_qwen38_27b_smoke`](experiments/reports/c6a_qwen38_27b_smoke/), [`c6a_qwen38_27b_20x200`](experiments/reports/c6a_qwen38_27b_20x200/).

```bash
python -m emergence_lab batch \
  --experiment-id c6a_qwen38_27b_20x200 \
  --seeds 1-20 \
  --ticks 200 \
  --controllers random,reactive,llm_evolution_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_a_evolution_memory \
  --llm-num-predict 128

# Next ablation: C6-B
python -m emergence_lab batch \
  --experiment-id c6b_qwen38_27b_smoke \
  --seeds 1 \
  --ticks 50 \
  --controllers random,reactive,llm_b_evolution_memory \
  --llm-model qwen3.8:27b \
  --prompt-id llm_b_evolution_memory \
  --llm-num-predict 128
```

**C2-diag** (diagonal linear features) is a separate named experiment — see below. Do not edit v0.1 C2 features in place.

## C2-diag — named experiment (not matrix C2)

Same frozen m1-v2 and linear argmax, but **17 features** (cardinal + diagonal resource/organism bits + bias) → **85** genome weights. Controllers: `evolutionary_diag` (evolved), `evolutionary_diag_oracle` / `evolutionary_diag_oracle_r` (fixed diag-oracle: cardinal food → that move; diagonal food ties the two adjacent cardinals). v0.1 C2 (`evolutionary`, 9 features / 45 weights) is unchanged.

```bash
# Non-LLM; can run while GPU is busy with C6-B, or after.
python -m emergence_lab batch \
  --experiment-id c2diag_oracle_100x1000 \
  --seeds 1-100 \
  --ticks 1000 \
  --controllers reactive,evolutionary,evolutionary_diag,evolutionary_diag_oracle,evolutionary_diag_oracle_r
```

Compare on the same seeds as the Milestone-1 C2 batches. Do not retune food, regen, mutation, or init.

## Project layout

```text
src/emergence_lab/          simulator, analytics, visualization, llm adapter
docs/lab_log.md             chronological interpretation (tracked)
experiments/configs/        YAML configs (`c3_ollama.yaml` … `c6_ollama.yaml`)
experiments/results/        raw runs (gitignored)
experiments/reports/        aggregate.md + CSVs + NOTES (tracked)
tests/                      world, invariants, verification controllers, replay, C3–C6 parse
spec.md                     implementation specification
```
