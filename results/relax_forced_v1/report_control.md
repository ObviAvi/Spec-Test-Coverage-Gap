# Step 5: relaxation and regrading, control tasks

Prompt `relax_forced_v1` (sha 801b6179a9b7). Agents: the top 30 Verified submissions.

## How failing patches failed (published per-test reports)

| group | tasks | failing patches | fail only new tests | break an old test |
|---|---|---|---|---|
| control | 113 | 812 | 51% (417/812, CI 48%-55%) | 46% (370/812, CI 42%-49%) |
| dev | 62 | 592 | 82% (486/592, CI 79%-85%) | 16% (94/592, CI 13%-19%) |
| flagged | 109 | 2434 | 90% (2186/2434, CI 89%-91%) | 9% (231/2434, CI 8%-11%) |

## Relaxations

- tasks with a patch that could flip: 79 of 296 in the group; run so far: 79
- outcome: {'valid': 76, 'invalid': 2, 'declined': 1}; valid on the first attempt: 75
- failed checks across attempts: {'edit_error': 6, 'passer_fails': 1}
- lines changed per valid relaxation: median 5.0, max 72
- valid relaxations where a graded test now passes on the unfixed code: 10
- valid relaxations with no passing patch to run check 3 on: 1

## Regrading

- outcomes (one per submission and task): {'still_fails': 257, 'flip': 120, 'patch_does_not_apply': 6, 'passes_original_here': 21}
- flip rate over regraded patches: 32% (120/377, CI 27%-37%)
- flip rate over every candidate patch, counting tasks without a valid relaxation as no flip: 29% (120/417, CI 25%-33%)
- tasks with at least one flip: 31% (19/61, CI 21%-44%)
- mean per-task share of patches that flip: 27%

| resolve band (top N) | flip rate |
|---|---|
| 0% | 0% (0/30, CI 0%-11%) |
| 1-50% | 42% (75/178, CI 35%-49%) |
| 51-89% | 26% (32/125, CI 19%-34%) |
| >=90% | 30% (13/44, CI 18%-44%) |

## Agents

Tasks gained per agent: min 2, median 4.0, max 6. Rank changed for 11 of 30; largest move 2 places.

| submission | resolved | flips | after | rank | rank after |
|---|---|---|---|---|---|
| 20251205_sonar-foundation-agent_claude-opus-4-5 | 396 | 4 | 400 | 1 | 2 |
| 20251215_livesweagent_claude-opus-4-5 | 396 | 5 | 401 | 1 | 1 |
| 20250928_trae_doubao_seed_code | 394 | 2 | 396 | 3 | 3 |
| 20251127_openhands_claude-opus-4-5 | 388 | 5 | 393 | 4 | 4 |
| 20251120_livesweagent_gemini-3-pro-preview | 387 | 2 | 389 | 5 | 5 |
| 20250804_epam-ai-run-claude-4-sonnet | 384 | 3 | 387 | 6 | 7 |
| 20250902_atlassian-rovo-dev | 384 | 4 | 388 | 6 | 6 |
| 20250819_ACoder | 382 | 2 | 384 | 8 | 8 |
| 20250901_warp | 378 | 4 | 382 | 9 | 10 |
| 20260217_mini-v2.0.0_claude-4-6-opus | 378 | 5 | 383 | 9 | 9 |
| 20250612_trae | 376 | 4 | 380 | 11 | 11 |
| 20250731_harness_ai | 374 | 4 | 378 | 12 | 12 |
| 20251103_sonar-foundation-agent_claude-sonnet-4-5 | 374 | 4 | 378 | 12 | 12 |
| 20250720_Lingxi-v1.5_claude-4-sonnet-20250514 | 373 | 3 | 376 | 14 | 15 |
| 20250915_JoyCode | 373 | 3 | 376 | 14 | 15 |
| 20250603_Refact_Agent_claude-4-sonnet | 372 | 3 | 375 | 16 | 17 |
| 20251124_mini-v1.16.0_claude-opus-4-5-20251101 | 372 | 5 | 377 | 16 | 14 |
| 20251118_mini-v1.15.0_gemini-3-pro-preview-20251118 | 371 | 3 | 374 | 18 | 18 |
| 20251103_SalesforceAIResearch_SAGE_OpenHands | 369 | 4 | 373 | 19 | 19 |
| 20250522_tools_claude-4-opus | 366 | 4 | 370 | 20 | 20 |
| 20251021_SalesforceAIResearch_SAGE_bash_only | 365 | 3 | 368 | 21 | 21 |
| 20250522_tools_claude-4-sonnet | 362 | 5 | 367 | 22 | 22 |
| 20250807_openhands_gpt5 | 359 | 6 | 365 | 23 | 23 |
| 20251211_mini-v1.17.2_gpt-5.2-2025-12-11-high | 359 | 3 | 362 | 23 | 24 |
| 20250710_bloop | 356 | 4 | 360 | 25 | 27 |
| 20250715_qodo_command | 356 | 5 | 361 | 25 | 25 |
| 20251014_Lingxi_kimi_k2 | 356 | 5 | 361 | 25 | 25 |
| 20250623_warp | 355 | 5 | 360 | 28 | 27 |
| 20250611_moatless_claude-4-sonnet-20250514 | 354 | 6 | 360 | 29 | 27 |
| 20250519_trae | 353 | 5 | 358 | 30 | 30 |
