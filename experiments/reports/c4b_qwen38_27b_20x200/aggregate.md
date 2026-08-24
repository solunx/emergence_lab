# Aggregate results — `c4b_qwen38_27b_20x200`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **20**
- controller-runs: **60**
- ticks: **200**
- controllers: random, reactive, llm_b_memory

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
| `experiment_id` | c4b_qwen38_27b_20x200 |

### LLM

| Parameter | Value |
|---|---|
| `llm_model` | qwen3.8:27b |
| `llm_endpoint` | http://127.0.0.1:11434 |
| `llm_temperature` | 0.0 |
| `llm_prompt_id` | llm_b_memory |
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
| llm_b_memory | no | no | yes |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 0a85cc5df853d51abe2ba5d0accd4aee09211adb |

**Warning:** shared parameters differ across runs in this batch:
- `controller_version`: `m1-v1` (n=40), `m2-c4-v1` (n=20)

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 20 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 7.2 | 6.5 | 0.0 |
| reactive | 20 | 20 | 100.0% | 0 | 0.0% | 4.95 | 5.00 | 0.00 | 0.00 | 83.2 | 87.0 | 845.9 |
| llm_b_memory | 20 | 20 | 100.0% | 0 | 0.0% | 1.80 | 2.00 | 0.00 | 0.00 | 34.5 | 33.0 | 194.7 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 20 | 100.0% | 107.2 | 101.5 | 107.2 | 101.5 |
| reactive | 0 | 0.0% | — | — | 200.0 | 200.0 |
| llm_b_memory | 0 | 0.0% | — | — | 200.0 | 200.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| llm_b_memory | 0.0% | 0.00 | 0.00 | — | — |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 20}`; births `{0: 20}`
- **reactive** final pop `{3: 3, 4: 4, 5: 8, 6: 2, 7: 2, 8: 1}`; births `{0: 20}`
- **llm_b_memory** final pop `{1: 9, 2: 7, 3: 3, 4: 1}`; births `{0: 20}`

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
| final_population | llm_b_memory − random | 20 | 1.80 | 2.00 | [1.41, 2.19] | 2.01 | 20 / 0 / 0 |
| births | llm_b_memory − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| resources_consumed_count | llm_b_memory − random | 20 | 27.35 | 25.50 | [22.48, 32.22] | 2.46 | 20 / 0 / 0 |
| total_energy_final | llm_b_memory − random | 20 | 194.65 | 157.50 | [130.50, 258.80] | 1.33 | 20 / 0 / 0 |
| time_to_extinction_censored | llm_b_memory − random | 20 | 92.85 | 98.50 | [83.79, 101.91] | 4.49 | 20 / 0 / 0 |
| max_generation | llm_b_memory − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| survived | llm_b_memory − random | 20 | 1.00 | 1.00 | [1.00, 1.00] | 0.00 | 20 / 0 / 0 |
| final_population | llm_b_memory − reactive | 20 | -3.15 | -3.00 | [-3.76, -2.54] | -2.27 | 0 / 0 / 20 |
| births | llm_b_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| resources_consumed_count | llm_b_memory − reactive | 20 | -48.60 | -45.50 | [-55.76, -41.44] | -2.97 | 0 / 0 / 20 |
| total_energy_final | llm_b_memory − reactive | 20 | -651.25 | -599.50 | [-798.75, -503.75] | -1.94 | 0 / 0 / 20 |
| time_to_extinction_censored | llm_b_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| max_generation | llm_b_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| survived | llm_b_memory − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

A visually interesting GIF is not evidence of emergence.
