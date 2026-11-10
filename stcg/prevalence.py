"""Step 3: how common overspecification is in SWE-bench Verified, and how the flag relates to agent results."""

import json
import statistics
from collections import Counter

from . import config, metrics, sources
from .evaluate import _fmt_rate
from .judging import aggregate, run_dir
from .tasks import load_tasks
from .validation import FINE, OVERSPECIFIED, load_validation

DIFFICULTIES = ["<15 min fix", "15 min - 1 hour", "1-4 hours", ">4 hours"]  # OpenAI's annotation labels
RESOLVE_BANDS = ["0%", "1-50%", "51-89%", ">=90%"]  # share of the top submissions that resolve a task


def resolve_band(rate: float) -> str:
    if rate == 0:
        return RESOLVE_BANDS[0]
    if rate <= 0.5:
        return RESOLVE_BANDS[1]
    return RESOLVE_BANDS[2] if rate < config.CONSENSUS_MIN_RESOLVE_RATE else RESOLVE_BANDS[3]


def corrected_prevalence(flag_rate: float, recall: float, false_flag_rate: float) -> float:
    """Rogan-Gladen estimate of the true rate given the judge's recall and false-flag rate."""
    return min(1.0, max(0.0, (flag_rate - false_flag_rate) / (recall - false_flag_rate)))


def _flag_rate(rows: list[dict]) -> dict:
    return metrics.rate(sum(r["flagged"] for r in rows), len(rows))


def _mean(rows: list[dict], key: str) -> float | None:
    return statistics.mean(r[key] for r in rows) if rows else None


def _groups(rows: list[dict], key: str, order: list[str] | None = None) -> dict:
    """Flag rate, score 3/4 counts and mean top-submission resolve rate (flagged vs not) per group."""
    names = order or [n for n, _ in Counter(r[key] for r in rows).most_common()]
    out = {}
    for name in names:
        g = [r for r in rows if r[key] == name]
        if g:
            out[name] = {"flag_rate": _flag_rate(g),
                         "score3": sum(r["final"] == 3 for r in g), "score4": sum(r["final"] == 4 for r in g),
                         "resolve_flagged": _mean([r for r in g if r["flagged"]], "resolve_top"),
                         "resolve_unflagged": _mean([r for r in g if not r["flagged"]], "resolve_top")}
    return out


