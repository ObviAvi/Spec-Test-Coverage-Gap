# Spec-Test Coverage Gap (STCG)

Detects SWE-bench-style tasks whose tests check *how* the reference fix was written rather than *whether* the issue is fixed. A panel of LLM judges from different model families reads only the task specification and the test patch, then rates each task 1-4:

| Score | Label | Meaning |
|---|---|---|
| 1 | Directly specified | Test maps near-verbatim to the issue; any correct fix passes |
| 2 | Reasonably specified | Test adds only conventions a careful reader would infer |
| 3 | Mildly overspecified | Test pins one valid choice among several (exact literal, specific component) |
| 4 | Significantly overspecified | Test locks in the implementation: sentinel values, internal state, private APIs, a different code path |

Judges output the 1-4 score (kept in the results for severity), but everything is validated on the binary label: **fine** (1-2) vs **overspecified** (3-4). A task is **flagged** when both judges score it 3 or 4.

The pipeline has five steps:

1. **Judge** each task (`stcg judge`).
2. **Validate** the judge on tasks with existing human or agent evidence (`stcg build`, `stcg judge --split dev|test`).
3. **Prevalence** on all of SWE-bench Verified and public SWE-bench Pro (`stcg prevalence`).
4. **Ablations** on dev: identical rerun, reference fix shown, one-paragraph baseline (`stcg compare`).
5. **Relax and regrade**: an LLM loosens the flagged tests, Docker checks the loosened tests, and public agent patches that failed are rerun against them (`stcg relax`, `stcg relax-report`).

## Results

All numbers come from the files in `results/`.

| | Result | Report |
|---|---|---|
| Validation, test split (206 tasks) | recall 89% (100/112), false-flag rate 4% (4/94), Cohen's kappa 0.82 | `results/judge_v1/eval_test.md` |
| Validation, dev split (138 tasks) | recall 81% (61/75), false-flag rate 3% (2/63), kappa 0.78 | `results/judge_v1/eval_dev.md` |
| SWE-bench Verified | 117 of 500 flagged (23%); flagged tasks are resolved by 31% of the top 30 submissions, unflagged by 88% | `results/judge_v1/prevalence_verified.md` |
| SWE-bench Pro (public) | 258 of 731 flagged (35%); 201 of 656 (31%) outside the 75 known-overspecified validation tasks | `results/judge_v1/prevalence_pro.md` |
| Ablations (dev) | rerun changes 6 of 138 panel flags; reference fix: recall 87%; baseline prompt: recall 72% | `results/compare_dev.md` |
| Relax, flagged tasks | valid relaxation on 93 of 108 tasks; 61% (1,331/2,186) of failing candidate patches now pass | `results/relax_v2/report_flagged.md` |
| Relax, flagged, no judge findings | 49% (1,069/2,186) of candidates pass | `results/relax_free_v1/report_flagged.md` |
| Relax, control (neither judge flags), no findings | relaxer declines all 79 tasks; 0 of 417 candidates pass | `results/relax_free_v1/report_control.md` |
| Relax, control, forced to loosen one requirement | 29% (120/417) of candidates pass | `results/relax_forced_v1/report_control.md` |

## Setup

```bash
python -m venv .venv && .venv/Scripts/activate     # or source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                # add the two API keys
```

Model IDs live in `stcg/config.py` (`JUDGES`). The panel is `claude-opus-5-5` and `gpt-6.1-sol`, both at high reasoning effort; the relaxer is `claude-opus-5-5`.

Step 5 also needs Docker with the SWE-bench Verified task images (pulled per task, deleted after unless `--keep-images`). On Windows use Docker Desktop with WSL2. Allow plenty of disk.

## Workflow

```bash
# Steps 1-2: build the sets, develop on dev, then score test once
python -m stcg build                          # download sources, build Verified/Pro tasks + validation sets, dev/test split
python -m stcg judge --split dev --dry-run    # call count + token estimate
python -m stcg judge --split dev              # judge the dev set with both judges, then evaluate
python -m stcg judge --split test             # once, with the frozen prompt (judge_v1)

# Step 3: prevalence
python -m stcg judge --set verified           # all 500 Verified tasks (--set pro for the 731 Pro tasks)
python -m stcg prevalence --set verified      # flag rate by repo; for Verified also by difficulty and agent resolve rate

# Step 4: ablations on dev against judge_v1
python -m stcg judge --split dev --prompt judge_v1_rerun     # likewise judge_v1_gold, baseline_v1
python -m stcg compare --prompts judge_v1_rerun,judge_v1_gold,baseline_v1

# Step 5: relax and regrade (Docker)
python -m stcg relax --group flagged                              # relax_v2, with the judges' findings
python -m stcg relax --group flagged --prompt relax_free_v1       # no findings
python -m stcg relax --group control --prompt relax_free_v1       # control: neither judge flags, relaxer may decline
python -m stcg relax --group control --prompt relax_forced_v1     # control: forced to loosen one requirement
python -m stcg relax-report --group flagged --prompt relax_v2     # likewise for the other runs
```

Useful flags for `judge` / `evaluate`: `--source agent_consensus,openai_excluded`, `--ids django__django-16667`, `--judges claude,gpt61`, `--limit 5`, `--workers 8`. For `relax`: `--ids`, `--limit`, `--no-regrade`, `--task-workers`, `--run-workers`.

Caching and guards:
- Judge calls are cached per `(prompt version, judge, task)` in `results/<prompt>/raw/`; reruns only call the API for missing or errored entries.
- Editing a prompt file in place after it has been used is refused, so every result maps to exactly one prompt text.
- The test split refuses a second run unless `--allow-test-rerun` is passed. Each run is logged to `results/test_runs.json`; it was run once.
- Relaxer calls are cached in `results/<relax prompt>/raw/`, per-task outcomes in `results/<relax prompt>/tasks/`. Container runs are cached in `data/raw/relax_runs/` (gitignored).

