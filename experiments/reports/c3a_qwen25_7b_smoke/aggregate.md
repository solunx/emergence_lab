# Aggregate results — `c3a_qwen25_7b_smoke`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **1**
- controller-runs: **3**
- ticks: **50**
- controllers: random, reactive, llm

## Parameters

From **3** `metadata.json` file(s). Shared world fields should be identical across clones; seed and controller differ by design.

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
| `ticks` | 50 |
| `snapshot_every` | 100 |
| `experiment_id` | c3a_qwen25_7b_smoke |

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
| llm | no | no |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 823cc1aa23329d56ac86709cad5ec9167013d16b |

**Warning:** shared parameters differ across runs in this batch:
- `controller_version`: `m1-v1` (n=2), `m2-c3-v1` (n=1)

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 1 | 1 | 100.0% | 0 | 0.0% | 10.00 | 10.00 | 0.00 | 0.00 | 4.0 | 4.0 | 218.0 |
| reactive | 1 | 1 | 100.0% | 0 | 0.0% | 10.00 | 10.00 | 0.00 | 0.00 | 25.0 | 25.0 | 837.0 |
| llm | 1 | 1 | 100.0% | 0 | 0.0% | 10.00 | 10.00 | 0.00 | 0.00 | 1.0 | 1.0 | 496.0 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 0 | 0.0% | — | — | 50.0 | 50.0 |
| reactive | 0 | 0.0% | — | — | 50.0 | 50.0 |
| llm | 0 | 0.0% | — | — | 50.0 | 50.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| llm | 0.0% | 0.00 | 0.00 | — | — |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{10: 1}`; births `{0: 1}`
- **reactive** final pop `{10: 1}`; births `{0: 1}`
- **llm** final pop `{10: 1}`; births `{0: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | reactive − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| births | reactive − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| resources_consumed_count | reactive − random | 1 | 21.00 | 21.00 | [21.00, 21.00] | 0.00 | 1 / 0 / 0 |
| total_energy_final | reactive − random | 1 | 619.00 | 619.00 | [619.00, 619.00] | 0.00 | 1 / 0 / 0 |
| time_to_extinction_censored | reactive − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| max_generation | reactive − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| survived | reactive − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| final_population | llm − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| births | llm − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| resources_consumed_count | llm − random | 1 | -3.00 | -3.00 | [-3.00, -3.00] | 0.00 | 0 / 0 / 1 |
| total_energy_final | llm − random | 1 | 278.00 | 278.00 | [278.00, 278.00] | 0.00 | 1 / 0 / 0 |
| time_to_extinction_censored | llm − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| max_generation | llm − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| survived | llm − random | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| final_population | llm − reactive | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| births | llm − reactive | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| resources_consumed_count | llm − reactive | 1 | -24.00 | -24.00 | [-24.00, -24.00] | 0.00 | 0 / 0 / 1 |
| total_energy_final | llm − reactive | 1 | -341.00 | -341.00 | [-341.00, -341.00] | 0.00 | 0 / 0 / 1 |
| time_to_extinction_censored | llm − reactive | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| max_generation | llm − reactive | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |
| survived | llm − reactive | 1 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 1 / 0 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

A visually interesting GIF is not evidence of emergence.
