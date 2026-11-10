"""Task record shared by every stage, plus JSONL io."""

import ast
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Task:
    task_id: str                 # unique across all files, e.g. "verified/django__django-11179"
    instance_id: str             # upstream id; the dev/test split is by this
    benchmark: str               # swe-bench-verified | swe-bench-full | swe-bench-pro | swe-bench-pro-verified
    problem_statement: str
    test_patch: str
    fail_to_pass: list = field(default_factory=list)
    requirements: str = ""       # SWE-bench Pro only: agents see these alongside the issue
    interface: str = ""
    gold_patch: str = ""         # the official fix; only prompts with {{GOLD_PATCH}} show it
    source: str = ""             # validation set = its file name; set on load, not stored
    expected: str | None = None  # validation label: "overspecified" | "fine"
    meta: dict = field(default_factory=dict)


def parse_test_list(value) -> list:
    """FAIL_TO_PASS comes as a list, a JSON string, or a Python-literal string depending on the dataset."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return list(ast.literal_eval(value))


def save_tasks(tasks: list[Task], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for t in tasks:
            row = asdict(t)
            del row["source"]
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_tasks(path: Path) -> list[Task]:
    with open(path, encoding="utf-8") as f:
        return [Task(**json.loads(line)) for line in f if line.strip()]


_PY_TEST_DEF = re.compile(r"^\+\s*(?:async\s+)?def\s+(test\w*)\s*\(")


def _short_name(test_id: str) -> str:
    # "tests/x.py::Cls::test_foo[param]" / "test_foo (mod.Cls)" -> "test_foo"
    name = test_id.split("::")[-1].split(" (")[0]
    return name.split("[")[0].strip()


def mark_fail_to_pass(test_patch: str, fail_to_pass: list) -> str:
    """Tag added Python test definitions that are FAIL_TO_PASS. Other languages rely on the explicit list."""
    names = {_short_name(t) for t in fail_to_pass}
    out = []
    for line in test_patch.splitlines():
        m = _PY_TEST_DEF.match(line)
        if m and m.group(1) in names:
            line += "  # <-- FAIL_TO_PASS"
        out.append(line)
    return "\n".join(out)
