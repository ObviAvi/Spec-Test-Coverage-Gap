"""Versioned prompt templates. A version is a file `prompts/<name>.txt`; edit by copying to a new version."""

import hashlib

from . import config
from .tasks import Task, mark_fail_to_pass

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "score": {"type": "integer", "enum": [1, 2, 3, 4]},
        "explanation": {"type": "string"},
        "overspecification_vector": {"type": "string"},
    },
    "required": ["reasoning", "score", "explanation", "overspecification_vector"],
    "additionalProperties": False,
}


def load_template(name: str) -> str:
    return (config.PROMPTS / f"{name}.txt").read_text(encoding="utf-8")


def template_sha(name: str) -> str:
    return hashlib.sha256(load_template(name).encode("utf-8")).hexdigest()[:12]


def fill(template: str, **values: str) -> str:
    # {{KEY}} placeholders, so braces in code/diffs never need escaping
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def render_spec(task: Task) -> str:
    parts = [f"Issue:\n{task.problem_statement.strip()}"]
    if task.requirements.strip():
        parts.append(f"Requirements:\n{task.requirements.strip()}")
    if task.interface.strip():
        parts.append(f"Interface:\n{task.interface.strip()}")
    return "\n\n".join(parts)


def render_judge_prompt(task: Task, template_name: str) -> str:
    f2p = "\n".join(f"- {t}" for t in task.fail_to_pass) or "(not provided)"
    template = load_template(template_name)
    if "{{GOLD_PATCH}}" in template and not task.gold_patch.strip():
        raise ValueError(f"{task.task_id}: {template_name} needs gold_patch; rebuild the validation sets")
    return fill(
        template,
        SPEC=render_spec(task),
        FAIL_TO_PASS=f2p,
        TEST_PATCH=mark_fail_to_pass(task.test_patch, task.fail_to_pass),
        GOLD_PATCH=task.gold_patch.strip(),
    )
