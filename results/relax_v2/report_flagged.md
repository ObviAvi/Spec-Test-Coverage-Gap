# Step 5: relaxation and regrading, flagged tasks

Prompt `relax_v2` (sha 93fabd0add57). Agents: the top 30 Verified submissions.

## How failing patches failed (published per-test reports)

| group | tasks | failing patches | fail only new tests | break an old test |
|---|---|---|---|---|
| control | 113 | 812 | 51% (417/812, CI 48%-55%) | 46% (370/812, CI 42%-49%) |
| dev | 62 | 592 | 82% (486/592, CI 79%-85%) | 16% (94/592, CI 13%-19%) |
| flagged | 109 | 2434 | 90% (2186/2434, CI 89%-91%) | 9% (231/2434, CI 8%-11%) |

## Relaxations

- tasks with a patch that could flip: 108 of 117 in the group; run so far: 108
- outcome: {'valid': 93, 'declined': 15}; valid on the first attempt: 92
- failed checks across attempts: {'gold_fails': 1, 'base_passes': 1}
- lines changed per valid relaxation: median 11, max 127
- valid relaxations where a graded test now passes on the unfixed code: 26
- valid relaxations with no passing patch to run check 3 on: 25

## Regrading

- outcomes (one per submission and task): {'flip': 1331, 'still_fails': 514, 'patch_does_not_apply': 1}
- flip rate over regraded patches: 72% (1331/1845, CI 70%-74%)
- flip rate over every candidate patch, counting tasks without a valid relaxation as no flip: 61% (1331/2186, CI 59%-63%)
- tasks with at least one flip: 92% (86/93, CI 85%-96%)
- mean per-task share of patches that flip: 72%

| resolve band (top N) | flip rate |
|---|---|
| 0% | 73% (545/745, CI 70%-76%) |
| 1-50% | 72% (696/969, CI 69%-75%) |
| 51-89% | 69% (82/118, CI 61%-77%) |
| >=90% | 62% (8/13, CI 36%-82%) |

## Agents

Tasks gained per agent: min 33, median 45.0, max 60. Rank changed for 28 of 30; largest move 10 places.

| submission | resolved | flips | after | rank | rank after |
|---|---|---|---|---|---|
| 20251205_sonar-foundation-agent_claude-opus-4-5 | 396 | 41 | 437 | 1 | 3 |
| 20251215_livesweagent_claude-opus-4-5 | 396 | 38 | 434 | 1 | 4 |
| 20250928_trae_doubao_seed_code | 394 | 45 | 439 | 3 | 1 |
| 20251127_openhands_claude-opus-4-5 | 388 | 44 | 432 | 4 | 5 |
| 20251120_livesweagent_gemini-3-pro-preview | 387 | 43 | 430 | 5 | 7 |
| 20250804_epam-ai-run-claude-4-sonnet | 384 | 38 | 422 | 6 | 10 |
| 20250902_atlassian-rovo-dev | 384 | 54 | 438 | 6 | 2 |
| 20250819_ACoder | 382 | 37 | 419 | 8 | 14 |
| 20250901_warp | 378 | 54 | 432 | 9 | 5 |
| 20260217_mini-v2.0.0_claude-4-6-opus | 378 | 45 | 423 | 9 | 8 |
| 20250612_trae | 376 | 39 | 415 | 11 | 16 |
| 20250731_harness_ai | 374 | 40 | 414 | 12 | 18 |
| 20251103_sonar-foundation-agent_claude-sonnet-4-5 | 374 | 49 | 423 | 12 | 8 |
| 20250720_Lingxi-v1.5_claude-4-sonnet-20250514 | 373 | 37 | 410 | 14 | 21 |
| 20250915_JoyCode | 373 | 33 | 406 | 14 | 24 |
| 20250603_Refact_Agent_claude-4-sonnet | 372 | 41 | 413 | 16 | 19 |
| 20251124_mini-v1.16.0_claude-opus-4-5-20251101 | 372 | 48 | 420 | 16 | 12 |
| 20251118_mini-v1.15.0_gemini-3-pro-preview-20251118 | 371 | 49 | 420 | 18 | 12 |
| 20251103_SalesforceAIResearch_SAGE_OpenHands | 369 | 53 | 422 | 19 | 10 |
| 20250522_tools_claude-4-opus | 366 | 49 | 415 | 20 | 16 |
| 20251021_SalesforceAIResearch_SAGE_bash_only | 365 | 48 | 413 | 21 | 19 |
| 20250522_tools_claude-4-sonnet | 362 | 45 | 407 | 22 | 23 |
| 20250807_openhands_gpt5 | 359 | 50 | 409 | 23 | 22 |
| 20251211_mini-v1.17.2_gpt-5.2-2025-12-11-high | 359 | 60 | 419 | 23 | 14 |
| 20250710_bloop | 356 | 41 | 397 | 25 | 28 |
| 20250715_qodo_command | 356 | 46 | 402 | 25 | 25 |
| 20251014_Lingxi_kimi_k2 | 356 | 34 | 390 | 25 | 29 |
| 20250623_warp | 355 | 46 | 401 | 28 | 27 |
| 20250611_moatless_claude-4-sonnet-20250514 | 354 | 48 | 402 | 29 | 25 |
| 20250519_trae | 353 | 36 | 389 | 30 | 30 |
