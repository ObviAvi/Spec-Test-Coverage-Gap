# Step 5: relaxation and regrading, flagged tasks

Prompt `relax_free_v1` (sha 941f9b813bf6). Agents: the top 30 Verified submissions.

## How failing patches failed (published per-test reports)

| group | tasks | failing patches | fail only new tests | break an old test |
|---|---|---|---|---|
| control | 113 | 812 | 51% (417/812, CI 48%-55%) | 46% (370/812, CI 42%-49%) |
| dev | 62 | 592 | 82% (486/592, CI 79%-85%) | 16% (94/592, CI 13%-19%) |
| flagged | 109 | 2434 | 90% (2186/2434, CI 89%-91%) | 9% (231/2434, CI 8%-11%) |

## Relaxations

- tasks with a patch that could flip: 108 of 117 in the group; run so far: 108
- outcome: {'valid': 82, 'declined': 26}; valid on the first attempt: 81
- failed checks across attempts: {'gold_fails': 1}
- lines changed per valid relaxation: median 10.0, max 127
- valid relaxations where a graded test now passes on the unfixed code: 22
- valid relaxations with no passing patch to run check 3 on: 22

## Regrading

- outcomes (one per submission and task): {'flip': 1069, 'still_fails': 595, 'patch_does_not_apply': 1}
- flip rate over regraded patches: 64% (1069/1664, CI 62%-67%)
- flip rate over every candidate patch, counting tasks without a valid relaxation as no flip: 49% (1069/2186, CI 47%-51%)
- tasks with at least one flip: 83% (68/82, CI 73%-90%)
- mean per-task share of patches that flip: 64%

| resolve band (top N) | flip rate |
|---|---|
| 0% | 54% (366/682, CI 50%-57%) |
| 1-50% | 73% (623/856, CI 70%-76%) |
| 51-89% | 64% (76/118, CI 55%-72%) |
| >=90% | 50% (4/8, CI 22%-78%) |

## Agents

Tasks gained per agent: min 27, median 35.5, max 45. Rank changed for 26 of 30; largest move 9 places.

| submission | resolved | flips | after | rank | rank after |
|---|---|---|---|---|---|
| 20251205_sonar-foundation-agent_claude-opus-4-5 | 396 | 32 | 428 | 1 | 1 |
| 20251215_livesweagent_claude-opus-4-5 | 396 | 32 | 428 | 1 | 1 |
| 20250928_trae_doubao_seed_code | 394 | 33 | 427 | 3 | 3 |
| 20251127_openhands_claude-opus-4-5 | 388 | 37 | 425 | 4 | 5 |
| 20251120_livesweagent_gemini-3-pro-preview | 387 | 33 | 420 | 5 | 6 |
| 20250804_epam-ai-run-claude-4-sonnet | 384 | 30 | 414 | 6 | 9 |
| 20250902_atlassian-rovo-dev | 384 | 42 | 426 | 6 | 4 |
| 20250819_ACoder | 382 | 29 | 411 | 8 | 13 |
| 20250901_warp | 378 | 40 | 418 | 9 | 7 |
| 20260217_mini-v2.0.0_claude-4-6-opus | 378 | 35 | 413 | 9 | 10 |
| 20250612_trae | 376 | 31 | 407 | 11 | 16 |
| 20250731_harness_ai | 374 | 34 | 408 | 12 | 15 |
| 20251103_sonar-foundation-agent_claude-sonnet-4-5 | 374 | 41 | 415 | 12 | 8 |
| 20250720_Lingxi-v1.5_claude-4-sonnet-20250514 | 373 | 30 | 403 | 14 | 21 |
| 20250915_JoyCode | 373 | 27 | 400 | 14 | 23 |
| 20250603_Refact_Agent_claude-4-sonnet | 372 | 32 | 404 | 16 | 17 |
| 20251124_mini-v1.16.0_claude-opus-4-5-20251101 | 372 | 40 | 412 | 16 | 12 |
| 20251118_mini-v1.15.0_gemini-3-pro-preview-20251118 | 371 | 38 | 409 | 18 | 14 |
| 20251103_SalesforceAIResearch_SAGE_OpenHands | 369 | 44 | 413 | 19 | 10 |
| 20250522_tools_claude-4-opus | 366 | 38 | 404 | 20 | 17 |
| 20251021_SalesforceAIResearch_SAGE_bash_only | 365 | 39 | 404 | 21 | 17 |
| 20250522_tools_claude-4-sonnet | 362 | 37 | 399 | 22 | 24 |
| 20250807_openhands_gpt5 | 359 | 42 | 401 | 23 | 22 |
| 20251211_mini-v1.17.2_gpt-5.2-2025-12-11-high | 359 | 45 | 404 | 23 | 17 |
| 20250710_bloop | 356 | 35 | 391 | 25 | 28 |
| 20250715_qodo_command | 356 | 36 | 392 | 25 | 26 |
| 20251014_Lingxi_kimi_k2 | 356 | 29 | 385 | 25 | 29 |
| 20250623_warp | 355 | 37 | 392 | 28 | 26 |
| 20250611_moatless_claude-4-sonnet-20250514 | 354 | 41 | 395 | 29 | 25 |
| 20250519_trae | 353 | 30 | 383 | 30 | 30 |
