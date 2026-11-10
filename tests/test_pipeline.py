import json

import pytest

from stcg import config, judging, metrics
from stcg.evaluate import evaluate
from stcg.prompts import render_judge_prompt
from stcg.tasks import Task, mark_fail_to_pass, parse_test_list, save_tasks
from stcg.validation import changed_lines, make_split, mean_jaccard

PATCH = """diff --git a/tests/test_x.py b/tests/test_x.py
--- a/tests/test_x.py
+++ b/tests/test_x.py
@@ -1,3 +1,6 @@
 def test_old():
     assert True
+def test_new_thing():
+    assert f() == 1
"""


def make_task(i, expected, source="src"):
    return Task(task_id=f"t/{i}", instance_id=f"inst-{i}", benchmark="b", problem_statement="Issue {x}",
                test_patch=PATCH, fail_to_pass=["tests/test_x.py::test_new_thing"],
                source=source, expected=expected)


def test_parse_test_list_formats():
    assert parse_test_list('["a", "b"]') == ["a", "b"]
    assert parse_test_list("['a', 'b']") == ["a", "b"]
    assert parse_test_list(["a"]) == ["a"]
    assert parse_test_list("") == []


def test_mark_fail_to_pass_only_tags_listed_tests():
    marked = mark_fail_to_pass(PATCH, ["tests/test_x.py::test_new_thing"])
    assert "+def test_new_thing():  # <-- FAIL_TO_PASS" in marked
    assert "test_old():  #" not in marked
    # django-style ids
    assert "FAIL_TO_PASS" in mark_fail_to_pass(PATCH, ["test_new_thing (tests.Cls)"])


def test_render_keeps_braces_and_pro_fields():
    t = make_task(1, "fine")
    t.requirements, t.interface = "Must return {a: 1}", "def f() -> int"
    prompt = render_judge_prompt(t, "judge_v1")
    assert "Issue {x}" in prompt and "Requirements:\nMust return {a: 1}" in prompt
    assert "Interface:\ndef f() -> int" in prompt and "{{" not in prompt
    with pytest.raises(ValueError):
        render_judge_prompt(t, "judge_v1_gold")
    t.gold_patch = "+return 1"
    assert "+return 1" in render_judge_prompt(t, "judge_v1_gold")
    assert "+return 1" not in render_judge_prompt(t, "judge_v1")


def test_cohen_kappa_known_values():
    T, F = True, False
    assert metrics.cohen_kappa([T, F, T, F], [T, F, T, F]) == pytest.approx(1.0)
    assert metrics.cohen_kappa([T, F, T, F], [F, T, F, T]) == pytest.approx(-1.0)
    # p_o = 0.75, p_e = 0.5
    assert metrics.cohen_kappa([T, T, F, F], [T, F, F, F]) == pytest.approx(0.5)


def test_fleiss_kappa():
    T, F = True, False
    assert metrics.fleiss_kappa([[T, T, T], [F, F, F], [T, T, T], [F, F, F]]) == pytest.approx(1.0)
    assert metrics.fleiss_kappa([[T, F, T]]) is not None
    assert metrics.fleiss_kappa([[T, F], [T, F, T]]) is None


def test_wilson_bounds():
    lo, hi = metrics.wilson(7, 10)
    assert 0.39 < lo < 0.40 and 0.89 < hi < 0.90


def test_changed_lines_ignores_new_files_and_whitespace():
    patch = ("diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-x =  1\n+x = 2\n"
             "diff --git a/repro.py b/repro.py\nnew file mode 100644\n--- /dev/null\n+++ b/repro.py\n@@ -0,0 +1 @@\n+print(1)\n")
    assert changed_lines(patch) == frozenset({"-x = 1", "+x = 2"})
    a, b = frozenset({"+a", "+b"}), frozenset({"+a", "+c"})
    assert mean_jaccard([a, a]) == 1.0 and mean_jaccard([a, b]) == pytest.approx(1 / 3)


