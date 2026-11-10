"""Step 2: build the validation sets of known-overspecified and known-fine tasks, then split dev/test.

Overspecified (judge should say 3-4)      Fine (judge should say 1-2)
  openai_excluded       (2.1a)              agent_consensus        (2.2a)
  pro_narrow_original   (2.1b)

The repaired SWE-Bench Pro Verified versions are not a fine set: the repairs fixed the reported narrow
check only, so many still carry other overspecified checks. The 12 hand-labelled pilot tasks
(data/pilot_labels.json) were used to write the rubric, so they are kept out of every set.
"""

import json
import random
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from itertools import combinations

from . import config, sources
from .tasks import Task, load_tasks, save_tasks

OVERSPECIFIED, FINE = "overspecified", "fine"


def _num(x: str) -> float:
    return float(x) if x not in ("", None) else float("nan")


def openai_excluded(full: dict[str, Task], exclude: set[str]) -> list[Task]:
    """Tasks dropped from Verified where all 3 annotators rated false_negative >= 2 (tests may reject valid
    solutions), the issue itself was clear (ensembled underspecified <= 1), and nothing else was wrong.
    The last two filters keep the label about test overspecification rather than a vague issue."""
    ensembled, per = sources.openai_annotations()
    out = []
    for iid, row in sorted(ensembled.items()):
        annots = per.get(iid, [])
        if (iid in exclude or row["filter_out"] != "True" or len(annots) != 3
                or not all(_num(a["false_negative"]) >= 2 for a in annots)
                or _num(row["underspecified"]) > 1 or _num(row["other_major_issues"]) > 0
                or iid not in full):
            continue
        notes = [a["false_negative_notes"] for a in annots]
        out.append(replace(full[iid], expected=OVERSPECIFIED,
                           meta={**full[iid].meta, "false_negative_scores": [a["false_negative"] for a in annots],
                                 "annotator_notes": notes}))
    return out


def pro_narrow(pro: dict[str, Task], pro_verified: dict[str, Task]) -> list[Task]:
    """The 75 'overly narrow tests' tasks SWE-Bench Pro Verified repaired, original (overspecified) versions."""
    ids = sources.pro_verified_categories()["overly narrow tests"]
    originals = []
    for iid in ids:
        orig, fixed = pro[iid], pro_verified[iid]
        changed = [f for f in ("problem_statement", "requirements", "interface", "test_patch")
                   if getattr(orig, f).strip() != getattr(fixed, f).strip()]
        originals.append(replace(orig, expected=OVERSPECIFIED, meta={**orig.meta, "fields_changed_by_repair": changed}))
    return originals


_SKIP_LINE = re.compile(r"^(diff --git|index |--- |\+\+\+ |@@)")


def changed_lines(patch: str) -> frozenset[str]:
    """Normalized +/- lines of a patch, ignoring files the patch creates (agents' scratch/repro scripts)."""
    out = set()
    for block in re.split(r"(?m)^(?=diff --git )", patch):
        if "\nnew file mode" in block[:500]:
            continue
        for line in block.splitlines():
            if _SKIP_LINE.match(line) or line[:1] not in ("+", "-"):
                continue
            body = " ".join(line[1:].split())
            if body:
                out.add(line[0] + body)
    return frozenset(out)


def mean_jaccard(sets: list[frozenset]) -> float:
    pairs = list(combinations(sets, 2))
    return sum(len(a & b) / len(a | b) if a | b else 1.0 for a, b in pairs) / len(pairs)