def prevalence(judges: list[str], prompt_name: str) -> dict:
    rows = [r for r in (aggregate(t, judges, prompt_name) for t in load_tasks(config.TASKS / "verified.jsonl"))
            if r["complete"]]
    if not rows:
        raise SystemExit("No Verified judgments found. Run: python -m stcg judge --set verified")

    subs = sorted(sources.verified_submissions(), key=lambda s: len(s["resolved"]), reverse=True)
    top = subs[: config.CONSENSUS_TOP_SUBMISSIONS]
    ensembled, _ = sources.openai_annotations()
    for r in rows:
        iid = r["instance_id"]
        r["repo"] = iid.rsplit("-", 1)[0].replace("__", "/")
        r["resolve_top"] = sum(iid in s["resolved"] for s in top) / len(top)
        r["resolve_all"] = sum(iid in s["resolved"] for s in subs) / len(subs)
        r["difficulty"] = ensembled[iid]["difficulty"]
        r["resolve_band"] = resolve_band(r["resolve_top"])

    # the judge's own error rates, pooled over the dev and test validation splits
    val = [r for r in (aggregate(t, judges, prompt_name) for t in load_validation()) if r["complete"]]
    recall = _flag_rate([r for r in val if r["expected"] == OVERSPECIFIED])
    ffr = _flag_rate([r for r in val if r["expected"] == FINE])

    n, flag = len(rows), config.FLAG_THRESHOLD
    flagged, rest = [r for r in rows if r["flagged"]], [r for r in rows if not r["flagged"]]
    overall = _flag_rate(rows)
    rep = {
        "prompt": prompt_name, "judges": judges, "set": "verified",
        "flag_rate": overall,
        "scores": dict(sorted(Counter(r["final"] for r in rows).items())),
        "per_judge": {j: metrics.rate(sum(r["scores"][j] >= flag for r in rows), n) for j in judges},
        "any_judge": metrics.rate(sum(max(r["scores"].values()) >= flag for r in rows), n),
        "uncertain": metrics.rate(sum(r["uncertain"] for r in rows), n),
        "pairwise": metrics.pairwise_kappas({j: {r["task_id"]: r["scores"][j] >= flag for r in rows} for j in judges}),
        "validation": {"recall": recall, "false_flag_rate": ffr},
        "corrected_prevalence": (corrected_prevalence(overall["rate"], recall["rate"], ffr["rate"])
                                 if recall["n"] and ffr["n"] else None),
        "resolve": {"top_n": len(top), "submissions": len(subs),
                    "flagged_top": _mean(flagged, "resolve_top"), "unflagged_top": _mean(rest, "resolve_top"),
                    "flagged_all": _mean(flagged, "resolve_all"), "unflagged_all": _mean(rest, "resolve_all")},
        "by_resolve_band": _groups(rows, "resolve_band", RESOLVE_BANDS),
        "by_difficulty": _groups(rows, "difficulty", DIFFICULTIES),
        "by_repo": _groups(rows, "repo"),
        "tasks": [{k: r[k] for k in ("instance_id", "repo", "scores", "final", "flagged", "uncertain",
                                     "difficulty", "resolve_top", "resolve_all")} for r in rows],
    }

    out = run_dir(prompt_name)
    name = "verified" if judges == config.PANEL else f"verified__{'+'.join(judges)}"
    (out / f"prevalence_{name}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / f"prevalence_{name}.md").write_text(to_markdown(rep), encoding="utf-8")
    return rep


def _pct(x: float | None) -> str:
    return "-" if x is None else f"{x:.0%}"


def _group_table(title: str, label: str, groups: dict) -> list[str]:
    lines = [f"## {title}", "", f"| {label} | flagged | score 3 | score 4 | resolve rate, flagged | resolve rate, not flagged |",
             "|---|---|---|---|---|---|"]
    for name, g in groups.items():
        lines.append(f"| {name} | {_fmt_rate(g['flag_rate'])} | {g['score3']} | {g['score4']} "
                     f"| {_pct(g['resolve_flagged'])} | {_pct(g['resolve_unflagged'])} |")
    return lines + [""]


def to_markdown(rep: dict) -> str:
    res, val = rep["resolve"], rep["validation"]
    lines = [f"# STCG prevalence: `{rep['prompt']}` on SWE-bench Verified", "",
             f"- flagged (final score >= {config.FLAG_THRESHOLD}): {_fmt_rate(rep['flag_rate'])}",
             f"- final scores: {rep['scores']}",
             f"- flagged by any judge: {_fmt_rate(rep['any_judge'])}",
             f"- uncertain (spread >= {config.UNCERTAIN_SPREAD}): {_fmt_rate(rep['uncertain'])}", ""]
    lines += ["| judge alone | flagged |", "|---|---|"]
    lines += [f"| {j} | {_fmt_rate(e)} |" for j, e in rep["per_judge"].items()]
    lines += ["", "| pair | Cohen's kappa | agree |", "|---|---|---|"]
    lines += [f"| {p} | {e['kappa']:.3f} | {e['agree']:.0%} |" for p, e in rep["pairwise"].items()]
    lines += ["", "## Corrected prevalence", "",
              f"- judge recall on validation (dev + test): {_fmt_rate(val['recall'])}",
              f"- judge false-flag rate on validation (dev + test): {_fmt_rate(val['false_flag_rate'])}",
              f"- corrected prevalence, (flag rate - false-flag rate) / (recall - false-flag rate): "
              f"{'-' if rep['corrected_prevalence'] is None else format(rep['corrected_prevalence'], '.1%')}", ""]
    lines += ["## Flag and agent resolve rate", "",
              f"Resolve rate = share of submissions in SWE-bench/experiments that resolve the task "
              f"(top {res['top_n']} by resolve count, or all {res['submissions']}).", "",
              "| submissions | flagged tasks | not flagged |", "|---|---|---|",
              f"| top {res['top_n']} | {_pct(res['flagged_top'])} | {_pct(res['unflagged_top'])} |",
              f"| all {res['submissions']} | {_pct(res['flagged_all'])} | {_pct(res['unflagged_all'])} |", ""]
    note = f"Resolve-rate columns in the tables below use the top {res['top_n']} submissions."
    lines += [note, ""]
    lines += _group_table(f"By share of the top {res['top_n']} submissions that resolve the task", "resolved by",
                          rep["by_resolve_band"])
    lines += _group_table("By OpenAI difficulty rating", "difficulty", rep["by_difficulty"])
    lines += _group_table("By repository", "repo", rep["by_repo"])
    return "\n".join(lines)
