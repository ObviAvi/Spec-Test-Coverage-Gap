"""Step 5: relax the tests of a task, check the relaxed tests, and regrade public agent patches against them.

A relaxed test is valid when (1) at least one graded test still fails on the unpatched repo, (2) the gold patch
resolves the task, and (3) every public agent patch that resolved the original task still resolves it.
"""

import ast
import difflib
import hashlib
import json
import random
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from . import config, dockerrun, judging, sources
from .llm import LLMError, make_client
from .prompts import fill, load_template, render_spec, template_sha
from .tasks import load_tasks, mark_fail_to_pass

RELAX_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "relaxable": {"type": "boolean"},
        "edits": {"type": "array", "items": {
            "type": "object",
            "properties": {"file": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
            "required": ["file", "old", "new"], "additionalProperties": False}},
        "summary": {"type": "string"},
    },
    "required": ["reasoning", "relaxable", "edits", "summary"],
    "additionalProperties": False,
}

def relax_schema(prompt_name: str) -> dict:
    """relax_v1 asks for a `reasoning` field. The API declines many such requests (refusal category
    reasoning_extraction), so later prompt versions leave the field out."""
    if "`reasoning`" in load_template(prompt_name):
        return RELAX_SCHEMA
    props = {k: v for k, v in RELAX_SCHEMA["properties"].items() if k != "reasoning"}
    return {**RELAX_SCHEMA, "properties": props, "required": list(props)}


GROUPS = {"flagged": 2, "dev": 1, "control": 0}  # number of panel judges scoring the task >= FLAG_THRESHOLD


class EditError(Exception):
    pass


# ---- which tasks and patches --------------------------------------------------------------------------------

def task_groups(judge_prompt: str) -> dict[str, str]:
    by_count = {n: g for g, n in GROUPS.items()}
    out = {}
    for line in open(judging.run_dir(judge_prompt) / "judgments_verified.jsonl", encoding="utf-8"):
        r = json.loads(line)
        out[r["instance_id"]] = by_count[sum(s >= config.FLAG_THRESHOLD for s in r["scores"].values())]
    return out


def published_report(sub: dict, instance_id: str) -> dict | None:
    """The per-test report the submission published for this task."""
    path = config.RAW / "experiments" / "reports" / sub["name"] / f"{instance_id}.json"
    if not path.exists():
        try:
            sources.fetch(f"{config.SUBMISSIONS_BUCKET}/{sub['logs_prefix']}/{instance_id}/report.json", path, timeout=60)
        except requests.RequestException:
            return None
    try:
        rep = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    return rep.get(instance_id, rep)


def classify_failure(rep: dict | None) -> str:
    """How a patch that did not resolve the task failed, from its published report."""
    if rep is None or not rep.get("tests_status"):
        return "no_report"
    if rep.get("resolved"):
        return "report_says_resolved"
    f2p, p2p = rep["tests_status"]["FAIL_TO_PASS"], rep["tests_status"]["PASS_TO_PASS"]
    if p2p["failure"]:
        return "breaks_old_tests"
    return "new_tests_only" if f2p["failure"] else "no_failures_listed"


def _ranked_submissions() -> list[dict]:
    return sorted(sources.verified_submissions(), key=lambda s: len(s["resolved"]), reverse=True)


def candidates(instance_id: str, subs: list[dict]) -> list[dict]:
    """Top-N patches that failed the task while passing every pre-existing test: the ones a relaxed test can flip."""
    top = [s for s in subs[: config.CONSENSUS_TOP_SUBMISSIONS] if instance_id not in s["resolved"]]
    return [s for s in top if classify_failure(published_report(s, instance_id)) == "new_tests_only"]


def passers(instance_id: str, subs: list[dict]) -> list[dict]:
    top = [s for s in subs[: config.CONSENSUS_TOP_SUBMISSIONS] if instance_id in s["resolved"]]
    rest = [s for s in subs[config.CONSENSUS_TOP_SUBMISSIONS:] if instance_id in s["resolved"]]
    return top + rest[: max(0, config.RELAX_MIN_PASSERS - len(top))]


