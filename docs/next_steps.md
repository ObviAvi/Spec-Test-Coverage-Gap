# Next steps

Written 2026-11-09. Goal: a paper.

## Where things stand

Steps 1-2 of the research plan (build the judge, validate it) are done. The prompt `judge_v1` is frozen.

| | Dev | Test | Target |
|---|---|---|---|
| Recall on overspecified | 81% (61/75, CI 71-89%) | 89% (100/112, CI 82-94%) | >= 70% |
| False flags on fine | 3% (2/63, CI 1-11%) | 4% (4/94, CI 2-10%) | <= 15% |
| Cohen's kappa | 0.78 | 0.82 | |

- Panel: `claude-opus-5-5` and `gpt-6.1-sol`, flagged only when both score 3 or 4.
- Test recall by set: `openai_excluded` 97% (65/67), `pro_narrow_original` 78% (35/45).
- Full reports: `results/judge_v1/eval_dev.md`, `results/judge_v1/eval_test.md`.

Limitation to state in the paper: there are no fine SWE-bench Pro tasks, so the false-flag rate is measured on Verified only and is unknown for Pro.

## Steps

### 1. Commit

Keep the pipeline, data, prompts and results in git.

### 2. Step 3 on Verified: how common is overspecification (RQ2)

Run the frozen judge on all 500 Verified tasks:

```bash
python -m stcg judge --set verified
```

The 157 fine tasks are already cached, so this is about 343 new tasks, roughly $22.

Report:
- flag rate overall, by repo, and by score 3 vs 4
- prevalence corrected for the judge's recall and false-flag rate
- whether flagged tasks are solved less often by public agents, controlling for OpenAI's difficulty rating
- flag rate among tasks no top agent solves (likely headline number)

### 3. Step 3 on Pro

The build only writes `data/tasks/verified.jsonl`. Add a Pro task file, then judge all 731 tasks. 75 are cached; the remaining 656 have longer prompts, so expect $45-55.

### 4. Ablations and a baseline on dev

About $10 each:
- gold-patch prompt (`judge_v1_gold`)
- rerun of `judge_v1` into a separate cache to measure run-to-run noise
- a plain one-paragraph prompt as a baseline

### 5. Executable counterexamples

For 20-30 flagged Verified tasks, have an LLM write the alternative fix the judge describes, then run it in the SWE-bench docker harness. A counterexample is confirmed when the fix passes the existing tests and fails the graded ones.

This is the part no other auditor has, and it removes the dependence on judge-only labels.

### 6. Step 4: relax tests and regrade public submissions (RQ3)

Uses the same harness as step 5.
- relax the overspecified part of each flagged test, using the judge's explanation
- each relaxed test must fail on the base commit, pass the gold patch, and accept at least one alternative the original rejected
- regrade existing patches from public submissions, no agent reruns
- run the same procedure on about 20 fine placebo tasks
- report score change per agent and ranking change

### 7. Write

The method and validation sections can be written now. The draft has no results section yet and needs the new numbers.

## Open decisions

- Steps 2-4 only need API calls. Steps 5-6 need Docker with the SWE-bench images (WSL2 on Windows, plus a lot of disk).
- Whether the paper includes step 6 or stops at step 5 depends on that setup and the deadline.
- The prompt-clarification experiment and the contamination study from the draft are future work.
