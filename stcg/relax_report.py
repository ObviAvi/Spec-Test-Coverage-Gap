"""Step 5 report: how failing patches failed (published reports), how the relaxations fared, and what regrading changes."""

import json
import statistics
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from . import config, judging
from .evaluate import _fmt_rate
from .metrics import rate
from .prevalence import RESOLVE_BANDS, resolve_band
from .prompts import template_sha
from .relax import _ranked_submissions, _task_path, candidates, classify_failure, published_report, task_groups


def failure_table(groups: dict[str, str], top: list[dict]) -> dict:
    """Per group, how each top-N patch that did not resolve its task failed, from the published per-test reports."""
    pairs = [(iid, s) for iid in groups for s in top if iid not in s["resolved"]]
    with ThreadPoolExecutor(max_workers=16) as pool:
        kinds = list(pool.map(lambda p: classify_failure(published_report(p[1], p[0])), pairs))
    out = {}
    for group in sorted(set(groups.values())):
        got = [(iid, k) for (iid, _), k in zip(pairs, kinds) if groups[iid] == group]
        tasks = {iid for iid, _ in got}
        counts = Counter(k for _, k in got)
        out[group] = {"tasks_with_failing_patch": len(tasks), "failing_patches": len(got), "kinds": dict(counts),
                      "new_tests_only": rate(counts["new_tests_only"], len(got)),
                      "breaks_old_tests": rate(counts["breaks_old_tests"], len(got)),
                      "tasks_with_new_tests_only": len({iid for iid, k in got if k == "new_tests_only"})}
    return out


def _rank(scores: dict[str, int]) -> dict[str, int]:
    """Competition ranking: equal scores share the better rank."""
    ordered = sorted(scores.values(), reverse=True)
    return {name: ordered.index(s) + 1 for name, s in scores.items()}


