# Aggregate results — `diag_c2_oracle_100x1000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **300**
- ticks: **1000**
- controllers: reactive, evolutionary, evolutionary_oracle

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
| `experiment_id` | diag_c2_oracle_100x1000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| reactive | no | no |
| evolutionary | yes | yes |
| evolutionary_oracle | no | no |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 823cc1aa23329d56ac86709cad5ec9167013d16b |

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reactive | 100 | 97 | 97.0% | 0 | 0.0% | 2.72 | 3.00 | 0.00 | 0.00 | 276.0 | 282.5 | 1587.5 |
| evolutionary | 100 | 6 | 6.0% | 32 | 32.0% | 0.16 | 0.00 | 0.99 | 0.00 | 25.3 | 10.0 | 9.9 |
| evolutionary_oracle | 100 | 32 | 32.0% | 0 | 0.0% | 0.34 | 0.00 | 0.00 | 0.00 | 88.6 | 82.0 | 122.0 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| reactive | 3 | 3.0% | 489.3 | 568.0 | 984.7 | 1000.0 |
| evolutionary | 94 | 94.0% | 251.1 | 129.5 | 296.0 | 134.0 |
| evolutionary_oracle | 68 | 68.0% | 528.3 | 513.0 | 679.3 | 676.5 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| evolutionary | 32.0% | 0.34 | 0.48 | 47.0 | 25.0 |
| evolutionary_oracle | 0.0% | 0.00 | 0.00 | — | — |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **reactive** final pop `{0: 3, 1: 13, 2: 28, 3: 29, 4: 20, 5: 6, 6: 1}`; births `{0: 100}`
- **evolutionary** final pop `{0: 94, 1: 2, 2: 2, 3: 1, 7: 1}`; births `{0: 68, 1: 22, 2: 2, 3: 1, 4: 1, 5: 1, 9: 2, 10: 2, 23: 1}`
- **evolutionary_oracle** final pop `{0: 68, 1: 30, 2: 2}`; births `{0: 100}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | evolutionary − reactive | 100 | -2.56 | -3.00 | [-2.83, -2.29] | -1.86 | 2 / 3 / 95 |
| births | evolutionary − reactive | 100 | 0.99 | 0.00 | [0.41, 1.57] | 0.33 | 32 / 68 / 0 |
| resources_consumed_count | evolutionary − reactive | 100 | -250.67 | -263.50 | [-267.75, -233.59] | -2.88 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive | 100 | -1577.54 | -1550.50 | [-1760.97, -1394.11] | -1.69 | 0 / 3 / 97 |
| time_to_extinction_censored | evolutionary − reactive | 100 | -688.69 | -859.50 | [-746.99, -630.39] | -2.32 | 0 / 6 / 94 |
| max_generation | evolutionary − reactive | 100 | 0.48 | 0.00 | [0.30, 0.66] | 0.52 | 32 / 68 / 0 |
| survived | evolutionary − reactive | 100 | -0.91 | -1.00 | [-0.97, -0.85] | -3.16 | 0 / 9 / 91 |
| final_population | evolutionary_oracle − reactive | 100 | -2.38 | -2.00 | [-2.64, -2.12] | -1.81 | 1 / 6 / 93 |
| births | evolutionary_oracle − reactive | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| resources_consumed_count | evolutionary_oracle − reactive | 100 | -187.38 | -198.50 | [-204.64, -170.12] | -2.13 | 2 / 0 / 98 |
| total_energy_final | evolutionary_oracle − reactive | 100 | -1465.50 | -1289.50 | [-1644.34, -1286.66] | -1.61 | 2 / 2 / 96 |
| time_to_extinction_censored | evolutionary_oracle − reactive | 100 | -305.41 | -308.00 | [-362.72, -248.10] | -1.04 | 2 / 31 / 67 |
| max_generation | evolutionary_oracle − reactive | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| survived | evolutionary_oracle − reactive | 100 | -0.65 | -1.00 | [-0.75, -0.55] | -1.30 | 1 / 33 / 66 |
| final_population | evolutionary_oracle − evolutionary | 100 | 0.18 | 0.00 | [-0.02, 0.38] | 0.18 | 32 / 62 / 6 |
| births | evolutionary_oracle − evolutionary | 100 | -0.99 | 0.00 | [-1.57, -0.41] | -0.33 | 0 / 68 / 32 |
| resources_consumed_count | evolutionary_oracle − evolutionary | 100 | 63.29 | 60.50 | [51.92, 74.66] | 1.09 | 94 / 0 / 6 |
| total_energy_final | evolutionary_oracle − evolutionary | 100 | 112.04 | 0.00 | [64.16, 159.92] | 0.46 | 32 / 62 / 6 |
| time_to_extinction_censored | evolutionary_oracle − evolutionary | 100 | 383.28 | 370.50 | [300.95, 465.61] | 0.91 | 83 / 0 / 17 |
| max_generation | evolutionary_oracle − evolutionary | 100 | -0.48 | 0.00 | [-0.66, -0.30] | -0.52 | 0 / 68 / 32 |
| survived | evolutionary_oracle − evolutionary | 100 | 0.26 | 0.00 | [0.15, 0.37] | 0.46 | 32 / 62 / 6 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

Non-reactive survivors (n=38):
- seed 3 evolutionary: pop=7 births=23 food=337 energy=406
- seed 88 evolutionary: pop=3 births=10 food=104 energy=157
- seed 8 evolutionary_oracle: pop=2 births=0 food=225 energy=1150
- seed 54 evolutionary_oracle: pop=2 births=0 food=175 energy=447
- seed 92 evolutionary: pop=2 births=9 food=151 energy=220
- seed 99 evolutionary: pop=2 births=9 food=138 energy=118
- seed 4 evolutionary_oracle: pop=1 births=0 food=101 energy=225
- seed 6 evolutionary_oracle: pop=1 births=0 food=118 energy=303
- seed 7 evolutionary_oracle: pop=1 births=0 food=106 energy=99
- seed 12 evolutionary_oracle: pop=1 births=0 food=144 energy=407
- seed 14 evolutionary_oracle: pop=1 births=0 food=150 energy=416
- seed 16 evolutionary: pop=1 births=10 food=93 energy=75
- seed 27 evolutionary_oracle: pop=1 births=0 food=81 energy=189
- seed 28 evolutionary_oracle: pop=1 births=0 food=145 energy=1046
- seed 33 evolutionary_oracle: pop=1 births=0 food=126 energy=579
- seed 38 evolutionary_oracle: pop=1 births=0 food=101 energy=208
- seed 40 evolutionary: pop=1 births=3 food=94 energy=19
- seed 43 evolutionary_oracle: pop=1 births=0 food=120 energy=638
- seed 49 evolutionary_oracle: pop=1 births=0 food=117 energy=21
- seed 55 evolutionary_oracle: pop=1 births=0 food=155 energy=405
- seed 58 evolutionary_oracle: pop=1 births=0 food=150 energy=269
- seed 60 evolutionary_oracle: pop=1 births=0 food=136 energy=642
- seed 61 evolutionary_oracle: pop=1 births=0 food=151 energy=436
- seed 65 evolutionary_oracle: pop=1 births=0 food=110 energy=680
- seed 66 evolutionary_oracle: pop=1 births=0 food=106 energy=306
- seed 73 evolutionary_oracle: pop=1 births=0 food=151 energy=144
- seed 74 evolutionary_oracle: pop=1 births=0 food=152 energy=648
- seed 77 evolutionary_oracle: pop=1 births=0 food=98 energy=42
- seed 78 evolutionary_oracle: pop=1 births=0 food=87 energy=158
- seed 79 evolutionary_oracle: pop=1 births=0 food=151 energy=170
- seed 82 evolutionary_oracle: pop=1 births=0 food=129 energy=358
- seed 84 evolutionary_oracle: pop=1 births=0 food=131 energy=255
- seed 86 evolutionary_oracle: pop=1 births=0 food=210 energy=450
- seed 87 evolutionary_oracle: pop=1 births=0 food=101 energy=685
- seed 89 evolutionary_oracle: pop=1 births=0 food=117 energy=149
- seed 91 evolutionary_oracle: pop=1 births=0 food=95 energy=88
- seed 94 evolutionary_oracle: pop=1 births=0 food=97 energy=197
- seed 100 evolutionary_oracle: pop=1 births=0 food=155 energy=389

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
