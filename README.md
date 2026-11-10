# Spec-Test Coverage Gap (STCG)

Detects SWE-bench-style tasks whose tests check *how* the reference fix was written rather than *whether* the issue is fixed. A panel of LLM judges from different model families reads only the task specification and the test patch, then rates each task 1-4:

| Score | Label | Meaning |
|---|---|---|
| 1 | Directly specified | Test maps near-verbatim to the issue; any correct fix passes |
| 2 | Reasonably specified | Test adds only conventions a careful reader would infer |
| 3 | Mildly overspecified | Test pins one valid choice among several (exact literal, specific component) |
| 4 | Significantly overspecified | Test locks in the implementation: sentinel values, internal state, private APIs, a different code path |

Judges output the 1-4 score (kept in the results for specificity), but everything is validated on the binary label: **fine** (1-2) vs **overspecified** (3-4). A task is **flagged** when its final score is 3 or 4. The research plan is in `docs/` (Steps 1-2 are implemented here).

## Setup

```bash
python -m venv .venv && .venv/Scripts/activate     # or source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                # add the two API keys
```

Model IDs live in `stcg/config.py` (`JUDGES`). Check them before a real run; the defaults are `claude-opus-5-5` and `gpt-6.1-sol`.

## Workflow

```bash
python -m stcg build                     # 1. download sources, build Verified tasks + validation sets, dev/test split
python -m stcg judge --split dev --dry-run   # 2. see call count + token estimate
python -m stcg judge --split dev         # 3. judge the dev set with both judges, then evaluate
# 4. read results/judge_v1/eval_dev.md, copy prompts/judge_v1.txt -> judge_v2.txt, edit, rerun with --prompt judge_v2
python -m stcg judge --split test --prompt judge_vN   # 5. once, with the frozen prompt
python -m stcg judge --set verified --prompt judge_vN # Step 3: all 500 Verified tasks (--set pro for the 731 Pro tasks)
python -m stcg prevalence --set verified               # Step 3 report: flag rate by repo; for Verified also by difficulty and agent resolve rate
```

Useful flags for `judge` / `evaluate`: `--source agent_consensus,openai_excluded`, `--ids django__django-16667`, `--judges claude,gpt61`, `--limit 5`, `--workers 8`.

Judge calls are cached per `(prompt version, judge, task)` in `results/<prompt>/raw/`; reruns only call the API for missing or errored entries. Editing a prompt file in place after it has been used is refused, so every result maps to exactly one prompt text. The test split refuses a second run unless `--allow-test-rerun` is passed (each run is logged to `results/test_runs.json`).

## Step 1: the judge

- **Input** (`stcg/prompts.py`): the task specification (issue text; for SWE-bench Pro also the `requirements` and `interface` fields, since agents see those) and the test patch with the FAIL_TO_PASS tests listed and, for Python, tagged inline. No repo context; the gold patch is shown only by `judge_v1_gold` (an ablation, not yet run).
- **Judges** (`stcg/llm.py`): Claude and GPT, same prompt, provider-native structured output. Each returns `reasoning`, `score`, `explanation` (what a valid alternative fix would get wrong, for the later repair step) and `overspecification_vector`.
- **Aggregation** (`stcg/judging.py`): final score = lower median of the judges' scores, so with 2 judges a task is flagged only when both flag it; tasks where judges differ by 2+ points are marked `uncertain` and reported separately.
- **Agreement** (`stcg/evaluate.py`): on the binary flag, Fleiss' kappa across all judges and pairwise Cohen's kappa + raw agreement.

The Claude client sends `fallbacks: "default"` (server-side refusal fallback). If a request is ever served by the fallback model, the raw record's `served_model` differs from `model`; filter those out if you need a single-model label.

## Step 2: validation sets

Built by `stcg build` into `data/validation/*.jsonl`:

| Set | Expected | Source | Count |
|---|---|---|---|
| `openai_excluded` | overspecified | SWE-bench tasks OpenAI dropped from Verified where **all 3** annotators rated `false_negative >= 2`, the issue was clear (`underspecified <= 1`) and no other major issue was flagged | see build output |
| `pro_narrow_original` | overspecified | the 75 tasks SWE-Bench Pro Verified repaired for "overly narrow tests", original SWE-bench Pro v1 versions | 75 |
| `agent_consensus` | fine | Verified tasks where all 3 OpenAI annotators rated `false_negative = 0`, resolved by >= 90% of the top 30 submissions in SWE-bench/experiments, whose resolving patches look different (mean pairwise Jaccard of changed lines <= 0.5) | 157 |

The split (`data/validation/split.json`) is by `instance_id`. 40% of the instances are sampled into dev stratified by set; everything else is test. Instances already in `split.json` keep their side when sets grow, so only new instances are sampled (delete the file to redraw).

The dev targets (Step 2.4) are recall >= 70% on overspecified and a false-flag rate <= 15% on fine, both reported with Wilson 95% intervals, per judge and for the ensemble, overall and per set.

### Known gaps

- The repaired SWE-Bench Pro Verified versions (2.2b) were dropped as a fine set. The repairs fixed only the reported narrow check, and on dev the judges flagged 11/30 of them for other overspecified checks that are still in the task (i.e. tests calling unexported helpers or omitting a required argument the interface lists).
- The 17 Pro tasks "reported broken but judged fine" are not in the SWE-Bench Pro Verified release (only the 102 repaired ids are listed), so they cannot stand in as a fine Pro set either.
- The SPICE comparison (Step 2.5) is not implemented.
- 2.1c (injected checks) and 2.2c (clarified issues) were dropped; all sets come from existing human or agent evidence.

## Layout

```
stcg/            config.py, tasks.py (Task record), sources.py (downloads), prompts.py,
                 llm.py (provider clients), judging.py, metrics.py, evaluate.py,
                 validation.py (Step 2 sets + split), prevalence.py (Step 3 report), cli.py
prompts/         judge_v*.txt
data/            tasks/verified.jsonl, tasks/pro.jsonl, validation/*.jsonl, raw/ (download cache, gitignored)
results/         <prompt>/raw/<judge>/*.json, eval_<split>.md/json, judgments_<split>.jsonl, prevalence_<set>.md/json
tests/           pytest, no API calls
docs/            next_steps.md
```

## Tests

```bash
python -m pytest tests
```