def report(group: str, prompt_name: str, judge_prompt: str) -> dict:
    subs = _ranked_submissions()
    top = subs[: config.CONSENSUS_TOP_SUBMISSIONS]
    groups = task_groups(judge_prompt)
    ids = sorted(i for i, g in groups.items() if g == group)
    with ThreadPoolExecutor(max_workers=16) as pool:
        cands = dict(zip(ids, pool.map(lambda i: len(candidates(i, subs)), ids)))
    selected = [i for i in ids if cands[i]]
    recs = [json.loads(_task_path(prompt_name, i).read_text(encoding="utf-8")) for i in selected
            if _task_path(prompt_name, i).exists()]
    valid = [r for r in recs if r["status"] == "valid"]

    outcomes = Counter()
    flips_by_sub, per_task, by_band = Counter(), [], {b: Counter() for b in RESOLVE_BANDS}
    task_flips = {}
    for r in valid:
        iid = r["instance_id"]
        band = resolve_band(sum(iid in s["resolved"] for s in top) / len(top))
        task = Counter()
        for x in r.get("regrade", []):
            for name in x["submissions"]:
                task[x["outcome"]] += 1
                if x["outcome"] == "flip":
                    flips_by_sub[name] += 1
        outcomes += task
        task_flips[iid] = task["flip"]
        by_band[band] += task
        graded = task["flip"] + task["still_fails"]
        if graded:
            per_task.append({"instance_id": iid, "flip": task["flip"], "graded": graded, "share": task["flip"] / graded,
                             "lines_changed": r["lines_changed"], "tests_passing_unfixed": len(r["neutralized"]),
                             "passers_checked": r["attempts"][-1].get("passers", 0)})
    graded = outcomes["flip"] + outcomes["still_fails"]

    before = {s["name"]: len(s["resolved"]) for s in top}
    after = {name: n + flips_by_sub[name] for name, n in before.items()}
    rank_before, rank_after = _rank(before), _rank(after)
    agents = [{"submission": name, "resolved_before": before[name], "flips": flips_by_sub[name],
               "resolved_after": after[name], "rank_before": rank_before[name], "rank_after": rank_after[name]}
              for name in sorted(before, key=lambda n: (rank_before[n], n))]
    changed = sorted((r["lines_changed"] for r in valid))
    rep = {
        "group": group, "prompt": prompt_name, "prompt_sha": template_sha(prompt_name),
        "top_n": len(top), "tasks_in_group": len(ids), "tasks_selected": len(selected), "tasks_run": len(recs),
        "candidate_patches": sum(cands.values()),
        "status": dict(Counter(r["status"] for r in recs)),
        "valid_first_attempt": sum(len(r["attempts"]) == 1 for r in valid),
        "failed_checks": dict(Counter(a["check"] for r in recs for a in r["attempts"] if a.get("check") not in (None, "ok"))),
        "lines_changed": {"median": statistics.median(changed) if changed else None, "max": changed[-1] if changed else None},
        "valid_with_test_passing_unfixed": sum(bool(r["neutralized"]) for r in valid),
        "valid_without_passing_patch": sum(not r["attempts"][-1].get("passers") for r in valid),
        "outcomes": dict(outcomes),
        "flip_rate_regraded": rate(outcomes["flip"], graded),
        "flip_rate_all_candidates": rate(outcomes["flip"], sum(cands.values())),
        "tasks_with_flip": rate(sum(t["flip"] > 0 for t in per_task), len(per_task)),
        "mean_task_flip_share": statistics.mean(t["share"] for t in per_task) if per_task else None,
        "by_resolve_band": {b: rate(c["flip"], c["flip"] + c["still_fails"]) for b, c in by_band.items()},
        "agents": agents,
        "agent_gain": {"min": min(a["flips"] for a in agents), "median": statistics.median(a["flips"] for a in agents),
                       "max": max(a["flips"] for a in agents),
                       "rank_changed": sum(a["rank_before"] != a["rank_after"] for a in agents),
                       "max_rank_change": max(abs(a["rank_before"] - a["rank_after"]) for a in agents)},
        "failure_table": failure_table(groups, top),
        "tasks": per_task,
        # every selected task, for task-level resampling; a task without a valid relaxation has no flips
        "all_tasks": [{"instance_id": i, "candidates": cands[i], "flips": task_flips.get(i, 0)} for i in selected],
    }
    out = judging.run_dir(prompt_name)
    (out / f"report_{group}.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out / f"report_{group}.md").write_text(_markdown(rep), encoding="utf-8")
    return rep


def _markdown(rep: dict) -> str:
    lines = [f"# Step 5: relaxation and regrading, {rep['group']} tasks", "",
             f"Prompt `{rep['prompt']}` (sha {rep['prompt_sha']}). Agents: the top {rep['top_n']} Verified submissions.", "",
             "## How failing patches failed (published per-test reports)", "",
             "| group | tasks | failing patches | fail only new tests | break an old test |", "|---|---|---|---|---|"]
    for g, e in rep["failure_table"].items():
        lines.append(f"| {g} | {e['tasks_with_failing_patch']} | {e['failing_patches']} | "
                     f"{_fmt_rate(e['new_tests_only'])} | {_fmt_rate(e['breaks_old_tests'])} |")
    lines += ["", "## Relaxations", "",
              f"- tasks with a patch that could flip: {rep['tasks_selected']} of {rep['tasks_in_group']} in the group; "
              f"run so far: {rep['tasks_run']}",
              f"- outcome: {rep['status']}; valid on the first attempt: {rep['valid_first_attempt']}",
              f"- failed checks across attempts: {rep['failed_checks']}",
              f"- lines changed per valid relaxation: median {rep['lines_changed']['median']}, max {rep['lines_changed']['max']}",
              f"- valid relaxations where a graded test now passes on the unfixed code: {rep['valid_with_test_passing_unfixed']}",
              f"- valid relaxations with no passing patch to run check 3 on: {rep['valid_without_passing_patch']}", "",
              "## Regrading", "",
              f"- outcomes (one per submission and task): {rep['outcomes']}",
              f"- flip rate over regraded patches: {_fmt_rate(rep['flip_rate_regraded'])}",
              f"- flip rate over every candidate patch, counting tasks without a valid relaxation as no flip: "
              f"{_fmt_rate(rep['flip_rate_all_candidates'])}",
              f"- tasks with at least one flip: {_fmt_rate(rep['tasks_with_flip'])}",
              f"- mean per-task share of patches that flip: {rep['mean_task_flip_share']:.0%}" if rep["mean_task_flip_share"] is not None else "",
              "", "| resolve band (top N) | flip rate |", "|---|---|"]
    lines += [f"| {b} | {_fmt_rate(e)} |" for b, e in rep["by_resolve_band"].items()]
    g = rep["agent_gain"]
    lines += ["", "## Agents", "",
              f"Tasks gained per agent: min {g['min']}, median {g['median']}, max {g['max']}. "
              f"Rank changed for {g['rank_changed']} of {len(rep['agents'])}; largest move {g['max_rank_change']} places.", "",
              "| submission | resolved | flips | after | rank | rank after |", "|---|---|---|---|---|---|"]
    lines += [f"| {a['submission']} | {a['resolved_before']} | {a['flips']} | {a['resolved_after']} | "
              f"{a['rank_before']} | {a['rank_after']} |" for a in rep["agents"]]
    return "\n".join(lines) + "\n"
