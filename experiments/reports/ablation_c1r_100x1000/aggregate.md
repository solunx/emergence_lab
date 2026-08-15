# Aggregate results — `ablation_c1r_100x1000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **300**
- ticks: **1000**
- controllers: reactive, reactive_r, evolutionary

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
| `experiment_id` | ablation_c1r_100x1000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| reactive | no | no |
| reactive_r | yes | no |
| evolutionary | yes | yes |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 77753cea747983af8747e4ddb20e7d24926333ba |

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reactive | 100 | 97 | 97.0% | 0 | 0.0% | 2.72 | 3.00 | 0.00 | 0.00 | 276.0 | 282.5 | 1587.5 |
| reactive_r | 100 | 95 | 95.0% | 99 | 99.0% | 8.48 | 9.00 | 38.36 | 37.50 | 526.6 | 531.5 | 602.2 |
| evolutionary | 100 | 6 | 6.0% | 32 | 32.0% | 0.16 | 0.00 | 0.99 | 0.00 | 25.3 | 10.0 | 9.9 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| reactive | 3 | 3.0% | 489.3 | 568.0 | 984.7 | 1000.0 |
| reactive_r | 5 | 5.0% | 536.6 | 506.0 | 976.8 | 1000.0 |
| evolutionary | 94 | 94.0% | 251.1 | 129.5 | 296.0 | 134.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| reactive | 0.0% | 0.00 | 0.00 | — | — |
| reactive_r | 99.0% | 3.98 | 7.17 | 14.6 | 4.0 |
| evolutionary | 32.0% | 0.34 | 0.48 | 47.0 | 25.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **reactive** final pop `{0: 3, 1: 13, 2: 28, 3: 29, 4: 20, 5: 6, 6: 1}`; births `{0: 100}`
- **reactive_r** final pop `{0: 5, 2: 2, 3: 3, 4: 5, 5: 4, 6: 8, 7: 8, 8: 11, 9: 11, 10: 12, 11: 11, 12: 6, 13: 9, 14: 2, 15: 2, 16: 1}`; births `{0: 1, 1: 1, 4: 1, 7: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 20: 2, 22: 2, 23: 1, 24: 2, 25: 1, 26: 2, 27: 1, 28: 4, 29: 1, 30: 3, 31: 4, 32: 3, 33: 5, 35: 4, 36: 1, 37: 5, 38: 3, 39: 2, 40: 2, 41: 4, 42: 2, 43: 1, 44: 1, 45: 3, 46: 1, 47: 4, 48: 1, 50: 1, 51: 1, 52: 3, 53: 5, 55: 3, 57: 1, 58: 2, 59: 3, 60: 2, 62: 2, 66: 1, 67: 1, 70: 1}`
- **evolutionary** final pop `{0: 94, 1: 2, 2: 2, 3: 1, 7: 1}`; births `{0: 68, 1: 22, 2: 2, 3: 1, 4: 1, 5: 1, 9: 2, 10: 2, 23: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | reactive_r − reactive | 100 | 5.76 | 6.00 | [5.07, 6.45] | 1.63 | 92 / 2 / 6 |
| births | reactive_r − reactive | 100 | 38.36 | 37.50 | [35.45, 41.27] | 2.59 | 99 / 1 / 0 |
| resources_consumed_count | reactive_r − reactive | 100 | 250.61 | 261.50 | [224.71, 276.51] | 1.90 | 94 / 1 / 5 |
| total_energy_final | reactive_r − reactive | 100 | -985.27 | -876.50 | [-1152.91, -817.63] | -1.15 | 6 / 1 / 93 |
| time_to_extinction_censored | reactive_r − reactive | 100 | -7.85 | 0.00 | [-28.12, 12.42] | -0.08 | 2 / 94 / 4 |
| max_generation | reactive_r − reactive | 100 | 7.17 | 7.00 | [6.68, 7.66] | 2.88 | 99 / 1 / 0 |
| survived | reactive_r − reactive | 100 | -0.02 | 0.00 | [-0.07, 0.03] | -0.08 | 2 / 94 / 4 |
| final_population | evolutionary − reactive | 100 | -2.56 | -3.00 | [-2.83, -2.29] | -1.86 | 2 / 3 / 95 |
| births | evolutionary − reactive | 100 | 0.99 | 0.00 | [0.41, 1.57] | 0.33 | 32 / 68 / 0 |
| resources_consumed_count | evolutionary − reactive | 100 | -250.67 | -263.50 | [-267.75, -233.59] | -2.88 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive | 100 | -1577.54 | -1550.50 | [-1760.97, -1394.11] | -1.69 | 0 / 3 / 97 |
| time_to_extinction_censored | evolutionary − reactive | 100 | -688.69 | -859.50 | [-746.99, -630.39] | -2.32 | 0 / 6 / 94 |
| max_generation | evolutionary − reactive | 100 | 0.48 | 0.00 | [0.30, 0.66] | 0.52 | 32 / 68 / 0 |
| survived | evolutionary − reactive | 100 | -0.91 | -1.00 | [-0.97, -0.85] | -3.16 | 0 / 9 / 91 |
| final_population | evolutionary − reactive_r | 100 | -8.32 | -9.00 | [-9.06, -7.58] | -2.21 | 1 / 5 / 94 |
| births | evolutionary − reactive_r | 100 | -37.37 | -36.50 | [-40.38, -34.36] | -2.44 | 1 / 2 / 97 |
| resources_consumed_count | evolutionary − reactive_r | 100 | -501.28 | -504.50 | [-532.31, -470.25] | -3.17 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive_r | 100 | -592.27 | -626.50 | [-644.28, -540.26] | -2.23 | 1 / 5 / 94 |
| time_to_extinction_censored | evolutionary − reactive_r | 100 | -680.84 | -857.00 | [-740.80, -620.88] | -2.23 | 1 / 6 / 93 |
| time_to_first_birth | evolutionary − reactive_r | 32 | 39.75 | 18.00 | [17.81, 61.69] | 0.63 | 23 / 7 / 2 |
| max_generation | evolutionary − reactive_r | 100 | -6.69 | -7.00 | [-7.21, -6.17] | -2.53 | 0 / 3 / 97 |
| survived | evolutionary − reactive_r | 100 | -0.89 | -1.00 | [-0.95, -0.83] | -2.83 | 0 / 11 / 89 |

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
- seed 55 reactive_r: births=70 pop=10 alive
- seed 43 reactive_r: births=67 pop=13 alive
- seed 23 reactive_r: births=66 pop=9 alive
- seed 14 reactive_r: births=62 pop=16 alive
- seed 27 reactive_r: births=62 pop=11 alive
- seed 87 reactive_r: births=60 pop=13 alive
- seed 98 reactive_r: births=60 pop=11 alive
- seed 48 reactive_r: births=59 pop=10 alive
- seed 84 reactive_r: births=59 pop=13 alive
- seed 100 reactive_r: births=59 pop=15 alive
- seed 80 reactive_r: births=58 pop=14 alive
- seed 83 reactive_r: births=58 pop=13 alive
- seed 38 reactive_r: births=57 pop=8 alive
- seed 51 reactive_r: births=55 pop=10 alive
- seed 61 reactive_r: births=55 pop=10 alive
- seed 74 reactive_r: births=55 pop=13 alive
- seed 8 reactive_r: births=53 pop=11 alive
- seed 12 reactive_r: births=53 pop=10 alive
- seed 53 reactive_r: births=53 pop=11 alive
- seed 86 reactive_r: births=53 pop=13 alive
- seed 96 reactive_r: births=53 pop=13 alive
- seed 24 reactive_r: births=52 pop=10 alive
- seed 65 reactive_r: births=52 pop=11 alive
- seed 82 reactive_r: births=52 pop=12 alive
- seed 73 reactive_r: births=51 pop=12 alive
- seed 33 reactive_r: births=50 pop=11 alive
- seed 58 reactive_r: births=48 pop=15 alive
- seed 31 reactive_r: births=47 pop=11 alive
- seed 32 reactive_r: births=47 pop=13 alive
- seed 36 reactive_r: births=47 pop=13 alive
- seed 42 reactive_r: births=47 pop=12 alive
- seed 79 reactive_r: births=46 pop=10 alive
- seed 9 reactive_r: births=45 pop=11 alive
- seed 16 reactive_r: births=45 pop=9 alive
- seed 97 reactive_r: births=45 pop=10 alive
- seed 60 reactive_r: births=44 pop=14 alive
- seed 17 reactive_r: births=43 pop=12 alive
- seed 26 reactive_r: births=42 pop=9 alive
- seed 28 reactive_r: births=42 pop=6 alive
- seed 67 reactive_r: births=41 pop=6 alive
- seed 77 reactive_r: births=41 pop=9 alive
- seed 92 reactive_r: births=41 pop=7 alive
- seed 99 reactive_r: births=41 pop=11 alive
- seed 47 reactive_r: births=40 pop=12 alive
- seed 49 reactive_r: births=40 pop=7 alive
- seed 7 reactive_r: births=39 pop=7 alive
- seed 70 reactive_r: births=39 pop=7 alive
- seed 5 reactive_r: births=38 pop=10 alive
- seed 30 reactive_r: births=38 pop=8 alive
- seed 66 reactive_r: births=38 pop=4 alive
- seed 21 reactive_r: births=37 pop=8 alive
- seed 40 reactive_r: births=37 pop=12 alive
- seed 46 reactive_r: births=37 pop=9 alive
- seed 64 reactive_r: births=37 pop=6 alive
- seed 94 reactive_r: births=37 pop=9 alive
- seed 44 reactive_r: births=36 pop=9 alive
- seed 41 reactive_r: births=35 pop=6 alive
- seed 63 reactive_r: births=35 pop=11 alive
- seed 68 reactive_r: births=35 pop=6 alive
- seed 75 reactive_r: births=35 pop=11 alive
- seed 35 reactive_r: births=33 pop=9 alive
- seed 52 reactive_r: births=33 pop=10 alive
- seed 54 reactive_r: births=33 pop=5 alive
- seed 76 reactive_r: births=33 pop=5 alive
- seed 91 reactive_r: births=33 pop=8 alive
- seed 6 reactive_r: births=32 pop=9 alive
- seed 69 reactive_r: births=32 pop=8 alive
- seed 78 reactive_r: births=32 pop=8 alive
- seed 45 reactive_r: births=31 pop=7 alive
- seed 56 reactive_r: births=31 pop=8 alive
- seed 62 reactive_r: births=31 pop=6 alive
- seed 81 reactive_r: births=31 pop=8 alive
- seed 1 reactive_r: births=30 pop=9 alive
- seed 10 reactive_r: births=30 pop=0 extinct@766
- seed 88 reactive_r: births=30 pop=10 alive
- seed 20 reactive_r: births=29 pop=8 alive
- seed 19 reactive_r: births=28 pop=10 alive
- seed 50 reactive_r: births=28 pop=4 alive
- seed 85 reactive_r: births=28 pop=8 alive
- seed 89 reactive_r: births=28 pop=9 alive
- seed 2 reactive_r: births=27 pop=7 alive
- seed 29 reactive_r: births=26 pop=8 alive
- seed 95 reactive_r: births=26 pop=6 alive
- seed 57 reactive_r: births=25 pop=7 alive
- seed 11 reactive_r: births=24 pop=7 alive
- seed 25 reactive_r: births=24 pop=3 alive
- seed 3 evolutionary: births=23 pop=7 alive
- seed 37 reactive_r: births=23 pop=6 alive
- seed 18 reactive_r: births=22 pop=4 alive
- seed 93 reactive_r: births=22 pop=4 alive
- seed 3 reactive_r: births=20 pop=5 alive
- seed 4 reactive_r: births=20 pop=5 alive
- seed 39 reactive_r: births=18 pop=3 alive
- seed 90 reactive_r: births=17 pop=3 alive
- seed 15 reactive_r: births=16 pop=4 alive
- seed 34 reactive_r: births=15 pop=2 alive
- seed 71 reactive_r: births=14 pop=2 alive
- seed 16 evolutionary: births=10 pop=1 alive
- seed 88 evolutionary: births=10 pop=3 alive
- seed 92 evolutionary: births=9 pop=2 alive
- seed 99 evolutionary: births=9 pop=2 alive
- seed 22 reactive_r: births=7 pop=0 extinct@902
- seed 85 evolutionary: births=5 pop=0 extinct@998

Extinct in a controller that usually survives:
- seed 46 reactive: tte=699 food=163
- seed 59 reactive: tte=201 food=22
- seed 86 reactive: tte=568 food=125
- seed 10 reactive_r: tte=766 food=371
- seed 13 reactive_r: tte=506 food=130
- seed 22 reactive_r: tte=902 food=182
- seed 59 reactive_r: tte=201 food=22
- seed 72 reactive_r: tte=308 food=53

A visually interesting GIF is not evidence of emergence.
