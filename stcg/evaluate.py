"""Step 1.4 + Step 2.4/2.5: inter-judge agreement and recall / false-flag rate, all on the binary flag (score >= 3)."""

import json
from collections import defaultdict

from . import config, metrics
from .judging import aggregate, run_dir
from .tasks import Task
from .validation import FINE, OVERSPECIFIED


def _detection(rows: list[dict], score_of) -> dict:
    """Recall on known-overspecified and false-flag rate on known-fine, overall and per source."""
    out = {}
    groups = {"all": rows, **{f"source:{s}": [r for r in rows if r["source"] == s]
                              for s in sorted({r["source"] for r in rows})}}
    for name, group in groups.items():
        pos = [score_of(r) for r in group if r["expected"] == OVERSPECIFIED and score_of(r) is not None]
        neg = [score_of(r) for r in group if r["expected"] == FINE and score_of(r) is not None]
        entry = {}
        if pos:
            entry["recall"] = metrics.rate(sum(s >= config.FLAG_THRESHOLD for s in pos), len(pos))
        if neg:
            entry["false_flag_rate"] = metrics.rate(sum(s >= config.FLAG_THRESHOLD for s in neg), len(neg))
        out[name] = entry
    return out


def evaluate(tasks: list[Task], judges: list[str], prompt_name: str, split: str) -> dict:
    rows = [aggregate(t, judges, prompt_name) for t in tasks]
    judged = [r for r in rows if r["final"] is not None]

    by_judge: dict[str, dict[str, bool]] = defaultdict(dict)
    for r in judged:
        for j, s in r["scores"].items():
            by_judge[j][r["task_id"]] = s >= config.FLAG_THRESHOLD
    complete = [r for r in judged if r["complete"]]

    report = {
        "prompt": prompt_name, "split": split, "judges": judges,
        "coverage": {"tasks": len(rows), "judged": len(judged), "all_judges": len(complete),
                     "errors": {j: sum(j in r["errors"] for r in rows) for j in judges}},
        "agreement": {
            "fleiss_kappa": metrics.fleiss_kappa([[r["scores"][j] >= config.FLAG_THRESHOLD for j in judges]
                                                  for r in complete]),
            "pairwise": metrics.pairwise_kappas(by_judge),
            "uncertain": metrics.rate(sum(r["uncertain"] for r in complete), len(complete)),
        },
        "detection": {},
    }

    for j in judges:
        report["detection"][j] = _detection(judged, lambda r, j=j: r["scores"].get(j))
    report["detection"]["ensemble"] = _detection(judged, lambda r: r["final"])
    report["detection"]["ensemble_certain_only"] = _detection([r for r in judged if not r["uncertain"]],
                                                              lambda r: r["final"])

    overall = report["detection"]["ensemble"]["all"]
    recall = (overall.get("recall") or {}).get("rate")
    ffr = (overall.get("false_flag_rate") or {}).get("rate")
    report["targets"] = {
        "recall": recall, "recall_target": config.TARGET_RECALL,
        "false_flag_rate": ffr, "false_flag_target": config.TARGET_FPR,
        "met": recall is not None and ffr is not None and recall >= config.TARGET_RECALL and ffr <= config.TARGET_FPR,
    }
    report["misses"] = [r for r in judged if r["expected"] == OVERSPECIFIED and not r["flagged"]]
    report["false_flags"] = [r for r in judged if r["expected"] == FINE and r["flagged"]]
    report["uncertain_tasks"] = [r for r in complete if r["uncertain"]]

    out = run_dir(prompt_name)
    out.mkdir(parents=True, exist_ok=True)
    name = split if judges == config.PANEL else f"{split}__{'+'.join(judges)}"
    (out / f"eval_{name}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(out / f"judgments_{name}.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / f"eval_{name}.md").write_text(to_markdown(report), encoding="utf-8")
    return report


def _fmt_rate(entry: dict | None) -> str:
    if not entry or entry.get("rate") is None:
        return "-"
    lo, hi = entry["ci95"]
    return f"{entry['rate']:.0%} ({entry['k']}/{entry['n']}, CI {lo:.0%}-{hi:.0%})"


def _fmt(x, spec=".3f") -> str:
    return "-" if x is None else format(x, spec)


def to_markdown(rep: dict) -> str:
    lines = [f"# STCG judge evaluation: `{rep['prompt']}` on `{rep['split']}`", ""]
    cov = rep["coverage"]
    lines += [f"- tasks: {cov['tasks']}, judged: {cov['judged']}, judged by all judges: {cov['all_judges']}",
              f"- errors per judge: {cov['errors']}", ""]

    t = rep["targets"]
    lines += ["## Targets (ensemble, all tasks)", "",
              f"- recall on overspecified: {_fmt(t['recall'], '.0%')} (target >= {t['recall_target']:.0%})",
              f"- false-flag rate on fine: {_fmt(t['false_flag_rate'], '.0%')} (target <= {t['false_flag_target']:.0%})",
              f"- **{'MET' if t['met'] else 'NOT MET'}**", ""]

    lines += ["## Detection", "", "| scorer | group | recall | false-flag rate |", "|---|---|---|---|"]
    for scorer, groups in rep["detection"].items():
        for group, e in groups.items():
            lines.append(f"| {scorer} | {group} | {_fmt_rate(e.get('recall'))} | {_fmt_rate(e.get('false_flag_rate'))} |")
    lines.append("")

    ag = rep["agreement"]
    lines += ["## Inter-judge agreement", "",
              f"- Fleiss' kappa on the flag (tasks judged by all): {_fmt(ag['fleiss_kappa'])}",
              f"- uncertain (spread >= {config.UNCERTAIN_SPREAD}): {_fmt_rate(ag['uncertain'])}", "",
              "| pair | n | Cohen's kappa | agree |", "|---|---|---|---|"]
    for pair, e in ag["pairwise"].items():
        lines.append(f"| {pair} | {e['n']} | {_fmt(e['kappa'])} | {_fmt(e['agree'], '.0%')} |")
    lines.append("")

    for title, key in (("Missed overspecified tasks", "misses"), ("False flags on fine tasks", "false_flags"),
                       ("Uncertain tasks (reported separately)", "uncertain_tasks")):
        lines += [f"## {title} ({len(rep[key])})", ""]
        for r in rep[key]:
            lines.append(f"- `{r['task_id']}` [{r['source']}] scores={r['scores']} final={r['final']}")
            for j, ex in r["explanations"].items():
                if ex:
                    lines.append(f"  - {j}: {ex}")
        lines.append("")
    return "\n".join(lines)
