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

Done. The panel flags 117 of 500 tasks (23%, CI 20-27%); 85% of the tasks no top-30 agent resolves are flagged, against 5% of the tasks at least 90% resolve. Report: `results/judge_v1/prevalence_verified.md` (`python -m stcg prevalence`).

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

Done. The panel flags 258 of 731 public Pro tasks (35%, CI 32-39%); 201 of 656 (31%) outside the 75 known-overspecified validation tasks. Kappa 0.62. Report: `results/judge_v1/prevalence_pro.md` (`python -m stcg prevalence --set pro`).

Caveat: the false-flag rate is measured on Verified only, so the corrected Pro prevalence (38-44%) assumes it carries over. There are no public per-task agent results for Pro in the pipeline, so no resolve-rate table.

### 4. Ablations and a baseline on dev

About $10 each:
- gold-patch prompt (`judge_v1_gold`)
- rerun of `judge_v1` into a separate cache to measure run-to-run noise
- a plain one-paragraph prompt as a baseline

### 5. Relax, validate, regrade (RQ3)

Merges the old "executable counterexamples" and "relax tests" steps. Needs the SWE-bench docker harness.

For each flagged Verified task:
1. An LLM relaxes the overspecified part of the test, using the judge's explanation and blamed lines.
2. The relaxed test is validated with the checks below.
3. Existing patches from public submissions are regraded on it. No agent reruns.

A patch that failed the original test, passes the relaxed one, and passes every pre-existing test is an executable counterexample: a working fix the benchmark marked wrong. These come from real agents, so nothing has to be generated.

Checks on each relaxed test (pass/fail, all deterministic):
1. It fails on the base commit with the failure the issue describes.
2. It passes with the gold patch.
3. Every agent patch that passed the original test still passes.

Check on the procedure as a whole:
4. Placebo. Run the same relaxation procedure on unflagged tasks. Almost nothing should flip. If patches flip there as often as on flagged tasks, the relaxer is weakening tests in general and the gains are not evidence of overspecification. The placebo flip rate is the baseline to subtract.
   - Placebo tasks need failing patches to be able to flip, so pick unflagged tasks matched on resolve rate (the fine validation set is solved by nearly everyone and has almost none).

Reported, not enforced:
- How much of the test each relaxation changed, and whether it stayed within the lines the judge blamed. Some fixes need a larger rewrite (e.g. a test that calls a private helper has to be rewritten to go through the public entry point), so this is not a pass/fail gate. Report results separately for small edits and rewrites.

Outcomes to report:
- tasks with at least one flipped patch (confirmed), tasks with none (inconclusive, not a negative), tasks where no relaxed test passes the checks (not relaxable)
- score change per agent and ranking change
- flip rate on flagged tasks against the placebo flip rate

Fallback: for flagged tasks where no agent patch flips, have an LLM write the alternative fix the judge describes and run it the same way.

### 6. Write

The method and validation sections can be written now. The draft has no results section yet and needs the new numbers.

## Open decisions

- Steps 2-4 only need API calls. Step 5 needs Docker with the SWE-bench images (WSL2 on Windows, plus a lot of disk).
- With the line restriction dropped, the placebo is the only guard against a relaxed test that is too weak, and it works on average, not per task. A per-task guard would be: a few deliberately wrong variants of the gold patch must still fail the relaxed test. Decide whether to add it, at least for rewrites.
- Possible shortcut before any Docker work: if the public submissions include per-test pass/fail reports, check whether failing agents fail specifically on the tests the judge blamed. Not yet verified that those files exist.
- The prompt-clarification experiment and the contamination study from the draft are future work.
