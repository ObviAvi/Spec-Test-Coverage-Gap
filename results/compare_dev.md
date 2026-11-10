# Prompt comparison on `dev` (138 tasks, base `judge_v1`)

## Panel

| prompt | recall | false-flag rate | recall, openai_excluded | recall, pro_narrow_original | judge kappa | uncertain |
|---|---|---|---|---|---|---|
| judge_v1 | 81% (61/75, CI 71%-89%) | 3% (2/63, CI 1%-11%) | 39/45 | 22/30 | 0.78 | 10 |
| judge_v1_rerun | 80% (60/75, CI 70%-87%) | 5% (3/63, CI 2%-13%) | 40/45 | 20/30 | 0.77 | 12 |
| judge_v1_gold | 87% (65/75, CI 77%-93%) | 5% (3/63, CI 2%-13%) | 41/45 | 24/30 | 0.87 | 5 |
| baseline_v1 | 72% (54/75, CI 61%-81%) | 6% (4/63, CI 2%-15%) | 38/45 | 16/30 | 0.78 | 4 |

## Each judge alone

| prompt | judge | recall | false-flag rate |
|---|---|---|---|
| judge_v1 | claude | 83% (62/75, CI 73%-90%) | 3% (2/63, CI 1%-11%) |
| judge_v1 | gpt61 | 88% (66/75, CI 79%-94%) | 17% (11/63, CI 10%-29%) |
| judge_v1_rerun | claude | 81% (61/75, CI 71%-89%) | 5% (3/63, CI 2%-13%) |
| judge_v1_rerun | gpt61 | 88% (66/75, CI 79%-94%) | 19% (12/63, CI 11%-30%) |
| judge_v1_gold | claude | 87% (65/75, CI 77%-93%) | 5% (3/63, CI 2%-13%) |
| judge_v1_gold | gpt61 | 88% (66/75, CI 79%-94%) | 17% (11/63, CI 10%-29%) |
| baseline_v1 | claude | 81% (61/75, CI 71%-89%) | 6% (4/63, CI 2%-15%) |
| baseline_v1 | gpt61 | 77% (58/75, CI 67%-85%) | 13% (8/63, CI 7%-23%) |

## Changes against `judge_v1`

Same tasks, so every difference is a task whose score or flag moved. Kappa is between the two runs' flags.

| prompt | scorer | same score | newly flagged | unflagged | kappa |
|---|---|---|---|---|---|
| judge_v1_rerun | panel | 126/138 | 3 | 3 | 0.91 |
| judge_v1_rerun | claude | 123/138 | 2 | 2 | 0.94 |
| judge_v1_rerun | gpt61 | 128/138 | 2 | 1 | 0.96 |
| judge_v1_gold | panel | 126/138 | 5 | 0 | 0.93 |
| judge_v1_gold | claude | 118/138 | 4 | 0 | 0.94 |
| judge_v1_gold | gpt61 | 129/138 | 2 | 2 | 0.94 |
| baseline_v1 | panel | 104/138 | 2 | 7 | 0.87 |
| baseline_v1 | claude | 91/138 | 2 | 1 | 0.96 |
| baseline_v1 | gpt61 | 92/138 | 1 | 12 | 0.81 |

Panel flag changes by expected label:

| prompt | overspecified: flag lost | overspecified: flag gained | fine: flag gained | fine: flag lost |
|---|---|---|---|---|
| judge_v1_rerun | 3 | 2 | 1 | 0 |
| judge_v1_gold | 0 | 4 | 1 | 0 |
| baseline_v1 | 7 | 0 | 2 | 0 |

### Tasks whose panel flag changed: `judge_v1_rerun` (6)

- `verified/pydata__xarray-2905` [agent_consensus, fine] {'claude': 2, 'gpt61': 4} -> {'claude': 3, 'gpt61': 4}
- `full/sympy__sympy-16334` [openai_excluded, overspecified] {'claude': 3, 'gpt61': 2} -> {'claude': 3, 'gpt61': 4}
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original, overspecified] {'claude': 4, 'gpt61': 4} -> {'claude': 2, 'gpt61': 4}
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 3, 'gpt61': 1}
- `pro/instance_internetarchive__openlibrary-a48fd6ba9482c527602bc081491d9e8ae6e8226c-vfa6ff903cb27f336e17654595dd900fa943dcd91` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 2, 'gpt61': 3}
- `pro/instance_internetarchive__openlibrary-e1e502986a3b003899a8347ac8a7ff7b08cbfc39-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original, overspecified] {'claude': 2, 'gpt61': 3} -> {'claude': 3, 'gpt61': 3}

### Tasks whose panel flag changed: `judge_v1_gold` (5)

- `verified/pydata__xarray-2905` [agent_consensus, fine] {'claude': 2, 'gpt61': 4} -> {'claude': 3, 'gpt61': 4}
- `full/django__django-13199` [openai_excluded, overspecified] {'claude': 2, 'gpt61': 3} -> {'claude': 3, 'gpt61': 3}
- `full/sympy__sympy-16334` [openai_excluded, overspecified] {'claude': 3, 'gpt61': 2} -> {'claude': 3, 'gpt61': 4}
- `pro/instance_internetarchive__openlibrary-e1e502986a3b003899a8347ac8a7ff7b08cbfc39-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original, overspecified] {'claude': 2, 'gpt61': 3} -> {'claude': 3, 'gpt61': 3}
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original, overspecified] {'claude': 2, 'gpt61': 4} -> {'claude': 4, 'gpt61': 4}

### Tasks whose panel flag changed: `baseline_v1` (9)

- `verified/pydata__xarray-2905` [agent_consensus, fine] {'claude': 2, 'gpt61': 4} -> {'claude': 3, 'gpt61': 3}
- `verified/django__django-13807` [agent_consensus, fine] {'claude': 2, 'gpt61': 2} -> {'claude': 3, 'gpt61': 3}
- `full/django__django-13447` [openai_excluded, overspecified] {'claude': 3, 'gpt61': 4} -> {'claude': 3, 'gpt61': 1}
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original, overspecified] {'claude': 4, 'gpt61': 4} -> {'claude': 3, 'gpt61': 1}
- `pro/instance_future-architect__vuls-030b2e03525d68d74cb749959aac2d7f3fc0effa` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 3, 'gpt61': 2}
- `pro/instance_future-architect__vuls-fd18df1dd4e4360f8932bc4b894bd8b40d654e7c` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 3, 'gpt61': 2}
- `pro/instance_gravitational__teleport-87a593518b6ce94624f6c28516ce38cc30cbea5a` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 3, 'gpt61': 2}
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 3, 'gpt61': 1}
- `pro/instance_internetarchive__openlibrary-9bdfd29fac883e77dcbc4208cab28c06fd963ab2-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c` [pro_narrow_original, overspecified] {'claude': 3, 'gpt61': 3} -> {'claude': 2, 'gpt61': 3}
