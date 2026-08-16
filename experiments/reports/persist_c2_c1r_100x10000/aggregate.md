# Aggregate results — `persist_c2_c1r_100x10000`

Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.

- seeds: **100**
- controller-runs: **200**
- ticks: **10000**
- controllers: reactive_r, evolutionary

## Parameters

From **200** `metadata.json` file(s). Shared world fields should be identical across clones; seed and controller differ by design.

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
| `ticks` | 10000 |
| `snapshot_every` | 100 |
| `experiment_id` | persist_c2_c1r_100x10000 |

### Controller flags

| Controller | Reproduction | Genome |
|---|---|---|
| reactive_r | yes | no |
| evolutionary | yes | yes |

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
| reactive_r | 100 | 68 | 68.0% | 99 | 99.0% | 6.28 | 7.50 | 332.30 | 332.50 | 4488.3 | 4879.0 | 459.9 |
| evolutionary | 100 | 0 | 0.0% | 32 | 32.0% | 0.00 | 0.00 | 1.15 | 0.00 | 28.0 | 10.0 | 0.0 |

## Time to extinction

| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |
|---|---:|---:|---:|---:|---:|---:|
| reactive_r | 32 | 32.0% | 4649.9 | 4106.5 | 8288.0 | 10000.0 |
| evolutionary | 100 | 100.0% | 320.4 | 134.0 | 320.4 | 134.0 |

Censored TTE treats survivors as lasting the full run.

## Reproduction timing

| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |
|---|---:|---:|---:|---:|---:|
| reactive_r | 99.0% | 3.98 | 46.02 | 14.6 | 4.0 |
| evolutionary | 32.0% | 0.34 | 0.53 | 47.0 | 25.0 |

Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.

## Distributions

- **reactive_r** final pop `{0: 32, 1: 1, 3: 1, 4: 1, 5: 4, 6: 7, 7: 4, 8: 8, 9: 14, 10: 2, 11: 8, 12: 9, 13: 5, 14: 2, 15: 1, 16: 1}`; births `{0: 1, 1: 1, 4: 1, 7: 1, 15: 1, 18: 1, 30: 1, 38: 1, 43: 2, 53: 1, 61: 1, 64: 1, 66: 1, 72: 1, 75: 1, 93: 1, 101: 1, 170: 1, 174: 1, 178: 1, 183: 1, 203: 2, 207: 1, 211: 1, 216: 1, 221: 1, 224: 1, 235: 1, 237: 1, 248: 1, 265: 1, 269: 1, 271: 1, 282: 1, 291: 1, 294: 1, 295: 2, 297: 1, 303: 1, 304: 1, 305: 1, 309: 1, 320: 1, 321: 1, 326: 1, 330: 1, 331: 1, 334: 2, 341: 1, 356: 1, 358: 1, 361: 2, 380: 2, 395: 1, 400: 1, 407: 1, 416: 1, 418: 1, 419: 1, 424: 1, 441: 1, 444: 1, 449: 1, 450: 1, 464: 1, 470: 1, 472: 1, 481: 1, 484: 1, 486: 1, 491: 1, 497: 2, 505: 1, 513: 1, 514: 1, 515: 1, 519: 1, 523: 1, 530: 1, 531: 1, 538: 1, 544: 1, 545: 2, 576: 1, 593: 1, 604: 1, 615: 1, 619: 1, 620: 1, 646: 1, 656: 1, 667: 1}`
- **evolutionary** final pop `{0: 100}`; births `{0: 68, 1: 22, 2: 2, 3: 1, 4: 1, 5: 1, 10: 1, 11: 1, 13: 1, 14: 1, 29: 1}`

## Paired Δ (later − earlier, same seed)

| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |
|---|---|---:|---:|---:|---|---:|---:|
| final_population | evolutionary − reactive_r | 100 | -6.28 | -7.50 | [-7.26, -5.30] | -1.26 | 0 / 32 / 68 |
| births | evolutionary − reactive_r | 100 | -331.15 | -332.00 | [-366.92, -295.38] | -1.81 | 0 / 2 / 98 |
| resources_consumed_count | evolutionary − reactive_r | 100 | -4460.35 | -4878.50 | [-4891.31, -4029.39] | -2.03 | 0 / 0 / 100 |
| total_energy_final | evolutionary − reactive_r | 100 | -459.90 | -538.00 | [-530.25, -389.55] | -1.28 | 0 / 32 / 68 |
| time_to_extinction_censored | evolutionary − reactive_r | 100 | -7967.62 | -9792.00 | [-8578.14, -7357.10] | -2.56 | 1 / 0 / 99 |
| time_to_first_birth | evolutionary − reactive_r | 32 | 39.75 | 18.00 | [17.81, 61.69] | 0.63 | 23 / 7 / 2 |
| max_generation | evolutionary − reactive_r | 100 | -45.49 | -51.00 | [-49.70, -41.28] | -2.12 | 0 / 2 / 98 |
| survived | evolutionary − reactive_r | 100 | -0.68 | -1.00 | [-0.77, -0.59] | -1.45 | 0 / 32 / 68 |

Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.
Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.