## Step 1: the judge

- **Input** (`stcg/prompts.py`): the task specification (issue text; for SWE-bench Pro also the `requirements` and `interface` fields, since agents see those) and the test patch with the FAIL_TO_PASS tests listed and, for Python, tagged inline. No repo context; the gold patch is shown only by `judge_v1_gold` (an ablation).
- **Judges** (`stcg/llm.py`): Claude and GPT, same prompt, provider-native structured output. Each returns `reasoning`, `score`, `explanation` (what a valid alternative fix would get wrong, read later by the relaxer) and `overspecification_vector`.
- **Aggregation** (`stcg/judging.py`): final score = lower median of the judges' scores, so with 2 judges a task is flagged only when both flag it; tasks where judges differ by 2+ points are marked `uncertain` and reported separately.
- **Agreement** (`stcg/evaluate.py`): on the binary flag, Fleiss' kappa across all judges and pairwise Cohen's kappa + raw agreement.

The Claude client sends `fallbacks: "default"` (server-side refusal fallback). If a request is ever served by the fallback model, the raw record's `served_model` differs from `model`. None of the `judge_v1` records were.

## Step 2: validation sets

Built by `stcg build` into `data/validation/*.jsonl`:

| Set | Expected | Source | Count |
|---|---|---|---|
| `openai_excluded` | overspecified | SWE-bench tasks OpenAI dropped from Verified where **all 3** annotators rated `false_negative >= 2`, the issue was clear (`underspecified <= 1`) and no other major issue was flagged | 112 |
| `pro_narrow_original` | overspecified | the 75 tasks SWE-Bench Pro Verified repaired for "overly narrow tests", original SWE-bench Pro v1 versions | 75 |
| `agent_consensus` | fine | Verified tasks where all 3 OpenAI annotators rated `false_negative = 0`, resolved by >= 90% of the top 30 submissions in SWE-bench/experiments, whose resolving patches look different (mean pairwise Jaccard of changed lines <= 0.5) | 157 |

The split (`data/validation/split.json`) is by `instance_id`. 40% of the instances are sampled into dev stratified by set; everything else is test. Instances already in `split.json` keep their side when sets grow, so only new instances are sampled (delete the file to redraw).

Targets, fixed before the test run: recall >= 70% on overspecified and a false-flag rate <= 15% on fine, both reported with Wilson 95% intervals, per judge and for the panel, overall and per set.

## Step 5: relax and regrade

For each Verified task with at least one *candidate* (a top-30 patch that failed the task, whose published report shows failing evaluation (FAIL_TO_PASS) tests and no failing regression (PASS_TO_PASS) test):

1. The relaxer (`stcg/relax.py`) gets the spec, the test patch, the gold patch and, for `relax_v2`, both judges' explanations. It returns search-and-replace edits inside the test patch's hunks.
2. The relaxed tests run in the task's image through the SWE-bench harness (`stcg/dockerrun.py`). A relaxation is valid when at least one evaluation test still fails on the unfixed repo, the gold patch passes, and every patch that resolved the original task still resolves it. Up to 3 attempts, each seeing the previous failure.
3. Every candidate is rerun on the valid relaxed tests. A *flip* passes every evaluation and regression test under the relaxed tests and also fails the original tests in our environment.

Groups (`--group`) are set by how many panel judges flag the task: `flagged` (both), `control` (neither), `dev` (exactly one). Relaxer prompts were developed on `dev` tasks (`relax_v1`, then `relax_v2`), which are excluded from the reports; the 10 dev task records under `results/relax_free_v1/tasks/` and `results/relax_forced_v1/tasks/` are from that development.

## Known gaps

- There are no known-fine SWE-bench Pro tasks, so the false-flag rate is measured on Verified only. The repaired SWE-Bench Pro Verified versions are not a fine set: the repairs fixed only the reported narrow check, and on dev the judges flagged 11/30 of them for other overspecified checks still in the task. The 17 Pro tasks "reported broken but judged fine" are not in the SWE-Bench Pro Verified release.
- Step 5 covers Verified only; there are no public per-task agent patches for Pro in the pipeline.
- The relaxed-test checks bound a relaxation from one side only: nothing stops a relaxed test from being looser than the specification warrants. Only a sample of flips is inspected by hand: two to four flipped patches on each of the five control tasks with the most flips, plus the examples in the paper's appendix.
- The SPICE comparison is not implemented.

## Layout

```
stcg/            config.py, tasks.py (Task record), sources.py (downloads), prompts.py,
                 llm.py (provider clients), judging.py, metrics.py, evaluate.py,
                 validation.py (Step 2 sets + split), prevalence.py (Step 3 report),
                 compare.py (Step 4 ablation table), relax.py + dockerrun.py (Step 5),
                 relax_report.py (Step 5 report), cli.py
prompts/         judge_v1.txt (frozen), judge_v1_rerun.txt, judge_v1_gold.txt, baseline_v1.txt,
                 relax_v1.txt (development), relax_v2.txt, relax_free_v1.txt, relax_forced_v1.txt
data/            tasks/verified.jsonl, tasks/pro.jsonl, validation/*.jsonl + split.json,
                 raw/ (download and container-run cache, gitignored)
results/         <prompt>/raw/, eval_<split>.md/json, judgments_<split>.jsonl, prevalence_<set>.md/json,
                 compare_dev.md/json, <relax prompt>/tasks/ + report_<group>.md/json
tests/           pytest, no API calls or Docker
```

## Tests

```bash
python -m pytest tests
```
