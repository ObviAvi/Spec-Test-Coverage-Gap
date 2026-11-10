"""Ablations: compare prompt versions against a base prompt on the same tasks."""

import json

from . import config, metrics
from .evaluate import _detection, _fmt_rate
from .judging import aggregate
from .tasks import Task
from .validation import FINE, OVERSPECIFIED


def _flag(score: int) -> bool:
    return score >= config.FLAG_THRESHOLD


def flag_changes(base: list[int], other: list[int]) -> dict:
    """How one scorer's scores and flags moved between two runs over the same tasks."""
    pairs = list(zip(base, other))
    return {"same_score": sum(a == b for a, b in pairs),
            "newly_flagged": sum(not _flag(a) and _flag(b) for a, b in pairs),
            "unflagged": sum(_flag(a) and not _flag(b) for a, b in pairs),
            "kappa": metrics.cohen_kappa([_flag(a) for a in base], [_flag(b) for b in other])}


def _scorers(judges: list[str]) -> dict:
    return {"panel": lambda r: r["final"], **{j: (lambda r, j=j: r["scores"][j]) for j in judges}}


def _summary(rows: list[dict], judges: list[str]) -> dict:
    flags = {j: {r["task_id"]: _flag(r["scores"][j]) for r in rows} for j in judges}
    return {"detection": {name: _detection(rows, f) for name, f in _scorers(judges).items()},
            "pairwise": metrics.pairwise_kappas(flags),
            "uncertain": sum(r["uncertain"] for r in rows)}


def compare(tasks: list[Task], judges: list[str], base: str, others: list[str], split: str) -> dict:
    runs = {p: {t.task_id: aggregate(t, judges, p) for t in tasks} for p in [base, *others]}
    ids = [t.task_id for t in tasks if all(runs[p][t.task_id]["complete"] for p in runs)]
    if not ids:
        raise SystemExit("No task is judged by all judges under every prompt.")
    rows = {p: [runs[p][i] for i in ids] for p in runs}

    rep = {"split": split, "judges": judges, "base": base, "tasks": len(ids),
           "prompts": {p: _summary(rows[p], judges) for p in runs}, "vs_base": {}}
    for p in others:
        pairs = list(zip(rows[base], rows[p]))
        entry = {name: flag_changes([f(b) for b, _ in pairs], [f(o) for _, o in pairs])
                 for name, f in _scorers(judges).items()}
        entry["panel_by_label"] = {
            label: {"unflagged": sum(b["flagged"] and not o["flagged"] for b, o in pairs if b["expected"] == label),
                    "newly_flagged": sum(o["flagged"] and not b["flagged"] for b, o in pairs if b["expected"] == label)}
            for label in (OVERSPECIFIED, FINE)}
        entry["changed_tasks"] = [{"task_id": b["task_id"], "source": b["source"], "expected": b["expected"],
                                   "base_scores": b["scores"], "scores": o["scores"]}
                                  for b, o in pairs if b["flagged"] != o["flagged"]]
        rep["vs_base"][p] = entry

    config.RESULTS.mkdir(parents=True, exist_ok=True)
    (config.RESULTS / f"compare_{split}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    (config.RESULTS / f"compare_{split}.md").write_text(to_markdown(rep), encoding="utf-8")
    return rep


def to_markdown(rep: dict) -> str:
    base, judges = rep["base"], rep["judges"]
    sources = [g for g in rep["prompts"][base]["detection"]["panel"] if g != "all"]
    recall_sources = [s for s in sources if "recall" in rep["prompts"][base]["detection"]["panel"][s]]
    count = lambda e: f"{e['k']}/{e['n']}" if e else "-"

    lines = [f"# Prompt comparison on `{rep['split']}` ({rep['tasks']} tasks, base `{base}`)", "",
             "## Panel", "",
             "| prompt | recall | false-flag rate | " + " | ".join(f"recall, {s.split(':')[1]}" for s in recall_sources)
             + " | judge kappa | uncertain |",
             "|---|---|---|" + "---|" * (len(recall_sources) + 2)]
    for p, s in rep["prompts"].items():
        d = s["detection"]["panel"]
        kappa = " / ".join(f"{e['kappa']:.2f}" for e in s["pairwise"].values())
        lines.append(f"| {p} | {_fmt_rate(d['all'].get('recall'))} | {_fmt_rate(d['all'].get('false_flag_rate'))} | "
                     + " | ".join(count(d[src].get("recall")) for src in recall_sources)
                     + f" | {kappa} | {s['uncertain']} |")

    lines += ["", "## Each judge alone", "", "| prompt | judge | recall | false-flag rate |", "|---|---|---|---|"]
    for p, s in rep["prompts"].items():
        for j in judges:
            d = s["detection"][j]["all"]
            lines.append(f"| {p} | {j} | {_fmt_rate(d.get('recall'))} | {_fmt_rate(d.get('false_flag_rate'))} |")

    lines += ["", f"## Changes against `{base}`", "",
              "Same tasks, so every difference is a task whose score or flag moved. "
              "Kappa is between the two runs' flags.", "",
              "| prompt | scorer | same score | newly flagged | unflagged | kappa |", "|---|---|---|---|---|---|"]
    for p, e in rep["vs_base"].items():
        for name in ["panel", *judges]:
            c = e[name]
            lines.append(f"| {p} | {name} | {c['same_score']}/{rep['tasks']} | {c['newly_flagged']} | {c['unflagged']} "
                         f"| {c['kappa']:.2f} |")

    lines += ["", "Panel flag changes by expected label:", "",
              "| prompt | overspecified: flag lost | overspecified: flag gained | fine: flag gained | fine: flag lost |",
              "|---|---|---|---|---|"]
    for p, e in rep["vs_base"].items():
        o, f = e["panel_by_label"][OVERSPECIFIED], e["panel_by_label"][FINE]
        lines.append(f"| {p} | {o['unflagged']} | {o['newly_flagged']} | {f['newly_flagged']} | {f['unflagged']} |")

    for p, e in rep["vs_base"].items():
        lines += ["", f"### Tasks whose panel flag changed: `{p}` ({len(e['changed_tasks'])})", ""]
        lines += [f"- `{t['task_id']}` [{t['source']}, {t['expected']}] {t['base_scores']} -> {t['scores']}"
                  for t in e["changed_tasks"]]
    return "\n".join(lines) + "\n"
