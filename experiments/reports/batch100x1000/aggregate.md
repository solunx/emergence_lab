# Aggregate results — `batch100x1000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **300**
- ticks: **1000**
- controllers: random, reactive, evolutionary

## Parameters

From **300** `metadata.json` file(s). Shared world fields should be identical across clones; seed and controller differ by design.

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
| `ticks` | 1000 |
| `snapshot_every` | 100 |
| `experiment_id` | batch100x1000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| random | no | no |
| reactive | no | no |
| evolutionary | yes | yes |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | — |

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 100 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 6.7 | 6.0 | 0.0 |
| reactive | 100 | 97 | 97.0% | 0 | 0.0% | 2.72 | 3.00 | 0.00 | 0.00 | 276.0 | 282.5 | 1587.5 |
| evolutionary | 100 | 6 | 6.0% | 32 | 32.0% | 0.16 | 0.00 | 0.99 | 0.00 | 25.3 | 10.0 | 9.9 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 100 | 100.0% | 108.0 | 105.0 | 108.0 | 105.0 |
| reactive | 3 | 3.0% | 489.3 | 568.0 | 984.7 | 1000.0 |
| evolutionary | 94 | 94.0% | 251.1 | 129.5 | 296.0 | 134.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | — | — | — | — |
| reactive | 0.0% | — | — | — | — |
| evolutionary | 32.0% | — | — | — | — |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 100}`; births `{0: 100}`
- **reactive** final pop `{0: 3, 1: 13, 2: 28, 3: 29, 4: 20, 5: 6, 6: 1}`; births `{0: 100}`
- **evolutionary** final pop `{0: 94, 1: 2, 2: 2, 3: 1, 7: 1}`; births `{0: 68, 1: 22, 2: 2, 3: 1, 4: 1, 5: 1, 9: 2, 10: 2, 23: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | reactive − random | 100 | 2.72 | 3.00 | [2.48, 2.96] | 2.19 | 97 / 3 / 0 |
| births | reactive − random | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| resources_consumed_count | reactive − random | 100 | 269.25 | 275.00 | [252.57, 285.93] | 3.16 | 100 / 0 / 0 |
| total_energy_final | reactive − random | 100 | 1587.49 | 1550.50 | [1404.27, 1770.71] | 1.70 | 97 / 3 / 0 |
| time_to_extinction_censored | reactive − random | 100 | 876.70 | 895.00 | [856.51, 896.89] | 8.51 | 100 / 0 / 0 |
| survived | reactive − random | 100 | 0.97 | 1.00 | [0.94, 1.00] | 5.66 | 97 / 3 / 0 |
| final_population | evolutionary − random | 100 | 0.16 | 0.00 | [0.00, 0.32] | 0.20 | 6 / 94 / 0 |
| births | evolutionary − random | 100 | 0.99 | 0.00 | [0.41, 1.57] | 0.33 | 32 / 68 / 0 |
| resources_consumed_count | evolutionary − random | 100 | 18.58 | 3.00 | [10.16, 27.00] | 0.43 | 61 / 5 / 34 |
| total_energy_final | evolutionary − random | 100 | 9.95 | 0.00 | [0.14, 19.76] | 0.20 | 6 / 94 / 0 |
| time_to_extinction_censored | evolutionary − random | 100 | 188.01 | 27.00 | [131.14, 244.88] | 0.65 | 83 / 0 / 17 |
| survived | evolutionary − random | 100 | 0.06 | 0.00 | [0.01, 0.11] | 0.25 | 6 / 94 / 0 |
| final_population | evolutionary − reactive | 100 | -2.56 | -3.00 | [-2.83, -2.29] | -1.86 | 2 / 3 / 95 |
| births | evolutionary − reactive | 100 | 0.99 | 0.00 | [0.41, 1.57] | 0.33 | 32 / 68 / 0 |
| resources_consumed_count | evolutionary − reactive | 100 | -250.67 | -263.50 | [-267.75, -233.59] | -2.88 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive | 100 | -1577.54 | -1550.50 | [-1760.97, -1394.11] | -1.69 | 0 / 3 / 97 |
| time_to_extinction_censored | evolutionary − reactive | 100 | -688.69 | -859.50 | [-746.99, -630.39] | -2.32 | 0 / 6 / 94 |
| survived | evolutionary − reactive | 100 | -0.91 | -1.00 | [-0.97, -0.85] | -3.16 | 0 / 9 / 91 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

Non-reactive survivors (n=6):
- seed 3 evolutionary: pop=7 births=23 food=337 energy=406
- seed 88 evolutionary: pop=3 births=10 food=104 energy=157
- seed 92 evolutionary: pop=2 births=9 food=151 energy=220
- seed 99 evolutionary: pop=2 births=9 food=138 energy=118
- seed 16 evolutionary: pop=1 births=10 food=93 energy=75
- seed 40 evolutionary: pop=1 births=3 food=94 energy=19

Births ≥ 5:
- seed 3 evolutionary: births=23 pop=7 alive
- seed 16 evolutionary: births=10 pop=1 alive
- seed 88 evolutionary: births=10 pop=3 alive
- seed 92 evolutionary: births=9 pop=2 alive
- seed 99 evolutionary: births=9 pop=2 alive
- seed 85 evolutionary: births=5 pop=0 extinct@998

Extinct in a controller that usually survives:
- seed 46 reactive: tte=699 food=163
- seed 59 reactive: tte=201 food=22
- seed 86 reactive: tte=568 food=125

A visually interesting GIF is not evidence of emergence.