def agent_consensus(verified: dict[str, Task], exclude: set[str]) -> list[Task]:
    """Verified tasks where all 3 OpenAI annotators rated false_negative 0 (tests accept every valid
    solution), almost every top public agent resolves it, and the resolving patches look different from
    each other. If very different fixes all pass, the tests are not pinning one implementation."""
    _, per = sources.openai_annotations()
    subs = sorted(sources.verified_submissions(), key=lambda s: len(s["resolved"]), reverse=True)
    top = subs[: config.CONSENSUS_TOP_SUBMISSIONS]
    print(f"  agent_consensus: using top {len(top)} of {len(subs)} submissions "
          f"({len(top[-1]['resolved'])}-{len(top[0]['resolved'])} resolved)")
    resolvers = {iid: [s for s in top if iid in s["resolved"]] for iid in verified}
    candidates = [iid for iid, rs in resolvers.items()
                  if len(rs) / len(top) >= config.CONSENSUS_MIN_RESOLVE_RATE and iid not in exclude
                  and len(per.get(iid, [])) == 3 and all(_num(a["false_negative"]) == 0 for a in per[iid])]
    print(f"  agent_consensus: {len(candidates)} tasks with unanimous false_negative 0 and resolved by "
          f">= {config.CONSENSUS_MIN_RESOLVE_RATE:.0%}; fetching patches")

    def score(iid: str):
        rng = random.Random(f"{config.SEED}:{iid}")  # per task: a shared rng across threads is not reproducible
        rs = resolvers[iid]
        rs = rng.sample(rs, min(len(rs), config.CONSENSUS_PATCHES_PER_TASK)) if len(rs) > config.CONSENSUS_PATCHES_PER_TASK else rs
        sets = [changed_lines(p) for p in (sources.agent_patch(s, iid) for s in rs) if p]
        sets = [s for s in sets if s]
        if len(sets) < 3:
            return iid, None, len(sets), 0
        return iid, mean_jaccard(sets), len(sets), len(set(sets))

    with ThreadPoolExecutor(max_workers=16) as pool:
        scored = [r for r in pool.map(score, sorted(candidates)) if r[1] is not None]
    diverse = sorted((r for r in scored if r[1] <= config.CONSENSUS_MAX_PATCH_SIMILARITY), key=lambda r: r[1])
    out = []
    for iid, sim, n_patches, n_distinct in diverse:
        t = verified[iid]
        out.append(replace(t, expected=FINE, meta={
            **t.meta, "resolve_rate": len(resolvers[iid]) / len(top), "patch_mean_jaccard": round(sim, 3),
            "patches_compared": n_patches, "distinct_patches": n_distinct}))
    print(f"  agent_consensus: {len(out)} pass the similarity cap")
    return out


def build_all() -> dict[str, list[Task]]:
    print("Loading SWE-bench Verified...")
    verified_list = sources.verified_tasks()
    save_tasks(verified_list, config.TASKS / "verified.jsonl")
    verified = {t.instance_id: t for t in verified_list}
    pilot_ids = set(json.loads((config.DATA / "pilot_labels.json").read_text(encoding="utf-8")))

    print("Loading full SWE-bench + OpenAI annotations...")
    excluded = openai_excluded(sources.full_swebench_tasks(), pilot_ids)

    print("Loading SWE-bench Pro (v1) + SWE-Bench Pro Verified...")
    pro_orig = pro_narrow(sources.pro_tasks(), sources.pro_verified_tasks())

    print("Selecting agent-consensus tasks from SWE-bench/experiments...")
    consensus = agent_consensus(verified, pilot_ids)

    sets = {"openai_excluded": excluded, "pro_narrow_original": pro_orig, "agent_consensus": consensus}
    for name, tasks in sets.items():
        save_tasks(tasks, config.VALIDATION / f"{name}.jsonl")
        print(f"  {name}: {len(tasks)}")
    return sets


def load_validation(split: str | None = None) -> list[Task]:
    """All validation tasks, optionally restricted to the dev or test split."""
    tasks = []
    for path in sorted(config.VALIDATION.glob("*.jsonl")):
        tasks += [replace(t, source=path.stem) for t in load_tasks(path)]
    if split in (None, "all"):
        return tasks
    groups = json.loads((config.VALIDATION / "split.json").read_text(encoding="utf-8"))
    keep = set(groups[split])
    return [t for t in tasks if t.instance_id in keep]


def make_split(dev_fraction: float = config.DEV_FRACTION, seed: int = config.SEED) -> dict[str, list[str]]:
    """Split by instance_id, sampled stratified by source.
    Instances already in split.json keep their side, so growing a set never moves judged dev tasks into
    test; only new instances are sampled. Delete split.json to redraw everything."""
    tasks = load_validation()
    by_instance: dict[str, set[str]] = {}
    for t in tasks:
        by_instance.setdefault(t.instance_id, set()).add(t.source)
    path = config.VALIDATION / "split.json"
    prev = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"dev": [], "test": []}
    dev = {i for i in prev["dev"] if i in by_instance}
    test = {i for i in prev["test"] if i in by_instance} - dev
    # stratify on the instance's "primary" source so every set is represented in dev
    strata: dict[str, list[str]] = {}
    for iid in sorted(by_instance):
        if iid not in dev and iid not in test:
            strata.setdefault(min(by_instance[iid]), []).append(iid)
    rng = random.Random(seed)
    for name, ids in sorted(strata.items()):
        rng.shuffle(ids)
        k = round(dev_fraction * len(ids))
        dev |= set(ids[:k])
        test |= set(ids[k:])
    split = {"dev": sorted(dev), "test": sorted(test)}
    path.write_text(json.dumps(split, indent=1), encoding="utf-8")
    counts = {name: Counter(t.source for t in tasks if t.instance_id in set(ids)) for name, ids in split.items()}
    for name, c in counts.items():
        print(f"  {name}: {len(split[name])} instances, {sum(c.values())} tasks  {dict(sorted(c.items()))}")
    return split
