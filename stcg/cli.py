"""python -m stcg <command>. See README.md for the full workflow."""

import argparse
import json
import sys
from datetime import datetime, timezone

from . import config


def _select(args):
    from .tasks import load_tasks
    from .validation import load_validation

    if args.set == "validation":
        tasks = load_validation(args.split)
    else:
        tasks = load_tasks(config.TASKS / f"{args.set}.jsonl")
    if args.source:
        tasks = [t for t in tasks if t.source in args.source.split(",")]
    if args.ids:
        wanted = set(args.ids.split(","))
        tasks = [t for t in tasks if t.instance_id in wanted or t.task_id in wanted]
    if args.limit:
        tasks = tasks[: args.limit]
    return tasks


def _guard_test_run(args) -> None:
    """Step 2.5: the test split is scored once, with a frozen prompt. Record every run; refuse repeats."""
    if args.set != "validation" or args.split != "test":
        return
    from .prompts import template_sha

    log_path = config.RESULTS / "test_runs.json"
    runs = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    if runs and not args.allow_test_rerun:
        sys.exit(f"The test split was already run ({runs[-1]}). Pass --allow-test-rerun to run it again, "
                 "and report that you did.")
    runs.append({"prompt": args.prompt, "prompt_sha": template_sha(args.prompt), "judges": args.judges,
                 "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")


def cmd_build(args):
    from .validation import build_all, make_split

    build_all()
    make_split()


def cmd_split(args):
    from .validation import make_split

    make_split(dev_fraction=args.dev_fraction, seed=args.seed)


def cmd_judge(args):
    from .judging import estimate, run_judges

    judges = args.judges.split(",")
    tasks = _select(args)
    print(estimate(tasks, judges, args.prompt))
    if args.dry_run:
        return
    _guard_test_run(args)
    run_judges(tasks, judges, args.prompt, workers=args.workers)
    if args.set == "validation":
        cmd_evaluate(args)


def cmd_evaluate(args):
    from .evaluate import evaluate
    from .judging import run_dir

    judges = args.judges.split(",")
    rep = evaluate(_select(args), judges, args.prompt, args.split if args.set == "validation" else args.set)
    t = rep["targets"]
    fmt = lambda x: "-" if x is None else f"{x:.0%}"
    print(f"\nrecall {fmt(t['recall'])} (>= {config.TARGET_RECALL:.0%}), "
          f"false flags {fmt(t['false_flag_rate'])} (<= {config.TARGET_FPR:.0%}): {'MET' if t['met'] else 'not met'}")
    print(f"Fleiss kappa: {rep['agreement']['fleiss_kappa']}")
    name = rep['split'] if judges == config.PANEL else f"{rep['split']}__{'+'.join(judges)}"
    print(f"report: {run_dir(args.prompt) / f'eval_{name}.md'}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="stcg", description="Spec-Test Coverage Gap judge pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="download sources, build Verified tasks + validation sets, make the split")

    s = sub.add_parser("split", help="assign new instances to dev/test (existing ones keep their side)")
    s.add_argument("--dev-fraction", type=float, default=config.DEV_FRACTION)
    s.add_argument("--seed", type=int, default=config.SEED)

    for name, help_ in (("judge", "run the judges (cached) and evaluate"), ("evaluate", "evaluate cached judgments")):
        j = sub.add_parser(name, help=help_)
        j.add_argument("--set", default="validation", help="validation | verified (any file in data/tasks/)")
        j.add_argument("--split", default="dev", choices=["dev", "test", "all"])
        j.add_argument("--source", help="comma-separated validation sources, e.g. agent_consensus,openai_excluded")
        j.add_argument("--ids", help="comma-separated instance or task ids")
        j.add_argument("--limit", type=int)
        j.add_argument("--judges", default=",".join(config.PANEL))
        j.add_argument("--prompt", default="judge_v1", help="prompt version in prompts/")
        if name == "judge":
            j.add_argument("--workers", type=int, default=4)
            j.add_argument("--dry-run", action="store_true", help="print the call/token estimate only")
            j.add_argument("--allow-test-rerun", action="store_true")

    args = p.parse_args(argv)
    {"build": cmd_build, "split": cmd_split,
     "judge": cmd_judge, "evaluate": cmd_evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()