## Outlier seeds (for follow-up GIFs, not evidence)

No non-reactive survivors.

Births ≥ 5:
- seed 27 reactive_r: births=667 pop=13 alive
- seed 55 reactive_r: births=656 pop=13 alive
- seed 84 reactive_r: births=646 pop=13 alive
- seed 80 reactive_r: births=620 pop=12 alive
- seed 43 reactive_r: births=619 pop=13 alive
- seed 8 reactive_r: births=615 pop=15 alive
- seed 23 reactive_r: births=604 pop=10 alive
- seed 38 reactive_r: births=593 pop=8 alive
- seed 98 reactive_r: births=576 pop=9 alive
- seed 14 reactive_r: births=545 pop=14 alive
- seed 58 reactive_r: births=545 pop=14 alive
- seed 74 reactive_r: births=544 pop=9 alive
- seed 87 reactive_r: births=538 pop=8 alive
- seed 53 reactive_r: births=531 pop=9 alive
- seed 96 reactive_r: births=530 pop=12 alive
- seed 48 reactive_r: births=523 pop=11 alive
- seed 83 reactive_r: births=519 pop=9 alive
- seed 24 reactive_r: births=515 pop=12 alive
- seed 47 reactive_r: births=514 pop=12 alive
- seed 12 reactive_r: births=513 pop=6 alive
- seed 65 reactive_r: births=505 pop=13 alive
- seed 82 reactive_r: births=497 pop=11 alive
- seed 100 reactive_r: births=497 pop=8 alive
- seed 51 reactive_r: births=491 pop=9 alive
- seed 36 reactive_r: births=486 pop=16 alive
- seed 64 reactive_r: births=484 pop=9 alive
- seed 86 reactive_r: births=481 pop=11 alive
- seed 61 reactive_r: births=472 pop=8 alive
- seed 60 reactive_r: births=470 pop=11 alive
- seed 73 reactive_r: births=464 pop=12 alive
- seed 77 reactive_r: births=450 pop=9 alive
- seed 33 reactive_r: births=449 pop=10 alive
- seed 31 reactive_r: births=444 pop=7 alive
- seed 32 reactive_r: births=441 pop=11 alive
- seed 28 reactive_r: births=424 pop=9 alive
- seed 16 reactive_r: births=419 pop=12 alive
- seed 19 reactive_r: births=418 pop=7 alive
- seed 97 reactive_r: births=416 pop=12 alive
- seed 17 reactive_r: births=407 pop=5 alive
- seed 99 reactive_r: births=400 pop=11 alive
- seed 75 reactive_r: births=395 pop=12 alive
- seed 26 reactive_r: births=380 pop=9 alive
- seed 42 reactive_r: births=380 pop=6 alive
- seed 1 reactive_r: births=361 pop=4 alive
- seed 52 reactive_r: births=361 pop=9 alive
- seed 68 reactive_r: births=358 pop=9 alive
- seed 92 reactive_r: births=356 pop=7 alive
- seed 69 reactive_r: births=341 pop=9 alive
- seed 11 reactive_r: births=334 pop=3 alive
- seed 78 reactive_r: births=334 pop=6 alive
- seed 54 reactive_r: births=331 pop=9 alive
- seed 30 reactive_r: births=330 pop=11 alive
- seed 5 reactive_r: births=326 pop=8 alive
- seed 95 reactive_r: births=321 pop=9 alive
- seed 6 reactive_r: births=320 pop=11 alive
- seed 91 reactive_r: births=309 pop=12 alive
- seed 21 reactive_r: births=305 pop=6 alive
- seed 41 reactive_r: births=304 pop=1 alive
- seed 9 reactive_r: births=303 pop=7 alive
- seed 57 reactive_r: births=297 pop=6 alive
- seed 85 reactive_r: births=295 pop=8 alive
- seed 89 reactive_r: births=295 pop=6 alive
- seed 44 reactive_r: births=294 pop=6 alive
- seed 94 reactive_r: births=291 pop=8 alive
- seed 93 reactive_r: births=282 pop=0 extinct@9305
- seed 40 reactive_r: births=271 pop=8 alive
- seed 4 reactive_r: births=269 pop=5 alive
- seed 56 reactive_r: births=265 pop=0 extinct@7828
- seed 81 reactive_r: births=248 pop=0 extinct@8387
- seed 37 reactive_r: births=237 pop=0 extinct@8899
- seed 3 reactive_r: births=235 pop=5 alive
- seed 7 reactive_r: births=224 pop=0 extinct@8194
- seed 18 reactive_r: births=221 pop=5 alive
- seed 39 reactive_r: births=216 pop=0 extinct@9457
- seed 79 reactive_r: births=211 pop=0 extinct@6153
- seed 66 reactive_r: births=207 pop=0 extinct@7998
- seed 49 reactive_r: births=203 pop=0 extinct@5177
- seed 62 reactive_r: births=203 pop=0 extinct@7124
- seed 88 reactive_r: births=183 pop=0 extinct@9018
- seed 70 reactive_r: births=178 pop=0 extinct@6352
- seed 20 reactive_r: births=174 pop=0 extinct@9726
- seed 76 reactive_r: births=170 pop=0 extinct@6167
- seed 50 reactive_r: births=101 pop=0 extinct@4024
- seed 63 reactive_r: births=93 pop=0 extinct@3346
- seed 45 reactive_r: births=75 pop=0 extinct@2809
- seed 29 reactive_r: births=72 pop=0 extinct@4189
- seed 2 reactive_r: births=66 pop=0 extinct@2559
- seed 46 reactive_r: births=64 pop=0 extinct@2474
- seed 25 reactive_r: births=61 pop=0 extinct@3579
- seed 15 reactive_r: births=53 pop=0 extinct@4920
- seed 35 reactive_r: births=43 pop=0 extinct@2153
- seed 67 reactive_r: births=43 pop=0 extinct@1244
- seed 71 reactive_r: births=38 pop=0 extinct@2721
- seed 10 reactive_r: births=30 pop=0 extinct@766
- seed 3 evolutionary: births=29 pop=0 extinct@1423
- seed 90 reactive_r: births=18 pop=0 extinct@1149
- seed 34 reactive_r: births=15 pop=0 extinct@1162
- seed 92 evolutionary: births=14 pop=0 extinct@1946
- seed 16 evolutionary: births=13 pop=0 extinct@1446
- seed 99 evolutionary: births=11 pop=0 extinct@1252
- seed 88 evolutionary: births=10 pop=0 extinct@1089
- seed 22 reactive_r: births=7 pop=0 extinct@902
- seed 85 evolutionary: births=5 pop=0 extinct@998