def test_split_keeps_existing_assignments(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VALIDATION", tmp_path)
    save_tasks([make_task(i, "fine") for i in range(1, 11)], tmp_path / "agent_consensus.jsonl")
    first = make_split(dev_fraction=0.4)
    assert len(first["dev"]) == 4

    save_tasks([make_task(i, "fine") for i in range(1, 21)], tmp_path / "agent_consensus.jsonl")
    second = make_split(dev_fraction=0.4)
    assert set(first["dev"]) <= set(second["dev"]) and set(first["test"]) <= set(second["test"])
    assert len(second["dev"]) == 8  # 4 of the 10 new instances


def test_run_aggregate_evaluate_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RESULTS", tmp_path)
    monkeypatch.setattr(config, "PANEL", ["a", "b", "c"])
    tasks = [make_task(1, "overspecified", "other"), make_task(2, "fine", "other"),
             make_task(3, "overspecified"), make_task(4, "fine")]
    # per judge, scores in task order; task 4 gets a 1/3/4 spread -> uncertain
    plan = {"a": [4, 1, 3, 1], "b": [4, 2, 2, 3], "c": [3, 1, 3, 4]}

    def fake_client(judge):
        it = iter(plan[judge])

        class Fake:
            model = "fake"

            def complete_json(self, prompt, schema):
                return {"reasoning": "r", "score": next(it), "explanation": f"{judge} says",
                        "overspecification_vector": "v"}, {"served_model": "fake"}
        return Fake()

    monkeypatch.setattr(judging, "make_client", fake_client)
    judging.run_judges(tasks, list(plan), "judge_v1", workers=1)  # workers=1 keeps score order deterministic
    rows = {t.task_id: judging.aggregate(t, list(plan), "judge_v1") for t in tasks}
    assert rows["t/1"]["final"] == 4 and not rows["t/1"]["uncertain"]
    assert rows["t/3"]["final"] == 3 and rows["t/3"]["flagged"]
    assert rows["t/4"]["final"] == 3 and rows["t/4"]["uncertain"]

    rep = evaluate(tasks, list(plan), "judge_v1", "dev")
    assert rep["detection"]["ensemble"]["all"]["recall"]["rate"] == 1.0
    assert rep["detection"]["ensemble"]["all"]["false_flag_rate"]["rate"] == 0.5
    assert rep["detection"]["ensemble_certain_only"]["all"]["false_flag_rate"]["rate"] == 0.0
    assert rep["detection"]["ensemble"]["source:other"]["recall"]["rate"] == 1.0
    assert rep["agreement"]["pairwise"]["a~c"]["agree"] == 0.75  # 4 vs 3 on t/1 counts as agreement
    assert not rep["targets"]["met"]
    assert (tmp_path / "judge_v1" / "eval_dev.md").exists()

    # a second run hits the cache and makes no calls
    monkeypatch.setattr(judging, "make_client", lambda j: pytest.fail("should be cached"))
    judging.run_judges(tasks, list(plan), "judge_v1", workers=1)


def test_errors_are_retried_and_editing_a_prompt_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RESULTS", tmp_path)
    t = make_task(1, "fine")

    class Boom:
        model = "fake"

        def complete_json(self, prompt, schema):
            raise RuntimeError("rate limited")

    monkeypatch.setattr(judging, "make_client", lambda j: Boom())
    judging.run_judges([t], ["a"], "judge_v1", workers=1)
    assert "error" in judging.load_raw("judge_v1", "a", t.task_id)
    assert judging.aggregate(t, ["a"], "judge_v1")["final"] is None

    path = judging._raw_path("judge_v1", "a", t.task_id)
    rec = json.loads(path.read_text())
    rec.pop("error")
    rec["prompt_sha"] = "stale"
    path.write_text(json.dumps(rec))
    with pytest.raises(SystemExit):
        judging.run_judges([t], ["a"], "judge_v1", workers=1)
