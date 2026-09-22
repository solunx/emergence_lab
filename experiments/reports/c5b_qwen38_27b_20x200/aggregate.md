# Aggregate results — `c5b_qwen38_27b_20x200`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **20**
- controller-runs: **60**
- ticks: **200**
- controllers: random, reactive, llm_b_evolution

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
| `experiment_id` | c5b_qwen38_27b_20x200 |

### LLM

| Parameter | Value |
|---|---|
| `llm_model` | qwen3.8:27b |
| `llm_endpoint` | http://127.0.0.1:11434 |
| `llm_temperature` | 0.0 |
| `llm_prompt_id` | llm_b_evolution |
| `llm_prompt_version` | 1 |
| `llm_num_predict` | 64 |

### Other config

| Parameter | Value |
|---|---|
| `llm_timeout_s` | 120.0 |

### Controller flags

| Controller | Reproduction | Genome | Memory |
|---|---|---|---|
| random | no | no | no |
| reactive | no | no | no |
| llm_b_evolution | yes | yes | no |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 09b0f80107272c6dce2132a98746ee7777729309 |

**Warning:** shared parameters differ across runs in this batch:
- `controller_version`: `m1-v1` (n=40), `m3-c5-v1` (n=20)

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 20 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 7.2 | 6.5 | 0.0 |
| reactive | 20 | 20 | 100.0% | 0 | 0.0% | 4.95 | 5.00 | 0.00 | 0.00 | 83.2 | 87.0 | 845.9 |
| llm_b_evolution | 20 | 12 | 60.0% | 14 | 70.0% | 1.95 | 1.00 | 2.80 | 1.00 | 22.6 | 19.5 | 96.5 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 20 | 100.0% | 107.2 | 101.5 | 107.2 | 101.5 |
| reactive | 0 | 0.0% | — | — | 200.0 | 200.0 |
| llm_b_evolution | 8 | 40.0% | 146.5 | 147.0 | 178.6 | 200.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| llm_b_evolution | 70.0% | 1.05 | 1.40 | 22.1 | 19.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 20}`; births `{0: 20}`
- **reactive** final pop `{3: 3, 4: 4, 5: 8, 6: 2, 7: 2, 8: 1}`; births `{0: 20}`
- **llm_b_evolution** final pop `{0: 8, 1: 4, 2: 2, 3: 3, 5: 1, 6: 1, 11: 1}`; births `{0: 6, 1: 5, 3: 2, 4: 2, 5: 2, 7: 1, 9: 1, 11: 1}`

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
| final_population | llm_b_evolution − random | 20 | 1.95 | 1.00 | [0.74, 3.16] | 0.71 | 12 / 8 / 0 |
| births | llm_b_evolution − random | 20 | 2.80 | 1.00 | [1.38, 4.22] | 0.86 | 14 / 6 / 0 |
| resources_consumed_count | llm_b_evolution − random | 20 | 15.40 | 12.00 | [6.30, 24.50] | 0.74 | 16 / 0 / 4 |
| total_energy_final | llm_b_evolution − random | 20 | 96.50 | 3.00 | [28.18, 164.82] | 0.62 | 12 / 8 / 0 |
| time_to_extinction_censored | llm_b_evolution − random | 20 | 71.45 | 76.50 | [58.13, 84.77] | 2.35 | 20 / 0 / 0 |
| max_generation | llm_b_evolution − random | 20 | 1.40 | 1.00 | [0.79, 2.01] | 1.01 | 14 / 6 / 0 |
| survived | llm_b_evolution − random | 20 | 0.60 | 1.00 | [0.38, 0.82] | 1.19 | 12 / 8 / 0 |
| final_population | llm_b_evolution − reactive | 20 | -3.00 | -3.00 | [-4.39, -1.61] | -0.95 | 2 / 1 / 17 |
| births | llm_b_evolution − reactive | 20 | 2.80 | 1.00 | [1.38, 4.22] | 0.86 | 14 / 6 / 0 |
| resources_consumed_count | llm_b_evolution − reactive | 20 | -60.55 | -63.00 | [-71.12, -49.98] | -2.51 | 0 / 0 / 20 |
| total_energy_final | llm_b_evolution − reactive | 20 | -749.40 | -801.00 | [-888.26, -610.54] | -2.37 | 0 / 0 / 20 |
| time_to_extinction_censored | llm_b_evolution − reactive | 20 | -21.40 | 0.00 | [-34.27, -8.53] | -0.73 | 0 / 12 / 8 |
| max_generation | llm_b_evolution − reactive | 20 | 1.40 | 1.00 | [0.79, 2.01] | 1.01 | 14 / 6 / 0 |
| survived | llm_b_evolution − reactive | 20 | -0.40 | 0.00 | [-0.62, -0.18] | -0.80 | 0 / 12 / 8 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

Births ≥ 5:
- seed 5 llm_b_evolution: births=11 pop=11 alive
- seed 10 llm_b_evolution: births=9 pop=6 alive
- seed 9 llm_b_evolution: births=7 pop=5 alive
- seed 2 llm_b_evolution: births=5 pop=3 alive
- seed 7 llm_b_evolution: births=5 pop=2 alive

Extinct in a controller that usually survives:
- seed 3 llm_b_evolution: tte=129 food=3
- seed 6 llm_b_evolution: tte=146 food=4
- seed 11 llm_b_evolution: tte=185 food=9
- seed 13 llm_b_evolution: tte=129 food=4
- seed 14 llm_b_evolution: tte=154 food=10
- seed 15 llm_b_evolution: tte=148 food=2
- seed 16 llm_b_evolution: tte=155 food=6
- seed 19 llm_b_evolution: tte=126 food=4

A visually interesting GIF is not evidence of emergence.
