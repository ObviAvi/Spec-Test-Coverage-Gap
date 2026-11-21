# Step 5: relaxation and regrading, control tasks

Prompt `relax_free_v1` (sha 941f9b813bf6). Agents: the top 30 Verified submissions.

## How failing patches failed (published per-test reports)

| group | tasks | failing patches | fail only new tests | break an old test |
|---|---|---|---|---|
| control | 113 | 812 | 51% (417/812, CI 48%-55%) | 46% (370/812, CI 42%-49%) |
| dev | 62 | 592 | 82% (486/592, CI 79%-85%) | 16% (94/592, CI 13%-19%) |
| flagged | 109 | 2434 | 90% (2186/2434, CI 89%-91%) | 9% (231/2434, CI 8%-11%) |

## Relaxations

- tasks with a patch that could flip: 79 of 296 in the group; run so far: 79
- outcome: {'declined': 79}; valid on the first attempt: 0
- failed checks across attempts: {}
- lines changed per valid relaxation: median None, max None
- valid relaxations where a graded test now passes on the unfixed code: 0
- valid relaxations with no passing patch to run check 3 on: 0

## Regrading

- outcomes (one per submission and task): {}
- flip rate over regraded patches: -
- flip rate over every candidate patch, counting tasks without a valid relaxation as no flip: 0% (0/417, CI 0%-1%)
- tasks with at least one flip: -


| resolve band (top N) | flip rate |
|---|---|
| 0% | - |
| 1-50% | - |
| 51-89% | - |
| >=90% | - |

## Agents

Tasks gained per agent: min 0, median 0.0, max 0. Rank changed for 0 of 30; largest move 0 places.

| submission | resolved | flips | after | rank | rank after |
|---|---|---|---|---|---|
| 20251205_sonar-foundation-agent_claude-opus-4-5 | 396 | 0 | 396 | 1 | 1 |
| 20251215_livesweagent_claude-opus-4-5 | 396 | 0 | 396 | 1 | 1 |
| 20250928_trae_doubao_seed_code | 394 | 0 | 394 | 3 | 3 |
| 20251127_openhands_claude-opus-4-5 | 388 | 0 | 388 | 4 | 4 |
| 20251120_livesweagent_gemini-3-pro-preview | 387 | 0 | 387 | 5 | 5 |
| 20250804_epam-ai-run-claude-4-sonnet | 384 | 0 | 384 | 6 | 6 |
| 20250902_atlassian-rovo-dev | 384 | 0 | 384 | 6 | 6 |
| 20250819_ACoder | 382 | 0 | 382 | 8 | 8 |
| 20250901_warp | 378 | 0 | 378 | 9 | 9 |
| 20260217_mini-v2.0.0_claude-4-6-opus | 378 | 0 | 378 | 9 | 9 |
| 20250612_trae | 376 | 0 | 376 | 11 | 11 |
| 20250731_harness_ai | 374 | 0 | 374 | 12 | 12 |
| 20251103_sonar-foundation-agent_claude-sonnet-4-5 | 374 | 0 | 374 | 12 | 12 |
| 20250720_Lingxi-v1.5_claude-4-sonnet-20250514 | 373 | 0 | 373 | 14 | 14 |
| 20250915_JoyCode | 373 | 0 | 373 | 14 | 14 |
| 20250603_Refact_Agent_claude-4-sonnet | 372 | 0 | 372 | 16 | 16 |
| 20251124_mini-v1.16.0_claude-opus-4-5-20251101 | 372 | 0 | 372 | 16 | 16 |
| 20251118_mini-v1.15.0_gemini-3-pro-preview-20251118 | 371 | 0 | 371 | 18 | 18 |
| 20251103_SalesforceAIResearch_SAGE_OpenHands | 369 | 0 | 369 | 19 | 19 |
| 20250522_tools_claude-4-opus | 366 | 0 | 366 | 20 | 20 |
| 20251021_SalesforceAIResearch_SAGE_bash_only | 365 | 0 | 365 | 21 | 21 |
| 20250522_tools_claude-4-sonnet | 362 | 0 | 362 | 22 | 22 |
| 20250807_openhands_gpt5 | 359 | 0 | 359 | 23 | 23 |
| 20251211_mini-v1.17.2_gpt-5.2-2025-12-11-high | 359 | 0 | 359 | 23 | 23 |
| 20250710_bloop | 356 | 0 | 356 | 25 | 25 |
| 20250715_qodo_command | 356 | 0 | 356 | 25 | 25 |
| 20251014_Lingxi_kimi_k2 | 356 | 0 | 356 | 25 | 25 |
| 20250623_warp | 355 | 0 | 355 | 28 | 28 |
| 20250611_moatless_claude-4-sonnet-20250514 | 354 | 0 | 354 | 29 | 29 |
| 20250519_trae | 353 | 0 | 353 | 30 | 30 |
