# Aggregate results — `diag_c2_oracle_r_100x1000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **300**
- ticks: **1000**
- controllers: reactive_r, evolutionary, evolutionary_oracle_r

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
| `experiment_id` | diag_c2_oracle_r_100x1000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| reactive_r | yes | no |
| evolutionary | yes | yes |
| evolutionary_oracle_r | yes | no |

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
| reactive_r | 100 | 95 | 95.0% | 99 | 99.0% | 8.48 | 9.00 | 38.36 | 37.50 | 526.6 | 531.5 | 602.2 |
| evolutionary | 100 | 6 | 6.0% | 32 | 32.0% | 0.16 | 0.00 | 0.99 | 0.00 | 25.3 | 10.0 | 9.9 |
| evolutionary_oracle_r | 100 | 17 | 17.0% | 96 | 96.0% | 0.49 | 0.00 | 8.12 | 5.00 | 121.1 | 86.0 | 36.4 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| reactive_r | 5 | 5.0% | 536.6 | 506.0 | 976.8 | 1000.0 |
| evolutionary | 94 | 94.0% | 251.1 | 129.5 | 296.0 | 134.0 |
| evolutionary_oracle_r | 83 | 83.0% | 458.1 | 433.0 | 550.2 | 486.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| reactive_r | 99.0% | 3.98 | 7.17 | 14.6 | 4.0 |
| evolutionary | 32.0% | 0.34 | 0.48 | 47.0 | 25.0 |
| evolutionary_oracle_r | 96.0% | 1.95 | 3.00 | 45.7 | 21.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **reactive_r** final pop `{0: 5, 2: 2, 3: 3, 4: 5, 5: 4, 6: 8, 7: 8, 8: 11, 9: 11, 10: 12, 11: 11, 12: 6, 13: 9, 14: 2, 15: 2, 16: 1}`; births `{0: 1, 1: 1, 4: 1, 7: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 20: 2, 22: 2, 23: 1, 24: 2, 25: 1, 26: 2, 27: 1, 28: 4, 29: 1, 30: 3, 31: 4, 32: 3, 33: 5, 35: 4, 36: 1, 37: 5, 38: 3, 39: 2, 40: 2, 41: 4, 42: 2, 43: 1, 44: 1, 45: 3, 46: 1, 47: 4, 48: 1, 50: 1, 51: 1, 52: 3, 53: 5, 55: 3, 57: 1, 58: 2, 59: 3, 60: 2, 62: 2, 66: 1, 67: 1, 70: 1}`
- **evolutionary** final pop `{0: 94, 1: 2, 2: 2, 3: 1, 7: 1}`; births `{0: 68, 1: 22, 2: 2, 3: 1, 4: 1, 5: 1, 9: 2, 10: 2, 23: 1}`
- **evolutionary_oracle_r** final pop `{0: 83, 1: 7, 2: 2, 3: 1, 4: 3, 5: 2, 6: 1, 7: 1}`; births `{0: 4, 1: 12, 2: 13, 3: 9, 4: 11, 5: 6, 6: 5, 7: 4, 8: 4, 9: 3, 10: 5, 11: 1, 12: 2, 13: 3, 15: 2, 16: 1, 17: 1, 18: 3, 20: 1, 23: 3, 26: 1, 27: 1, 31: 1, 32: 2, 36: 1, 42: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | evolutionary − reactive_r | 100 | -8.32 | -9.00 | [-9.06, -7.58] | -2.21 | 1 / 5 / 94 |
| births | evolutionary − reactive_r | 100 | -37.37 | -36.50 | [-40.38, -34.36] | -2.44 | 1 / 2 / 97 |
| resources_consumed_count | evolutionary − reactive_r | 100 | -501.28 | -504.50 | [-532.31, -470.25] | -3.17 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive_r | 100 | -592.27 | -626.50 | [-644.28, -540.26] | -2.23 | 1 / 5 / 94 |
| time_to_extinction_censored | evolutionary − reactive_r | 100 | -680.84 | -857.00 | [-740.80, -620.88] | -2.23 | 1 / 6 / 93 |
| time_to_first_birth | evolutionary − reactive_r | 32 | 39.75 | 18.00 | [17.81, 61.69] | 0.63 | 23 / 7 / 2 |
| max_generation | evolutionary − reactive_r | 100 | -6.69 | -7.00 | [-7.21, -6.17] | -2.53 | 0 / 3 / 97 |
| survived | evolutionary − reactive_r | 100 | -0.89 | -1.00 | [-0.95, -0.83] | -2.83 | 0 / 11 / 89 |
| final_population | evolutionary_oracle_r − reactive_r | 100 | -7.99 | -8.00 | [-8.69, -7.29] | -2.25 | 2 / 3 / 95 |
| births | evolutionary_oracle_r − reactive_r | 100 | -30.24 | -31.50 | [-32.95, -27.53] | -2.19 | 2 / 0 / 98 |
| resources_consumed_count | evolutionary_oracle_r − reactive_r | 100 | -405.53 | -420.00 | [-435.50, -375.56] | -2.65 | 2 / 0 / 98 |
| total_energy_final | evolutionary_oracle_r − reactive_r | 100 | -565.83 | -570.50 | [-616.08, -515.58] | -2.21 | 2 / 3 / 95 |
| time_to_extinction_censored | evolutionary_oracle_r − reactive_r | 100 | -426.61 | -509.50 | [-485.70, -367.52] | -1.42 | 3 / 15 / 82 |
| time_to_first_birth | evolutionary_oracle_r − reactive_r | 95 | 31.59 | 11.00 | [19.72, 43.46] | 0.54 | 62 / 23 / 10 |
| max_generation | evolutionary_oracle_r − reactive_r | 100 | -4.17 | -4.00 | [-4.80, -3.54] | -1.29 | 7 / 5 / 88 |
| survived | evolutionary_oracle_r − reactive_r | 100 | -0.78 | -1.00 | [-0.87, -0.69] | -1.69 | 2 / 18 / 80 |
| final_population | evolutionary_oracle_r − evolutionary | 100 | 0.33 | 0.00 | [0.01, 0.65] | 0.20 | 16 / 78 / 6 |
| births | evolutionary_oracle_r − evolutionary | 100 | 7.13 | 4.00 | [5.33, 8.93] | 0.78 | 88 / 7 / 5 |
| resources_consumed_count | evolutionary_oracle_r − evolutionary | 100 | 95.75 | 70.50 | [76.56, 114.94] | 0.98 | 92 / 1 / 7 |
| total_energy_final | evolutionary_oracle_r − evolutionary | 100 | 26.44 | 0.00 | [3.84, 49.04] | 0.23 | 16 / 78 / 6 |
| time_to_extinction_censored | evolutionary_oracle_r − evolutionary | 100 | 254.23 | 268.00 | [179.76, 328.70] | 0.67 | 80 / 1 / 19 |
| time_to_first_birth | evolutionary_oracle_r − evolutionary | 31 | -18.84 | -10.00 | [-44.41, 6.74] | -0.26 | 9 / 4 / 18 |
| max_generation | evolutionary_oracle_r − evolutionary | 100 | 2.52 | 2.00 | [1.96, 3.08] | 0.88 | 83 / 12 / 5 |
| survived | evolutionary_oracle_r − evolutionary | 100 | 0.11 | 0.00 | [0.02, 0.20] | 0.25 | 16 / 79 / 5 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

Non-reactive survivors (n=23):
- seed 3 evolutionary: pop=7 births=23 food=337 energy=406
- seed 74 evolutionary_oracle_r: pop=7 births=31 food=347 energy=485
- seed 43 evolutionary_oracle_r: pop=6 births=32 food=356 energy=460
- seed 47 evolutionary_oracle_r: pop=5 births=20 food=286 energy=380
- seed 83 evolutionary_oracle_r: pop=5 births=16 food=240 energy=395
- seed 26 evolutionary_oracle_r: pop=4 births=23 food=314 energy=224
- seed 51 evolutionary_oracle_r: pop=4 births=18 food=322 energy=298
- seed 53 evolutionary_oracle_r: pop=4 births=42 food=418 energy=301
- seed 17 evolutionary_oracle_r: pop=3 births=13 food=173 energy=307
- seed 88 evolutionary: pop=3 births=10 food=104 energy=157
- seed 61 evolutionary_oracle_r: pop=2 births=27 food=272 energy=172
- seed 64 evolutionary_oracle_r: pop=2 births=32 food=345 energy=145
- seed 92 evolutionary: pop=2 births=9 food=151 energy=220
- seed 99 evolutionary: pop=2 births=9 food=138 energy=118
- seed 8 evolutionary_oracle_r: pop=1 births=18 food=256 energy=58
- seed 14 evolutionary_oracle_r: pop=1 births=23 food=264 energy=47
- seed 16 evolutionary: pop=1 births=10 food=93 energy=75
- seed 19 evolutionary_oracle_r: pop=1 births=18 food=233 energy=131
- seed 22 evolutionary_oracle_r: pop=1 births=6 food=143 energy=56
- seed 40 evolutionary: pop=1 births=3 food=94 energy=19
- seed 59 evolutionary_oracle_r: pop=1 births=26 food=294 energy=94
- seed 82 evolutionary_oracle_r: pop=1 births=10 food=172 energy=10
- seed 92 evolutionary_oracle_r: pop=1 births=9 food=181 energy=76

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
- seed 53 evolutionary_oracle_r: births=42 pop=4 alive
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
- seed 84 evolutionary_oracle_r: births=36 pop=0 extinct@996
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
- seed 43 evolutionary_oracle_r: births=32 pop=6 alive
- seed 64 evolutionary_oracle_r: births=32 pop=2 alive
- seed 69 reactive_r: births=32 pop=8 alive
- seed 78 reactive_r: births=32 pop=8 alive
- seed 45 reactive_r: births=31 pop=7 alive
- seed 56 reactive_r: births=31 pop=8 alive
- seed 62 reactive_r: births=31 pop=6 alive
- seed 74 evolutionary_oracle_r: births=31 pop=7 alive
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
- seed 61 evolutionary_oracle_r: births=27 pop=2 alive
- seed 29 reactive_r: births=26 pop=8 alive
- seed 59 evolutionary_oracle_r: births=26 pop=1 alive
- seed 95 reactive_r: births=26 pop=6 alive
- seed 57 reactive_r: births=25 pop=7 alive
- seed 11 reactive_r: births=24 pop=7 alive
- seed 25 reactive_r: births=24 pop=3 alive
- seed 3 evolutionary: births=23 pop=7 alive
- seed 14 evolutionary_oracle_r: births=23 pop=1 alive
- seed 26 evolutionary_oracle_r: births=23 pop=4 alive
- seed 37 reactive_r: births=23 pop=6 alive
- seed 65 evolutionary_oracle_r: births=23 pop=0 extinct@820
- seed 18 reactive_r: births=22 pop=4 alive
- seed 93 reactive_r: births=22 pop=4 alive
- seed 3 reactive_r: births=20 pop=5 alive
- seed 4 reactive_r: births=20 pop=5 alive
- seed 47 evolutionary_oracle_r: births=20 pop=5 alive
- seed 8 evolutionary_oracle_r: births=18 pop=1 alive
- seed 19 evolutionary_oracle_r: births=18 pop=1 alive
- seed 39 reactive_r: births=18 pop=3 alive
- seed 51 evolutionary_oracle_r: births=18 pop=4 alive
- seed 68 evolutionary_oracle_r: births=17 pop=0 extinct@796
- seed 90 reactive_r: births=17 pop=3 alive
- seed 15 reactive_r: births=16 pop=4 alive
- seed 83 evolutionary_oracle_r: births=16 pop=5 alive
- seed 34 reactive_r: births=15 pop=2 alive
- seed 55 evolutionary_oracle_r: births=15 pop=0 extinct@551
- seed 73 evolutionary_oracle_r: births=15 pop=0 extinct@820
- seed 71 reactive_r: births=14 pop=2 alive
- seed 12 evolutionary_oracle_r: births=13 pop=0 extinct@606
- seed 17 evolutionary_oracle_r: births=13 pop=3 alive
- seed 91 evolutionary_oracle_r: births=13 pop=0 extinct@752
- seed 10 evolutionary_oracle_r: births=12 pop=0 extinct@576
- seed 87 evolutionary_oracle_r: births=12 pop=0 extinct@840
- seed 78 evolutionary_oracle_r: births=11 pop=0 extinct@807
- seed 16 evolutionary: births=10 pop=1 alive
- seed 28 evolutionary_oracle_r: births=10 pop=0 extinct@637
- seed 36 evolutionary_oracle_r: births=10 pop=0 extinct@703
- seed 82 evolutionary_oracle_r: births=10 pop=1 alive
- seed 86 evolutionary_oracle_r: births=10 pop=0 extinct@418
- seed 88 evolutionary: births=10 pop=3 alive
- seed 99 evolutionary_oracle_r: births=10 pop=0 extinct@574
- seed 3 evolutionary_oracle_r: births=9 pop=0 extinct@967
- seed 58 evolutionary_oracle_r: births=9 pop=0 extinct@787
- seed 92 evolutionary: births=9 pop=2 alive
- seed 92 evolutionary_oracle_r: births=9 pop=1 alive
- seed 99 evolutionary: births=9 pop=2 alive
- seed 27 evolutionary_oracle_r: births=8 pop=0 extinct@435
- seed 75 evolutionary_oracle_r: births=8 pop=0 extinct@513
- seed 94 evolutionary_oracle_r: births=8 pop=0 extinct@525
- seed 98 evolutionary_oracle_r: births=8 pop=0 extinct@526
- seed 7 evolutionary_oracle_r: births=7 pop=0 extinct@475
- seed 22 reactive_r: births=7 pop=0 extinct@902
- seed 24 evolutionary_oracle_r: births=7 pop=0 extinct@509
- seed 32 evolutionary_oracle_r: births=7 pop=0 extinct@385
- seed 48 evolutionary_oracle_r: births=7 pop=0 extinct@461
- seed 16 evolutionary_oracle_r: births=6 pop=0 extinct@560
- seed 22 evolutionary_oracle_r: births=6 pop=1 alive
- seed 33 evolutionary_oracle_r: births=6 pop=0 extinct@347
- seed 79 evolutionary_oracle_r: births=6 pop=0 extinct@316
- seed 81 evolutionary_oracle_r: births=6 pop=0 extinct@709
- seed 9 evolutionary_oracle_r: births=5 pop=0 extinct@620
- seed 31 evolutionary_oracle_r: births=5 pop=0 extinct@364
- seed 42 evolutionary_oracle_r: births=5 pop=0 extinct@491
- seed 49 evolutionary_oracle_r: births=5 pop=0 extinct@311
- seed 77 evolutionary_oracle_r: births=5 pop=0 extinct@446
- seed 85 evolutionary: births=5 pop=0 extinct@998
- seed 85 evolutionary_oracle_r: births=5 pop=0 extinct@604

Extinct in a controller that usually survives:
- seed 10 reactive_r: tte=766 food=371
- seed 13 reactive_r: tte=506 food=130
- seed 22 reactive_r: tte=902 food=182
- seed 59 reactive_r: tte=201 food=22
- seed 72 reactive_r: tte=308 food=53

A visually interesting GIF is not evidence of emergence.
