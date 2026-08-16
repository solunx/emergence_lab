# Aggregate results — `c3b_qwen25_7b_20x200`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **20**
- controller-runs: **60**
- ticks: **200**
- controllers: random, reactive, llm_b

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
| `experiment_id` | c3b_qwen25_7b_20x200 |

### LLM

| Parameter | Value |
|---|---|
| `llm_model` | qwen2.5:7b |
| `llm_endpoint` | http://127.0.0.1:11434 |
| `llm_temperature` | 0.0 |
| `llm_prompt_id` | llm_a |
| `llm_prompt_version` | 1 |
| `llm_num_predict` | 64 |

### Other config

| Parameter | Value |
|---|---|
| `llm_timeout_s` | 120.0 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| random | no | no |
| reactive | no | no |
| llm_b | no | no |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 99ab5570084855aaba3ff73806c254d309dc286e |

**Warning:** shared parameters differ across runs in this batch:
- `llm_prompt_id`: `llm_a` (n=40), `llm_b` (n=20)
- `controller_version`: `m1-v1` (n=40), `m2-c3-v1` (n=20)

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 20 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 7.2 | 6.5 | 0.0 |
| reactive | 20 | 20 | 100.0% | 0 | 0.0% | 4.95 | 5.00 | 0.00 | 0.00 | 83.2 | 87.0 | 845.9 |
| llm_b | 20 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 1.3 | 1.0 | 0.0 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 20 | 100.0% | 107.2 | 101.5 | 107.2 | 101.5 |
| reactive | 0 | 0.0% | — | — | 200.0 | 200.0 |
| llm_b | 20 | 100.0% | 121.3 | 127.0 | 121.3 | 127.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| llm_b | 0.0% | 0.00 | 0.00 | — | — |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 20}`; births `{0: 20}`
- **reactive** final pop `{3: 3, 4: 4, 5: 8, 6: 2, 7: 2, 8: 1}`; births `{0: 20}`
- **llm_b** final pop `{0: 20}`; births `{0: 20}`

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
| final_population | llm_b − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| births | llm_b − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| resources_consumed_count | llm_b − random | 20 | -5.90 | -6.00 | [-7.23, -4.57] | -1.95 | 0 / 0 / 20 |
| total_energy_final | llm_b − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| time_to_extinction_censored | llm_b − random | 20 | 14.15 | 6.50 | [1.33, 26.97] | 0.48 | 14 / 0 / 6 |
| max_generation | llm_b − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| survived | llm_b − random | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| final_population | llm_b − reactive | 20 | -4.95 | -5.00 | [-5.54, -4.36] | -3.65 | 0 / 0 / 20 |
| births | llm_b − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| resources_consumed_count | llm_b − reactive | 20 | -81.85 | -85.50 | [-89.06, -74.64] | -4.98 | 0 / 0 / 20 |
| total_energy_final | llm_b − reactive | 20 | -845.90 | -848.50 | [-995.45, -696.35] | -2.48 | 0 / 0 / 20 |
| time_to_extinction_censored | llm_b − reactive | 20 | -78.70 | -73.00 | [-85.50, -71.90] | -5.07 | 0 / 0 / 20 |
| max_generation | llm_b − reactive | 20 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 20 / 0 |
| survived | llm_b − reactive | 20 | -1.00 | -1.00 | [-1.00, -1.00] | 0.00 | 0 / 0 / 20 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

A visually interesting GIF is not evidence of emergence.