Extinct in a controller that usually survives:
- seed 2 reactive_r: tte=2559 food=1002
- seed 7 reactive_r: tte=8194 food=3078
- seed 10 reactive_r: tte=766 food=371
- seed 13 reactive_r: tte=506 food=130
- seed 15 reactive_r: tte=4920 food=947
- seed 20 reactive_r: tte=9726 food=3051
- seed 22 reactive_r: tte=902 food=182
- seed 25 reactive_r: tte=3579 food=1036
- seed 29 reactive_r: tte=4189 food=1095
- seed 34 reactive_r: tte=1162 food=237
- seed 35 reactive_r: tte=2153 food=639
- seed 37 reactive_r: tte=8899 food=3708
- seed 39 reactive_r: tte=9457 food=3285
- seed 45 reactive_r: tte=2809 food=988
- seed 46 reactive_r: tte=2474 food=1019
- seed 49 reactive_r: tte=5177 food=2786
- seed 50 reactive_r: tte=4024 food=1617
- seed 56 reactive_r: tte=7828 food=3481
- seed 59 reactive_r: tte=201 food=22
- seed 62 reactive_r: tte=7124 food=3283
- seed 63 reactive_r: tte=3346 food=1406
- seed 66 reactive_r: tte=7998 food=2930
- seed 67 reactive_r: tte=1244 food=618
- seed 70 reactive_r: tte=6352 food=2774
- seed 71 reactive_r: tte=2721 food=572
- seed 72 reactive_r: tte=308 food=53
- seed 76 reactive_r: tte=6167 food=2463
- seed 79 reactive_r: tte=6153 food=2867
- seed 81 reactive_r: tte=8387 food=3916
- seed 88 reactive_r: tte=9018 food=3672
- seed 90 reactive_r: tte=1149 food=374
- seed 93 reactive_r: tte=9305 food=4275

A visually interesting GIF is not evidence of emergence.
