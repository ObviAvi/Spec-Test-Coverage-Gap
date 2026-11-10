"""Paths, model defaults, and thresholds. Edit here, not in the modules."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"                  # downloaded sources (gitignored)
TASKS = DATA / "tasks"              # normalized benchmark task files
VALIDATION = DATA / "validation"    # Step 2 validation sets + split
PROMPTS = ROOT / "prompts"
RESULTS = ROOT / "results"

# One judge per model family (Step 1.2). Model IDs move fast; check them before a real run.
JUDGES = {
    "claude": {"provider": "anthropic", "model": "claude-opus-5-5", "effort": "high"},
    "gpt61": {"provider": "openai", "model": "gpt-6.1-sol", "reasoning_effort": "high"},
}
# The frozen panel the test split was scored with. Other judges are reported under a suffixed file name.
PANEL = ["claude", "gpt61"]

# A task is "flagged" (overspecified) when its label is >= this.
FLAG_THRESHOLD = 3
# Judges disagreeing by >= this many points mark the task uncertain (Step 1.3).
UNCERTAIN_SPREAD = 2

# Step 2.4 targets on the dev set.
TARGET_RECALL = 0.70
TARGET_FPR = 0.15

# Prompts longer than this are skipped and reported, never truncated.
MAX_PROMPT_CHARS = 400_000

# Validation-set construction.
SEED = 13
DEV_FRACTION = 0.4             # share of instances sampled into dev
CONSENSUS_TOP_SUBMISSIONS = 30 # "public agents" = top-N Verified submissions by resolve count
CONSENSUS_MIN_RESOLVE_RATE = 0.9
CONSENSUS_MAX_PATCH_SIMILARITY = 0.5  # mean pairwise Jaccard of changed lines
CONSENSUS_PATCHES_PER_TASK = 12

# Source URLs.
VERIFIED_HF = "princeton-nlp/SWE-bench_Verified"
FULL_HF = "princeton-nlp/SWE-bench"
PRO_HF = "ScaleAI/SWE-bench_Pro"
PRO_HF_CONFIG = "v1"  # the original 731 tasks, before the V2 refresh
PRO_VERIFIED_BASE = "https://huggingface.co/datasets/opencompass/SWEBench-Pro-Verified/resolve/main"
OPENAI_ANNOTATIONS_ZIP = "https://cdn.openai.com/introducing-swe-bench-verified/swe-bench-annotation-results.zip"
EXPERIMENTS_REPO = "SWE-bench/experiments"
SUBMISSIONS_BUCKET = "https://swe-bench-submissions.s3.amazonaws.com"
