"""Step 5: run SWE-bench Verified evaluations in the prebuilt task images, through the official harness."""

import hashlib
import io
import json
import re
import shutil
import tarfile
from functools import cache
from pathlib import Path

import docker
from swebench.harness import run_evaluation
from swebench.harness.constants import APPLY_PATCH_FAIL, END_TEST_OUTPUT, START_TEST_OUTPUT
from swebench.harness.utils import make_test_spec

from . import config

RUNS = config.RAW / "relax_runs"
run_evaluation.RUN_EVALUATION_LOG_DIR = RUNS / "logs"

# The harness writes patch.diff and eval.sh in text mode. On Windows that gives CRLF, which git and bash reject.
_write_text = Path.write_text
Path.write_text = lambda self, data, encoding=None, errors=None, newline="\n": _write_text(self, data, encoding, errors, newline)

RELAXED_EOF = "STCG_RELAXED_EOF"


@cache
def client() -> docker.DockerClient:
    return docker.from_env(timeout=600)


@cache
def eval_rows() -> dict[str, dict]:
    from datasets import load_dataset

    return {r["instance_id"]: r for r in load_dataset(config.VERIFIED_EVAL_HF, split="test")}


def _heredoc(script: str) -> tuple[list[str], int, int]:
    """The eval script as lines, with the indexes of the `git apply` line and of its heredoc terminator."""
    lines = script.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("git apply -v - <<"))
    end = lines.index(re.search(r"<<'(\w+)'", lines[start]).group(1), start)
    return lines, start, end


def relaxed_script(row: dict, new_files: dict[str, str]) -> str:
    """The task's eval script, overwriting the given test files right after the test patch is applied."""
    lines, _, end = _heredoc(row["eval_script"])
    extra = []
    for path, content in new_files.items():
        if RELAXED_EOF in content:
            raise ValueError(f"{path} contains the heredoc delimiter")
        extra += [f"cat > '{path}' <<'{RELAXED_EOF}'", content.removesuffix("\n"), RELAXED_EOF]
    return "\n".join(lines[: end + 1] + extra + lines[end + 1:])


def test_files(row: dict) -> dict[str, str]:
    """Contents of the files the test patch touches, after the patch is applied. Read from the task image."""
    cached = RUNS / "files" / f"{row['instance_id']}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    lines, start, end = _heredoc(row["eval_script"])
    prep = "\n".join(["cd /testbed", lines[start - 1], *lines[start: end + 1]]) + "\n"  # git checkout, git apply
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo("stcg_prep.sh")
        info.size = len(prep.encode("utf-8"))
        tar.addfile(info, io.BytesIO(prep.encode("utf-8")))
    container = client().containers.run(row["image"], "tail -f /dev/null", detach=True, user="root")
    try:
        container.put_archive("/tmp", buf.getvalue())
        res = container.exec_run("bash /tmp/stcg_prep.sh")
        if res.exit_code != 0:
            raise RuntimeError(f"test patch did not apply: {res.output.decode(errors='replace')[-500:]}")
        files = {}
        for path in re.findall(r"^\+\+\+ b/(.+)$", row["test_patch"], flags=re.M):
            out = container.exec_run(["cat", path], workdir="/testbed")
            try:
                files[path] = out.output.decode("utf-8")
            except UnicodeDecodeError:
                pass  # binary fixture: not editable
    finally:
        container.remove(force=True)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(files), encoding="utf-8")
    return files


def _log_dir(key: str, instance_id: str) -> Path:
    return RUNS / "logs" / key / "p" / instance_id


def run(row: dict, patch: str | None, eval_script: str | None = None, tries: int = 2) -> dict:
    """One evaluation of `patch` (None = the unpatched repo) under the task's eval script or a replacement.

    Returns resolved + the failing FAIL_TO_PASS and PASS_TO_PASS tests. `unparsed` means the tests ran but gave no
    readable results (for example a syntax error in a test file). `apply_failed` means the patch does not apply
    to the repo in the image. `error` means the run itself failed (Docker, timeout); those are never cached, so
    the next call retries them.
    """
    script = eval_script or row["eval_script"]
    iid = row["instance_id"]
    if patch and not patch.endswith("\n"):
        patch += "\n"  # some submissions publish the patch without its final newline, and then it does not apply
    key = hashlib.sha1(f"{script}\0{patch}".encode("utf-8")).hexdigest()[:16]
    spec = make_test_spec({**row, "eval_script": script})
    pred = {"instance_id": iid, "model_name_or_path": "p", "model_patch": patch or ""}
    no_apply = _log_dir(key, iid) / "apply_failed"
    if no_apply.exists():
        return {"key": key, "resolved": False, "apply_failed": True, "f2p_failed": [], "p2p_failed": []}
    for _ in range(tries):
        try:
            out = run_evaluation.run_instance(spec, pred, client(), key, timeout=config.RUN_TIMEOUT,
                                              skip_patch=patch is None)
        except Exception:  # the harness catches most errors itself and returns None
            out = None
        if out:
            rep = out[1][iid]
            if "tests_status" not in rep:
                return {"key": key, "resolved": False, "unparsed": True, "f2p_failed": [], "p2p_failed": []}
            ts = rep["tests_status"]
            return {"key": key, "resolved": rep["resolved"],
                    "f2p_failed": ts["FAIL_TO_PASS"]["failure"], "p2p_failed": ts["PASS_TO_PASS"]["failure"]}
        log = _log_dir(key, iid) / "run_instance.log"
        if log.exists() and APPLY_PATCH_FAIL in log.read_text(encoding="utf-8", errors="replace"):
            no_apply.write_text("", encoding="utf-8")  # deterministic: remember it instead of retrying
            return {"key": key, "resolved": False, "apply_failed": True, "f2p_failed": [], "p2p_failed": []}
        shutil.rmtree(_log_dir(key, iid), ignore_errors=True)
    return {"key": key, "error": True}


def output_tail(key: str, instance_id: str, chars: int = 5000) -> str:
    path = _log_dir(key, instance_id) / "test_output.txt"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if START_TEST_OUTPUT in text:
        text = text.split(START_TEST_OUTPUT, 1)[1].split(END_TEST_OUTPUT, 1)[0]
    return text[-chars:]


def remove_image(row: dict) -> None:
    try:
        client().images.remove(row["image"], force=True)
    except docker.errors.APIError:
        pass
