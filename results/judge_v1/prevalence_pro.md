# STCG prevalence: `judge_v1` on SWE-bench Pro (public set)

- flagged (final score >= 3): 35% (258/731, CI 32%-39%)
- final scores: {1: 286, 2: 187, 3: 143, 4: 115}
- flagged by any judge: 54% (398/731, CI 51%-58%)
- uncertain (spread >= 2): 10% (71/731, CI 8%-12%)

| judge alone | flagged |
|---|---|
| claude | 38% (275/731, CI 34%-41%) |
| gpt61 | 52% (381/731, CI 48%-56%) |

| pair | Cohen's kappa | agree |
|---|---|---|
| claude~gpt61 | 0.621 | 81% |

## Corrected prevalence

Corrected = (flag rate - false-flag rate) / (recall - false-flag rate), with the judge's rates on the validation sets (dev + test). The false-flag rate is measured on Verified fine tasks only.

- false-flag rate: 4% (6/157, CI 2%-8%)
- recall, all overspecified validation tasks: 86% (161/187, CI 80%-90%) -> corrected prevalence 38.3%
- recall, `pro_narrow_original` only (same benchmark family): 76% (57/75, CI 65%-84%) -> corrected prevalence 43.6%

## By repository

| repo | flagged | score 3 | score 4 |
|---|---|---|---|
| ansible/ansible | 43% (41/96, CI 33%-53%) | 27 | 14 |
| internetarchive/openlibrary | 21% (19/91, CI 14%-30%) | 10 | 9 |
| flipt-io/flipt | 42% (36/85, CI 32%-53%) | 12 | 24 |
| qutebrowser/qutebrowser | 30% (24/79, CI 21%-41%) | 17 | 7 |
| gravitational/teleport | 46% (35/76, CI 35%-57%) | 9 | 26 |
| protonmail/webclients | 34% (22/65, CI 24%-46%) | 16 | 6 |
| future-architect/vuls | 35% (22/62, CI 25%-48%) | 11 | 11 |
| navidrome/navidrome | 35% (20/57, CI 24%-48%) | 10 | 10 |
| element-hq/element-web | 45% (25/56, CI 32%-58%) | 19 | 6 |
| NodeBB/NodeBB | 23% (10/44, CI 13%-37%) | 10 | 0 |
| tutao/tutanota | 20% (4/20, CI 8%-42%) | 2 | 2 |