def _patches(instance_id: str, subs: list[dict]) -> dict[str, list[str]]:
    """Patch text -> names of the submissions that produced it."""
    out: dict[str, list[str]] = {}
    for s in subs:
        patch = sources.agent_patch(s, instance_id)
        if patch and patch.strip():
            out.setdefault(patch, []).append(s["name"])
    return out


# ---- edits ---------------------------------------------------------------------------------------------------

def hunk_ranges(test_patch: str) -> dict[str, list[tuple[int, int]]]:
    """Per file, the line ranges of the patched file that the test patch shows."""
    out, path = {}, None
    for line in test_patch.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@") and path:
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            start, n = int(m[1]), int(m[2] or 1)
            out.setdefault(path, []).append((start, start + n - 1))
    return out


def _parses(source: str) -> bool:
    try:
        ast.parse(source)
        return True
    except (SyntaxError, ValueError):
        return False


def apply_edits(files: dict[str, str], edits: list[dict], ranges: dict) -> dict[str, str]:
    """New contents of the edited files. Every edit must match once, inside a region the test patch shows."""
    spans: dict[str, list] = {}
    for e in edits:
        path, old = e["file"], e["old"]
        if path not in files:
            raise EditError(f"`{path}` is not a file the test patch touches. Files: {', '.join(files)}")
        text = files[path]
        if not old or text.count(old) != 1:
            raise EditError(f"`old` occurs {text.count(old) if old else 0} times in {path}; it must occur exactly once. "
                            f"It started with: {old[:200]!r}")
        i = text.index(old)
        first = text.count("\n", 0, i) + 1
        last = text.count("\n", 0, i + len(old.rstrip("\n"))) + 1
        if not any(a <= first and last <= b for a, b in ranges.get(path, [])):
            raise EditError(f"the edit at lines {first}-{last} of {path} is outside the regions the test patch shows")
        spans.setdefault(path, []).append((i, i + len(old), e["new"]))
    out = {}
    for path, sp in spans.items():
        sp.sort()
        if any(a[1] > b[0] for a, b in zip(sp, sp[1:])):
            raise EditError(f"two edits to {path} overlap")
        text = files[path]
        for i, j, new in reversed(sp):
            text = text[:i] + new + text[j:]
        if path.endswith(".py") and _parses(files[path]) and not _parses(text):
            raise EditError(f"{path} is not valid Python after the edits")
        if text != files[path]:
            out[path] = text
    if not out:
        raise EditError("the edits change nothing")
    return out


def _diff(files: dict[str, str], new_files: dict[str, str]) -> str:
    return "".join("".join(difflib.unified_diff(files[p].splitlines(True), new.splitlines(True), f"a/{p}", f"b/{p}"))
                   for p, new in new_files.items())


# ---- the relaxer ---------------------------------------------------------------------------------------------

def findings(instance_id: str, judge_prompt: str) -> str:
    parts = []
    for judge in config.PANEL:
        rec = judging.load_raw(judge_prompt, judge, f"verified/{instance_id}")
        out = (rec or {}).get("output")
        if out and out["score"] >= config.FLAG_THRESHOLD:
            parts.append(f"Reviewer {len(parts) + 1}: {out['explanation'].strip()}\n"
                         f"Lines responsible: {out['overspecification_vector'].strip()}")
    return "\n\n".join(parts)


def render_prompt(task, gold_patch: str, prompt_name: str, judge_prompt: str, previous: dict | None) -> str:
    prompt = fill(load_template(prompt_name),
                  SPEC=render_spec(task),
                  FAIL_TO_PASS="\n".join(f"- {t}" for t in task.fail_to_pass),
                  TEST_PATCH=mark_fail_to_pass(task.test_patch, task.fail_to_pass),
                  GOLD_PATCH=gold_patch.strip(),
                  FINDINGS=findings(task.instance_id, judge_prompt))
    if previous:
        prompt += ("\n\n<previous_attempt>\nYou already answered this once with these edits:\n"
                   f"{json.dumps(previous['edits'], indent=1)}\n\nThey were rejected: {previous['problem']}\n"
                   "</previous_attempt>\n\nReturn a complete new answer, not a change on top of the previous edits.")
    return prompt


