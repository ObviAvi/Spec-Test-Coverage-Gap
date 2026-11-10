"""Download and normalize the upstream datasets. Everything is cached under data/raw/."""

import csv
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import yaml

from . import config
from .tasks import Task, parse_test_list


def fetch(url: str, path: Path, timeout: int = 120) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(resp.content)
    tmp.replace(path)
    return path


def _hf_rows(name: str, config_name: str | None = None) -> list[dict]:
    from datasets import load_dataset

    return list(load_dataset(name, config_name, split="test"))


def _swebench_task(row: dict, benchmark: str, prefix: str) -> Task:
    return Task(
        task_id=f"{prefix}/{row['instance_id']}",
        instance_id=row["instance_id"],
        benchmark=benchmark,
        problem_statement=row["problem_statement"],
        test_patch=row["test_patch"],
        fail_to_pass=parse_test_list(row.get("FAIL_TO_PASS") or row.get("fail_to_pass")),
        requirements=row.get("requirements") or "",
        interface=row.get("interface") or "",
        gold_patch=row.get("patch") or "",
        meta={"repo": row["repo"]},
    )


def verified_tasks() -> list[Task]:
    return [_swebench_task(r, "swe-bench-verified", "verified") for r in _hf_rows(config.VERIFIED_HF)]


def full_swebench_tasks() -> dict[str, Task]:
    return {r["instance_id"]: _swebench_task(r, "swe-bench-full", "full")
            for r in _hf_rows(config.FULL_HF)}


def pro_tasks() -> dict[str, Task]:
    rows = _hf_rows(config.PRO_HF, config.PRO_HF_CONFIG)
    return {r["instance_id"]: _swebench_task(r, "swe-bench-pro", "pro") for r in rows}


def pro_verified_tasks() -> dict[str, Task]:
    path = fetch(f"{config.PRO_VERIFIED_BASE}/swebench_pro_verified.jsonl",
                 config.RAW / "pro_verified" / "swebench_pro_verified.jsonl")
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return {r["instance_id"]: _swebench_task(r, "swe-bench-pro-verified", "pro-verified") for r in rows}


def pro_verified_categories() -> dict[str, list[str]]:
    """The dataset card lists repaired instance ids per category in fenced blocks under '- **Name** (N samples)'."""
    path = fetch(f"{config.PRO_VERIFIED_BASE}/README.md", config.RAW / "pro_verified" / "README.md")
    text = path.read_text(encoding="utf-8")
    cats = {}
    for m in re.finditer(r"- \*\*(.+?)\*\* \((\d+) samples\)\s*```text\n(.*?)```", text, re.S):
        ids = [line.strip() for line in m.group(3).splitlines() if line.strip()]
        if len(ids) != int(m.group(2)):
            raise ValueError(f"{m.group(1)}: card says {m.group(2)} ids, parsed {len(ids)}")
        cats[m.group(1).strip().lower()] = ids
    return cats


def openai_annotations() -> tuple[dict[str, dict], dict[str, list[dict]]]:
    """(ensembled row per instance, the three per-annotator rows per instance) from OpenAI's Verified release."""
    path = fetch(config.OPENAI_ANNOTATIONS_ZIP, config.RAW / "openai" / "swe-bench-annotation-results.zip")
    with zipfile.ZipFile(path) as z:
        def read(name):
            return list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8")))
        ensembled = {r["instance_id"]: r for r in read("ensembled_annotations_public.csv")}
        per = {}
        for r in read("samples_with_3_annotations_public.csv"):
            per.setdefault(r["instance_id"], []).append(r)
    return ensembled, per


# --- SWE-bench/experiments: per-submission resolved sets and agent patches -----------------

def _github_json(url: str, path: Path) -> dict | list:
    return json.loads(fetch(url, path).read_text(encoding="utf-8"))


def verified_submissions() -> list[dict]:
    """Every Verified submission with its resolved set and S3 logs prefix (where patch.diff lives)."""
    raw = config.RAW / "experiments"
    tree = _github_json(f"https://api.github.com/repos/{config.EXPERIMENTS_REPO}/git/trees/main?recursive=1",
                        raw / "tree.json")
    files: dict[str, set] = {}
    for item in tree["tree"]:
        parts = item["path"].split("/")
        if len(parts) >= 4 and parts[:2] == ["evaluation", "verified"]:
            files.setdefault(parts[2], set()).add("/".join(parts[3:]))

    base = f"https://raw.githubusercontent.com/{config.EXPERIMENTS_REPO}/main/evaluation/verified"

    def load(name: str) -> dict | None:
        have = files[name]
        if "metadata.yaml" not in have:
            return None
        meta = yaml.safe_load(fetch(f"{base}/{name}/metadata.yaml", raw / name / "metadata.yaml").read_text(encoding="utf-8"))
        logs = ((meta or {}).get("assets") or {}).get("logs") or ""
        if "results/results.json" in have:
            resolved = set(_github_json(f"{base}/{name}/results/results.json", raw / name / "results.json")["resolved"])
        elif "per_instance_details.json" in have:
            details = _github_json(f"{base}/{name}/per_instance_details.json", raw / name / "per_instance_details.json")
            resolved = {iid for iid, d in details.items() if d.get("resolved")}
        else:
            return None
        if not logs.startswith("s3://swe-bench-submissions/"):
            return None
        return {"name": name, "resolved": resolved, "logs_prefix": logs.removeprefix("s3://swe-bench-submissions/").rstrip("/")}

    with ThreadPoolExecutor(max_workers=16) as pool:
        subs = [s for s in pool.map(load, sorted(files)) if s]
    return subs


def agent_patch(submission: dict, instance_id: str) -> str | None:
    path = config.RAW / "experiments" / "patches" / submission["name"] / f"{instance_id}.diff"
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    url = f"{config.SUBMISSIONS_BUCKET}/{submission['logs_prefix']}/{instance_id}/patch.diff"
    try:
        fetch(url, path, timeout=60)
    except requests.HTTPError:
        return None
    return path.read_text(encoding="utf-8", errors="replace")
