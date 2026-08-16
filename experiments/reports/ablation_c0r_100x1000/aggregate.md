# Aggregate results — `ablation_c0r_100x1000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **300**
- ticks: **1000**
- controllers: random, random_r, reactive_r

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
| `experiment_id` | ablation_c0r_100x1000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| random | no | no |
| random_r | yes | no |
| reactive_r | yes | no |

Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics.

### Versions

| Field | Value |
|---|---|
| `config_version` | 0.2 |
| `world_version` | m1-v1 |
| `controller_version` | m1-v1 |
| `git_commit` | 0deb1f9c08314363dcf9643f6348fdb8d6c1d8a8 |

## Survival and births

| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 100 | 0 | 0.0% | 0 | 0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 6.7 | 6.0 | 0.0 |
| random_r | 100 | 0 | 0.0% | 6 | 6.0% | 0.00 | 0.00 | 0.06 | 0.00 | 6.9 | 6.0 | 0.0 |
| reactive_r | 100 | 95 | 95.0% | 99 | 99.0% | 8.48 | 9.00 | 38.36 | 37.50 | 526.6 | 531.5 | 602.2 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| random | 100 | 100.0% | 108.0 | 105.0 | 108.0 | 105.0 |
| random_r | 100 | 100.0% | 105.8 | 103.5 | 105.8 | 103.5 |
| reactive_r | 5 | 5.0% | 536.6 | 506.0 | 976.8 | 1000.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| random | 0.0% | 0.00 | 0.00 | — | — |
| random_r | 6.0% | 0.06 | 0.06 | 15.5 | 17.0 |
| reactive_r | 99.0% | 3.98 | 7.17 | 14.6 | 4.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **random** final pop `{0: 100}`; births `{0: 100}`
- **random_r** final pop `{0: 100}`; births `{0: 94, 1: 6}`
- **reactive_r** final pop `{0: 5, 2: 2, 3: 3, 4: 5, 5: 4, 6: 8, 7: 8, 8: 11, 9: 11, 10: 12, 11: 11, 12: 6, 13: 9, 14: 2, 15: 2, 16: 1}`; births `{0: 1, 1: 1, 4: 1, 7: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 20: 2, 22: 2, 23: 1, 24: 2, 25: 1, 26: 2, 27: 1, 28: 4, 29: 1, 30: 3, 31: 4, 32: 3, 33: 5, 35: 4, 36: 1, 37: 5, 38: 3, 39: 2, 40: 2, 41: 4, 42: 2, 43: 1, 44: 1, 45: 3, 46: 1, 47: 4, 48: 1, 50: 1, 51: 1, 52: 3, 53: 5, 55: 3, 57: 1, 58: 2, 59: 3, 60: 2, 62: 2, 66: 1, 67: 1, 70: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | random_r − random | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| births | random_r − random | 100 | 0.06 | 0.00 | [0.01, 0.11] | 0.25 | 6 / 94 / 0 |
| resources_consumed_count | random_r − random | 100 | 0.12 | 0.00 | [-0.04, 0.28] | 0.15 | 4 / 95 / 1 |
| total_energy_final | random_r − random | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| time_to_extinction_censored | random_r − random | 100 | -2.23 | 0.00 | [-4.53, 0.07] | -0.19 | 0 / 94 / 6 |
| max_generation | random_r − random | 100 | 0.06 | 0.00 | [0.01, 0.11] | 0.25 | 6 / 94 / 0 |
| survived | random_r − random | 100 | 0.00 | 0.00 | [0.00, 0.00] | 0.00 | 0 / 100 / 0 |
| final_population | reactive_r − random | 100 | 8.48 | 9.00 | [7.77, 9.19] | 2.33 | 95 / 5 / 0 |
| births | reactive_r − random | 100 | 38.36 | 37.50 | [35.45, 41.27] | 2.59 | 99 / 1 / 0 |
| resources_consumed_count | reactive_r − random | 100 | 519.86 | 528.50 | [490.65, 549.07] | 3.49 | 100 / 0 / 0 |
| total_energy_final | reactive_r − random | 100 | 602.22 | 631.50 | [551.51, 652.93] | 2.33 | 95 / 5 / 0 |
| time_to_extinction_censored | reactive_r − random | 100 | 868.85 | 894.50 | [845.66, 892.04] | 7.34 | 100 / 0 / 0 |
| max_generation | reactive_r − random | 100 | 7.17 | 7.00 | [6.68, 7.66] | 2.88 | 99 / 1 / 0 |
| survived | reactive_r − random | 100 | 0.95 | 1.00 | [0.91, 0.99] | 4.34 | 95 / 5 / 0 |
| final_population | reactive_r − random_r | 100 | 8.48 | 9.00 | [7.77, 9.19] | 2.33 | 95 / 5 / 0 |
| births | reactive_r − random_r | 100 | 38.30 | 37.50 | [35.40, 41.20] | 2.59 | 99 / 1 / 0 |
| resources_consumed_count | reactive_r − random_r | 100 | 519.74 | 528.50 | [490.56, 548.92] | 3.49 | 100 / 0 / 0 |
| total_energy_final | reactive_r − random_r | 100 | 602.22 | 631.50 | [551.51, 652.93] | 2.33 | 95 / 5 / 0 |
| time_to_extinction_censored | reactive_r − random_r | 100 | 871.08 | 895.00 | [847.90, 894.26] | 7.37 | 100 / 0 / 0 |
| time_to_first_birth | reactive_r − random_r | 6 | -12.33 | -13.50 | [-20.14, -4.53] | -1.26 | 0 / 0 / 6 |
| max_generation | reactive_r − random_r | 100 | 7.11 | 7.00 | [6.63, 7.59] | 2.88 | 99 / 1 / 0 |
| survived | reactive_r − random_r | 100 | 0.95 | 1.00 | [0.91, 0.99] | 4.34 | 95 / 5 / 0 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

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
- seed 22 reactive_r: births=7 pop=0 extinct@902

Extinct in a controller that usually survives:
- seed 10 reactive_r: tte=766 food=371
- seed 13 reactive_r: tte=506 food=130
- seed 22 reactive_r: tte=902 food=182
- seed 59 reactive_r: tte=201 food=22
- seed 72 reactive_r: tte=308 food=53

A visually interesting GIF is not evidence of emergence.
