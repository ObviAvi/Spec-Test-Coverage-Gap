"""Step 1: run every judge on every task, cache raw outputs, aggregate to a final label."""

import json
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import config
from .llm import make_client
from .prompts import JUDGE_SCHEMA, render_judge_prompt, template_sha
from .tasks import Task


def run_dir(prompt_name: str) -> Path:
    return config.RESULTS / prompt_name


def _raw_path(prompt_name: str, judge: str, task_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", task_id)
    return run_dir(prompt_name) / "raw" / judge / f"{safe}.json"


def load_raw(prompt_name: str, judge: str, task_id: str) -> dict | None:
    path = _raw_path(prompt_name, judge, task_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _judge_one(client, judge: str, task: Task, prompt_name: str, sha: str) -> dict:
    prompt = render_judge_prompt(task, prompt_name)
    record = {"task_id": task.task_id, "judge": judge, "model": client.model,
              "prompt": prompt_name, "prompt_sha": sha, "prompt_chars": len(prompt)}
    if len(prompt) > config.MAX_PROMPT_CHARS:
        record["error"] = f"prompt too long ({len(prompt)} chars), skipped"
        return record
    started = time.time()
    try:
        parsed, meta = client.complete_json(prompt, JUDGE_SCHEMA)
        if parsed.get("score") not in (1, 2, 3, 4):
            raise ValueError(f"score out of range: {parsed.get('score')!r}")
        record.update(output=parsed, **meta)
    except Exception as e:  # keep going; failures are recorded and retried on the next run
        record["error"] = f"{type(e).__name__}: {e}"
    record["seconds"] = round(time.time() - started, 1)
    return record


def run_judges(tasks: list[Task], judges: list[str], prompt_name: str, workers: int = 4) -> None:
    """Judge each (task, judge) pair not already cached with this exact prompt text."""
    sha = template_sha(prompt_name)
    for judge in judges:
        todo = []
        for t in tasks:
            cached = load_raw(prompt_name, judge, t.task_id)
            if cached and cached.get("prompt_sha") != sha:
                raise SystemExit(f"prompts/{prompt_name}.txt changed since {judge} judged {t.task_id}. "
                                 "Copy it to a new version name instead of editing in place.")
            if not cached or "error" in cached:
                todo.append(t)
        print(f"[{judge}] {len(tasks) - len(todo)} cached, {len(todo)} to judge")
        if not todo:
            continue
        client = make_client(judge)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_judge_one, client, judge, t, prompt_name, sha): t for t in todo}
            for i, fut in enumerate(as_completed(futures), 1):
                rec = fut.result()
                path = _raw_path(prompt_name, judge, rec["task_id"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
                status = rec["error"] if "error" in rec else f"score {rec['output']['score']}"
                print(f"  [{judge} {i}/{len(todo)}] {rec['task_id']}: {status}")


def aggregate(task: Task, judges: list[str], prompt_name: str) -> dict:
    """Final label = median of the judges that answered; spread >= UNCERTAIN_SPREAD marks it uncertain."""
    scores, explanations, errors = {}, {}, {}
    for judge in judges:
        rec = load_raw(prompt_name, judge, task.task_id)
        if rec is None:
            continue
        if "error" in rec:
            errors[judge] = rec["error"]
        else:
            scores[judge] = rec["output"]["score"]
            explanations[judge] = rec["output"]["explanation"]
    values = list(scores.values())
    final = statistics.median_low(values) if values else None
    spread = max(values) - min(values) if values else None
    return {
        "task_id": task.task_id, "instance_id": task.instance_id, "source": task.source,
        "benchmark": task.benchmark, "expected": task.expected,
        "scores": scores, "final": final, "spread": spread,
        "uncertain": spread is not None and spread >= config.UNCERTAIN_SPREAD,
        "complete": len(scores) == len(judges),
        "flagged": final is not None and final >= config.FLAG_THRESHOLD,
        "explanations": explanations, "errors": errors,
    }


def estimate(tasks: list[Task], judges: list[str], prompt_name: str) -> str:
    chars = [len(render_judge_prompt(t, prompt_name)) for t in tasks]
    too_long = sum(c > config.MAX_PROMPT_CHARS for c in chars)
    # ~4 chars/token is rough for code; treat this as an order of magnitude
    return (f"{len(tasks)} tasks x {len(judges)} judges = {len(tasks) * len(judges)} calls, "
            f"~{sum(chars) / 4 / 1e6 * len(judges):.2f}M input tokens total, "
            f"median prompt {statistics.median(chars) if chars else 0:,.0f} chars, {too_long} over the length limit")
