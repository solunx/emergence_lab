# Aggregate results — `c6a_qwen38_27b_20x200`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **20**
- controller-runs: **60**
- ticks: **200**
- controllers: random, reactive, llm_evolution_memory

## Parameters

From **60** `metadata.json` file(s). Shared world fields should be identical across clones; seed and controller differ by design.

### World

| Parameter | Value |
|---|---|
| `width` | 32 |
| `height` | 32 |
| `torus` | yes |

### Resources

| Parameter | Value |
|---|---|
| `resource_count` | 20 |
| `resource_value` | 30 |
| `regen_delay` | 15 |
| spawn under organism | no |

### Population

| Parameter | Value |
|---|---|
| `initial_population` | 10 |

### Organism / energy

| Parameter | Value |
|---|---|
| `initial_energy` | 100 |
| `base_metabolism` | 1 |
| `movement_cost` | 1 |
| STAY cost | 1 (`base_metabolism`) |
| MOVE cost | 2 (`base_metabolism` + `movement_cost`) |

### Reproduction / genome

| Parameter | Value |
|---|---|
| `reproduction_energy_threshold` | 150 |
| `reproduction_cost` | 75 |
| `mutation_probability` | 0.05 |
| `mutation_strength` | 0.1 |
| `genome_init_low` | -0.1 |
| `genome_init_high` | 0.1 |
| child energy | same as `reproduction_cost` |
| genome weights | 45 (9 features × 5 actions) |
| C2 policy | linear argmax, no hidden exploration term |

### Observation / memory

| Parameter | Value |
|---|---|
| `observation_radius` | 2 |
| `memory_capacity` | 20 |
| `memory_entry_max_chars` | 200 |
| observation window | 5×5 egocentric |
| global coords / IDs / others' energy | no |

### Simulation

| Parameter | Value |
|---|---|
| `ticks` | 200 |
| `snapshot_every` | 100 |
| `experiment_id` | c6a_qwen38_27b_20x200 |

### LLM

| Parameter | Value |
|---|---|
| `llm_model` | qwen3.8:27b |
| `llm_endpoint` | http://127.0.0.1:11434 |
| `llm_temperature` | 0.0 |
| `llm_prompt_id` | llm_a_evolution_memory |
| `llm_prompt_version` | 1 |
| `llm_num_predict` | 128 |

### Other config

| Parameter | Value |
|---|---|
| `llm_timeout_s` | 120.0 |

### Controller flags

| Controller | Reproduction | Genome | Memory |
|---|---|---|---|
| random | no | no | no |
| reactive | no | no | no |
| llm_evolution_memory | yes | yes | yes |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 4cccfb643e983d92dcaa96fd2a7e662f456d1a9c |

**Warning:** shared parameters differ across runs in this batch:
- `controller_version`: `m1-v1` (n=40), `m3-c6-v1` (n=20)

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 20 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 7.2 | 6.5 | 0.0 |
| reactive | 20 | 20 | 100.0% | 0 | 0.0% | 4.95 | 5.00 | 0.00 | 0.00 | 83.2 | 87.0 | 845.9 |
| llm_evolution_memory | 20 | 20 | 100.0% | 18 | 90.0% | 3.25 | 3.50 | 2.90 | 2.50 | 58.9 | 60.5 | 197.8 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 20 | 100.0% | 107.2 | 101.5 | 107.2 | 101.5 |
| reactive | 0 | 0.0% | — | — | 200.0 | 200.0 |
| llm_evolution_memory | 0 | 0.0% | — | — | 200.0 | 200.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| llm_evolution_memory | 90.0% | 2.15 | 1.20 | 29.4 | 10.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 20}`; births `{0: 20}`
- **reactive** final pop `{3: 3, 4: 4, 5: 8, 6: 2, 7: 2, 8: 1}`; births `{0: 20}`
- **llm_evolution_memory** final pop `{1: 4, 2: 2, 3: 4, 4: 7, 5: 2, 7: 1}`; births `{0: 2, 1: 3, 2: 5, 3: 3, 4: 4, 5: 1, 7: 1, 8: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | reactive − random | 20 | 4.95 | 5.00 | [4.36, 5.54] | 3.65 | 20 / 0 / 0 |
| births | reactive − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| resources_consumed_count | reactive − random | 20 | 75.95 | 82.00 | [68.83, 83.07] | 4.67 | 20 / 0 / 0 |
| total_energy_final | reactive − random | 20 | 845.90 | 848.50 | [696.35, 995.45] | 2.48 | 20 / 0 / 0 |
| time_to_extinction_censored | reactive − random | 20 | 92.85 | 98.50 | [83.79, 101.91] | 4.49 | 20 / 0 / 0 |
| max_generation | reactive − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| survived | reactive − random | 20 | 1.00 | 1.00 | [1.00, 1.00] | 0.00 | 20 / 0 / 0 |
| final_population | llm_evolution_memory − random | 20 | 3.25 | 3.50 | [2.56, 3.94] | 2.05 | 20 / 0 / 0 |
| births | llm_evolution_memory − random | 20 | 2.90 | 2.50 | [1.98, 3.82] | 1.38 | 18 / 2 / 0 |
| resources_consumed_count | llm_evolution_memory − random | 20 | 51.65 | 52.00 | [43.55, 59.75] | 2.79 | 20 / 0 / 0 |
| total_energy_final | llm_evolution_memory − random | 20 | 197.80 | 195.50 | [143.19, 252.41] | 1.59 | 20 / 0 / 0 |
| time_to_extinction_censored | llm_evolution_memory − random | 20 | 92.85 | 98.50 | [83.79, 101.91] | 4.49 | 20 / 0 / 0 |
| max_generation | llm_evolution_memory − random | 20 | 1.20 | 1.00 | [0.90, 1.50] | 1.72 | 18 / 2 / 0 |
| survived | llm_evolution_memory − random | 20 | 1.00 | 1.00 | [1.00, 1.00] | 0.00 | 20 / 0 / 0 |
| final_population | llm_evolution_memory − reactive | 20 | -1.70 | -1.50 | [-2.44, -0.96] | -1.01 | 0 / 5 / 15 |
| births | llm_evolution_memory − reactive | 20 | 2.90 | 2.50 | [1.98, 3.82] | 1.38 | 18 / 2 / 0 |
| resources_consumed_count | llm_evolution_memory − reactive | 20 | -24.30 | -22.50 | [-34.11, -14.49] | -1.09 | 2 / 0 / 18 |
| total_energy_final | llm_evolution_memory − reactive | 20 | -648.10 | -595.00 | [-797.01, -499.19] | -1.91 | 0 / 0 / 20 |
| time_to_extinction_censored | llm_evolution_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| max_generation | llm_evolution_memory − reactive | 20 | 1.20 | 1.00 | [0.90, 1.50] | 1.72 | 18 / 2 / 0 |
| survived | llm_evolution_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

Births ≥ 5:
- seed 16 llm_evolution_memory: births=8 pop=7 alive
- seed 7 llm_evolution_memory: births=7 pop=5 alive
- seed 14 llm_evolution_memory: births=5 pop=2 alive

A visually interesting GIF is not evidence of emergence.