def ask(client, task, gold_patch: str, prompt_name: str, judge_prompt: str, attempt: int, previous: dict | None) -> dict:
    """One relaxer call, cached by attempt number and exact prompt text."""
    prompt = render_prompt(task, gold_patch, prompt_name, judge_prompt, previous)
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    path = judging.run_dir(prompt_name) / "raw" / f"{task.instance_id}.{attempt}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("prompt_digest") == digest and "error" not in rec:
            return rec
    rec = {"instance_id": task.instance_id, "attempt": attempt, "model": client.model, "prompt": prompt_name,
           "prompt_sha": template_sha(prompt_name), "prompt_digest": digest, "prompt_chars": len(prompt)}
    started = time.time()
    try:
        if len(prompt) > config.MAX_PROMPT_CHARS:
            raise ValueError(f"prompt too long ({len(prompt)} chars)")
        for tries_left in (2, 1, 0):  # the model's safety filter refuses some of these calls at random
            try:
                parsed, meta = client.complete_json(prompt, relax_schema(prompt_name))
                break
            except LLMError:
                if not tries_left:
                    raise
        rec.update(output=parsed, **meta)
    except Exception as e:  # recorded; the task is marked as an error and retried on the next run
        rec["error"] = f"{type(e).__name__}: {e}"
    rec["seconds"] = round(time.time() - started, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    return rec


# ---- one task ------------------------------------------------------------------------------------------------

def _failed(run: dict) -> str:
    if run.get("unparsed"):
        return "the tests produced no readable results (for example a syntax or collection error)"
    return ", ".join(run["f2p_failed"] + run["p2p_failed"]) or "(none listed)"


def _check(row: dict, script: str, pass_patches: dict, pool) -> tuple[str, str, dict]:
    """Run the three validity checks. Returns (verdict, problem text for the relaxer, details)."""
    iid = row["instance_id"]
    base, gold = pool.map(lambda p: dockerrun.run(row, p, script), [None, row["patch"]])
    if "error" in base or "error" in gold:
        return "error", "", {}
    f2p = json.loads(row["FAIL_TO_PASS"]) if isinstance(row["FAIL_TO_PASS"], str) else row["FAIL_TO_PASS"]
    details = {"neutralized": sorted(set(f2p) - set(base["f2p_failed"])) if not base.get("unparsed") else []}
    if not base.get("unparsed") and not base["f2p_failed"]:
        return "base_passes", ("with your edits every graded test passes on the unfixed code, so the tests no longer "
                               "detect the reported problem."), details
    if not gold["resolved"]:
        return "gold_fails", (f"with your edits the original fix no longer passes. Failing: {_failed(gold)}\n"
                              f"End of the test output:\n{dockerrun.output_tail(gold['key'], iid)}"), details
    runs = list(pool.map(lambda p: dockerrun.run(row, p, script), pass_patches))
    broken = [(p, r) for p, r in zip(pass_patches, runs) if "error" not in r and not r["resolved"]]
    # a patch that also fails the original tests in our environment says nothing about the relaxed ones
    reproduced = list(pool.map(lambda pr: dockerrun.run(row, pr[0]), broken))
    broken = [pr for pr, orig in zip(broken, reproduced) if orig.get("resolved")]
    details.update(passers=len(pass_patches), passers_error=sum("error" in r for r in runs),
                   passers_unreproduced=sum(not o.get("resolved") for o in reproduced))
    if broken:
        _, r = broken[0]
        return "passer_fails", ("a fix that passes the original tests fails yours, so your tests added a requirement. "
                                f"Failing: {_failed(r)}\nEnd of the test output:\n{dockerrun.output_tail(r['key'], iid)}"), details
    return "ok", "", details


def process(iid: str, ctx: dict, regrade: bool) -> dict:
    row, task = dockerrun.eval_rows()[iid], ctx["tasks"][iid]
    rec = {"instance_id": iid, "group": ctx["groups"][iid], "prompt": ctx["prompt"],
           "prompt_sha": template_sha(ctx["prompt"]), "status": "invalid", "attempts": []}
    try:
        files = dockerrun.test_files(row)
    except Exception as e:
        return {**rec, "status": "error", "error": f"{type(e).__name__}: {e}"}
    ranges = hunk_ranges(task.test_patch)
    pass_patches = _patches(iid, passers(iid, ctx["subs"])[: ctx["max_passers"]])
    previous, script = None, None
    for n in range(config.RELAX_ATTEMPTS):
        raw = ask(ctx["client"], task, row["patch"], ctx["prompt"], ctx["judge_prompt"], n, previous)
        if "error" in raw:
            return {**rec, "status": "error", "error": raw["error"]}
        out = raw["output"]
        att = {"relaxable": out["relaxable"], "summary": out["summary"], "edits": len(out["edits"])}
        rec["attempts"].append(att)
        if not out["relaxable"]:
            rec["status"] = "declined"
            break
        try:
            new_files = apply_edits(files, out["edits"], ranges)
            script = dockerrun.relaxed_script(row, new_files)
        except (EditError, ValueError) as e:
            att["check"], problem = "edit_error", str(e)
        else:
            att["check"], problem, details = _check(row, script, pass_patches, ctx["pool"])
            if att["check"] == "error":
                return {**rec, "status": "error", "error": "container run failed during the checks"}
            att.update(details)
        if att["check"] == "ok":
            diff = _diff(files, new_files)
            rec.update(status="valid", diff=diff, neutralized=att["neutralized"],
                       lines_changed=sum(l[:1] in "+-" and l[:3] not in ("+++", "---") for l in diff.splitlines()))
            break
        previous = {"edits": out["edits"], "problem": problem}
    if rec["status"] == "valid" and regrade:
        rec["regrade"] = _regrade(row, script, _patches(iid, candidates(iid, ctx["subs"])), ctx["pool"])
    return rec


def _regrade(row: dict, script: str, cand_patches: dict, pool) -> list[dict]:
    """Outcome of each candidate patch under the relaxed tests. A flip must also fail the original tests when we
    rerun them, so it cannot come from a difference between our environment and the published run."""
    runs = list(pool.map(lambda p: dockerrun.run(row, p, script), cand_patches))
    flips = [p for p, r in zip(cand_patches, runs) if r.get("resolved")]
    orig = dict(zip(flips, pool.map(lambda p: dockerrun.run(row, p), flips)))
    out = []
    for (patch, names), r in zip(cand_patches.items(), runs):
        if "error" in r or "error" in orig.get(patch, {}):
            outcome = "error"
        elif r.get("apply_failed"):
            outcome = "patch_does_not_apply"
        elif not r["resolved"]:
            outcome = "still_fails"
        else:
            outcome = "passes_original_here" if orig[patch]["resolved"] else "flip"
        out.append({"submissions": names, "outcome": outcome, "f2p_failed": r.get("f2p_failed", []),
                    "p2p_failed": r.get("p2p_failed", [])})
    return out


# ---- the run -------------------------------------------------------------------------------------------------

def _task_path(prompt_name: str, iid: str) -> Path:
    return judging.run_dir(prompt_name) / "tasks" / f"{iid}.json"


def _done(prompt_name: str, iid: str, regrade: bool) -> bool:
    path = _task_path(prompt_name, iid)
    if not path.exists():
        return False
    rec = json.loads(path.read_text(encoding="utf-8"))
    if rec["status"] == "error" or rec["prompt_sha"] != template_sha(prompt_name):
        return False
    if any(r["outcome"] == "error" for r in rec.get("regrade", [])):
        return False
    return not (regrade and rec["status"] == "valid" and "regrade" not in rec)


def select(group: str, judge_prompt: str, subs: list[dict]) -> list[str]:
    """Flagged and control tasks need a patch that could flip. Dev tasks are shuffled so --limit takes a sample."""
    groups = task_groups(judge_prompt)
    ids = sorted(i for i, g in groups.items() if g == group)
    if group == "dev":
        random.Random(config.SEED).shuffle(ids)
        return ids
    with ThreadPoolExecutor(max_workers=16) as pool:
        has = list(pool.map(lambda i: bool(candidates(i, subs)), ids))
    return [i for i, h in zip(ids, has) if h]


def run_relax(group: str, prompt_name: str, judge_prompt: str, ids: list[str] | None, skip: int, limit: int | None,
              regrade: bool, max_passers: int | None, task_workers: int, run_workers: int, keep_images: bool) -> None:
    subs = _ranked_submissions()
    todo = ids or select(group, judge_prompt, subs)[skip:][:limit]
    ctx = {"tasks": {t.instance_id: t for t in load_tasks(config.TASKS / "verified.jsonl")},
           "groups": task_groups(judge_prompt), "subs": subs, "prompt": prompt_name, "judge_prompt": judge_prompt,
           "client": make_client(config.RELAXER), "max_passers": max_passers,
           "pool": ThreadPoolExecutor(max_workers=run_workers)}
    pending = [i for i in todo if not _done(prompt_name, i, regrade)]
    print(f"{len(todo)} tasks, {len(todo) - len(pending)} done, {len(pending)} to run")
    dockerrun.eval_rows()

    def one(iid):
        rec = process(iid, ctx, regrade)
        path = _task_path(prompt_name, iid)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        if not keep_images:
            dockerrun.remove_image(dockerrun.eval_rows()[iid])
        return rec

    with ThreadPoolExecutor(max_workers=task_workers) as tasks_pool:
        for n, rec in enumerate(tasks_pool.map(one, pending), 1):
            flips = sum(r["outcome"] == "flip" for r in rec.get("regrade", []))
            extra = f", {flips}/{len(rec['regrade'])} flipped" if "regrade" in rec else ""
            checks = [a.get("check", "declined") for a in rec["attempts"]]
            print(f"  [{n}/{len(pending)}] {rec['instance_id']}: {rec['status']} {checks}{extra} {rec.get('error', '')}", flush=True)
    print(summary(prompt_name, todo))


def summary(prompt_name: str, ids: list[str]) -> str:
    recs = [json.loads(_task_path(prompt_name, i).read_text(encoding="utf-8")) for i in ids if _task_path(prompt_name, i).exists()]
    status = Counter(r["status"] for r in recs)
    valid = [r for r in recs if r["status"] == "valid"]
    first = sum(len(r["attempts"]) == 1 for r in valid)
    lines = [f"{len(recs)} tasks: " + ", ".join(f"{k} {v}" for k, v in status.most_common()),
             f"valid on the first attempt: {first}",
             f"failed checks: {dict(Counter(a['check'] for r in recs for a in r['attempts'] if a.get('check') not in (None, 'ok')))}"]
    if valid:
        changed = sorted(r["lines_changed"] for r in valid)
        lines.append(f"lines changed per valid task: median {changed[len(changed) // 2]}, max {changed[-1]}; "
                     f"tasks with a neutralized test: {sum(bool(r['neutralized']) for r in valid)}")
    graded = [x for r in valid for x in r.get("regrade", [])]
    if graded:
        n = Counter(x["outcome"] for x in graded for _ in x["submissions"])
        lines.append(f"regraded patches: {dict(n)}; tasks with a flip: "
                     f"{sum(any(x['outcome'] == 'flip' for x in r.get('regrade', [])) for r in valid)} of {len(valid)}")
    return "\n".join(lines)
