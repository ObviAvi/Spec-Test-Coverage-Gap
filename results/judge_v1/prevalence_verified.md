# STCG prevalence: `judge_v1` on SWE-bench Verified

- flagged (final score >= 3): 23% (117/500, CI 20%-27%)
- final scores: {1: 167, 2: 216, 3: 78, 4: 39}
- flagged by any judge: 41% (204/500, CI 37%-45%)
- uncertain (spread >= 2): 11% (57/500, CI 9%-14%)

| judge alone | flagged |
|---|---|
| claude | 25% (123/500, CI 21%-29%) |
| gpt61 | 40% (198/500, CI 35%-44%) |

| pair | Cohen's kappa | agree |
|---|---|---|
| claude~gpt61 | 0.611 | 83% |

## Corrected prevalence

- judge recall on validation (dev + test): 86% (161/187, CI 80%-90%)
- judge false-flag rate on validation (dev + test): 4% (6/157, CI 2%-8%)
- corrected prevalence, (flag rate - false-flag rate) / (recall - false-flag rate): 23.8%

## Flag and agent resolve rate

Resolve rate = share of submissions in SWE-bench/experiments that resolve the task (top 30 by resolve count, or all 155).

| submissions | flagged tasks | not flagged |
|---|---|---|
| top 30 | 31% | 88% |
| all 155 | 17% | 62% |

Resolve-rate columns in the tables below use the top 30 submissions.

## By share of the top 30 submissions that resolve the task

| resolved by | flagged | score 3 | score 4 | resolve rate, flagged | resolve rate, not flagged |
|---|---|---|---|---|---|
| 0% | 85% (33/39, CI 70%-93%) | 19 | 14 | 0% | 0% |
| 1-50% | 63% (52/82, CI 53%-73%) | 33 | 19 | 19% | 29% |
| 51-89% | 26% (18/70, CI 17%-37%) | 16 | 2 | 69% | 72% |
| >=90% | 5% (14/309, CI 3%-7%) | 10 | 4 | 97% | 98% |

## By OpenAI difficulty rating

| difficulty | flagged | score 3 | score 4 | resolve rate, flagged | resolve rate, not flagged |
|---|---|---|---|---|---|
| <15 min fix | 13% (26/194, CI 9%-19%) | 18 | 8 | 41% | 93% |
| 15 min - 1 hour | 25% (65/261, CI 20%-30%) | 43 | 22 | 32% | 85% |
| 1-4 hours | 55% (23/42, CI 40%-69%) | 15 | 8 | 14% | 68% |
| >4 hours | 100% (3/3, CI 44%-100%) | 2 | 1 | 30% | - |

## By repository

| repo | flagged | score 3 | score 4 | resolve rate, flagged | resolve rate, not flagged |
|---|---|---|---|---|---|
| django/django | 20% (46/231, CI 15%-26%) | 33 | 13 | 32% | 89% |
| sympy/sympy | 31% (23/75, CI 21%-42%) | 17 | 6 | 26% | 92% |
| sphinx-doc/sphinx | 25% (11/44, CI 15%-39%) | 9 | 2 | 31% | 80% |
| matplotlib/matplotlib | 26% (9/34, CI 15%-43%) | 3 | 6 | 24% | 87% |
| scikit-learn/scikit-learn | 25% (8/32, CI 13%-42%) | 4 | 4 | 61% | 98% |
| astropy/astropy | 27% (6/22, CI 13%-48%) | 5 | 1 | 15% | 73% |
| pydata/xarray | 23% (5/22, CI 10%-43%) | 3 | 2 | 37% | 95% |
| pytest-dev/pytest | 16% (3/19, CI 6%-38%) | 1 | 2 | 21% | 96% |
| pylint-dev/pylint | 50% (5/10, CI 24%-76%) | 2 | 3 | 20% | 55% |
| psf/requests | 0% (0/8, CI 0%-32%) | 0 | 0 | - | 63% |
| mwaskom/seaborn | 50% (1/2, CI 9%-91%) | 1 | 0 | 17% | 73% |
| pallets/flask | 0% (0/1, CI 0%-79%) | 0 | 0 | - | 100% |
