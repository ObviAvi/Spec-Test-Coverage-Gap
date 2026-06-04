# SWE-bench Test Case Analysis

This project provides tools to download and analyze the SWE-bench-verified dataset, specifically identifying newly added test cases versus pre-existing broken tests, and generating natural language descriptions of test behaviors using Google's Gemini AI.

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 3-step guide to get started immediately!

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google API key for Gemini AI:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```
Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Step 1: Download the Dataset

Run the download script to fetch the SWE-bench-verified dataset from HuggingFace and organize it into folders:

```bash
python download_swebench.py
```

This will create the following directory structure:
- `test_patches/` - Test patch diff files for each instance
- `fail_to_pass/` - JSON files containing FAIL_TO_PASS test lists
- `pass_to_pass/` - JSON files containing PASS_TO_PASS test lists
- `problem_statements/` - Markdown files with problem descriptions

### Step 2: Analyze Test Cases

Run the analysis script to identify newly added vs pre-existing test cases:

```bash
# Analyze all instances
python new_testcases.py

# Analyze a specific instance
python new_testcases.py django-14315
```

## Output

The analysis script will:
1. Parse the test patch to identify newly added test functions
2. Compare against the FAIL_TO_PASS test list
3. Categorize tests as either:
   - **Newly Added**: Tests that were added in the patch
   - **Pre-existing**: Tests that existed before but were broken

Example output:
```
================================================================================
Processing: django__django-14315
================================================================================

Total FAIL_TO_PASS tests: 11
  - Newly added: 1
  - Pre-existing: 10

--- NEWLY ADDED TEST CASES ---
  + test_runshell_use_environ (backends.base.test_client.SimpleDatabaseClientTests)

--- PRE-EXISTING BROKEN TEST CASES ---
  - test_settings_to_cmd_args_env (backends.base.test_client.SimpleDatabaseClientTests)
  - test_accent (dbshell.test_postgresql.PostgreSqlDbshellCommandTestCase)
  ...
```

### Step 3: Generate Summary Statistics (Optional)

Run the analysis script to get aggregate statistics across all instances:

```bash
python analyze_all.py
```

This will:
- Analyze all instances in the dataset
- Generate summary statistics
- Show top instances with most new/pre-existing tests
- Save detailed results to `analysis_results.json`

### Step 4: Generate Test Behavior Descriptions with Gemini AI

Use Gemini AI to automatically generate human-readable descriptions of what each test patch is checking:

```bash
# Analyze all test patches
python generate_test_descriptions.py

# Analyze a specific instance
python generate_test_descriptions.py django__django-14315

# Append to existing results
python generate_test_descriptions.py sphinx-doc__sphinx-9591 --append
```

This will:
- Analyze test patch(es) in `test_patches/`
- Use Google Gemini AI to understand what behavior each test verifies
- Generate concise, technical descriptions
- Save results to `test_descriptions.json`

Example output:
```json
{
  "sphinx-doc__sphinx-9591": "This patch tests that property type annotations in Python documentation are properly cross-referenced as pending_xref nodes rather than plain text, ensuring that type hints in @property decorators create clickable links to the referenced types.",
  
  "django__django-14315": "This patch verifies that the database client's runshell method correctly handles environment variables by passing None instead of an empty dictionary when no environment variables are needed, ensuring proper subprocess behavior."
}
```

**Working with Results:**
```bash
# View example usage and statistics
python example_usage.py

# Search for specific functionality
python -c "import json; d=json.load(open('test_descriptions.json')); print([k for k,v in d.items() if 'cross-reference' in v.lower()])"
```

See [USAGE.md](USAGE.md) for detailed documentation and advanced usage.

### Step 5: Judge Test Inferability (Optional)

Evaluate whether test behaviors could be predicted from the problem statements alone:

```bash
# Judge all test descriptions
python judge_test_inferability.py

# Judge a specific instance
python judge_test_inferability.py django__django-14315
```

This will:
- Read problem statements and test descriptions
- Use Gemini AI to judge if the test behavior is inferable from the issue
- Categorize each as:
  - **Directly specified**: Issue explicitly states this behavior
  - **Reasonably derivable**: Can be inferred from issue context
  - **Overspecified**: Test encodes implementation details not in the issue
- Save results to `inferability_judgments.json`

See [JUDGE_USAGE.md](JUDGE_USAGE.md) for detailed documentation.

### Step 6: Judge Implementation Specificity (Optional)

Analyze whether tests check "was the bug fixed?" or "was the bug fixed in this specific way?":

```bash
# Judge all instances
python judge_implementation_specificity.py

# Judge a specific instance
python judge_implementation_specificity.py django__django-14315
```

This will:
- Read problem statements and actual test patches (code)
- Use Gemini AI to determine if tests are bug-focused or implementation-specific
- Categorize each as:
  - **Bug-focused**: Tests validate the problem is solved (the WHAT)
  - **Implementation-specific**: Tests validate specific implementation choices (the HOW)
  - **Mixed**: Tests check both aspects
- Assign specificity score (1-5, where 1=purely bug-focused, 5=highly implementation-specific)
- Save results to `implementation_specificity.json`

Example output:
```json
{
  "django__django-14315": {
    "judgment": {
      "category": "bug_focused",
      "specificity_score": 2,
      "reasoning": "The test validates that environment variables are handled correctly, which directly addresses the reported issue without encoding unnecessary implementation details."
    }
  }
}
```

This helps identify tests that may be overly coupled to specific implementation choices rather than focusing on whether the bug is actually fixed.

## Files

### Main Scripts
- `download_swebench.py` - Downloads and organizes the SWE-bench-verified dataset
- `generate_test_descriptions.py` - **NEW!** Uses Gemini AI to analyze test patches and generate behavior descriptions
- `judge_test_inferability.py` - **NEW!** Judges whether test behaviors are inferable from problem statements
- `judge_implementation_specificity.py` - **NEW!** Judges whether tests check bug fixes or implementation specifics
- `example_usage.py` - **NEW!** Examples of working with generated test descriptions
- `new_testcases.py` - Analyzes test patches to identify new vs pre-existing tests
- `analyze_all.py` - Generates summary statistics across all instances

### Documentation
- `README.md` - This file
- `QUICKSTART.md` - **NEW!** Quick 3-step guide to get started
- `USAGE.md` - **NEW!** Detailed documentation for test description generation
- `requirements.txt` - Python dependencies

### Generated Data
- `test_patches/` - Test patch diff files
- `fail_to_pass/` - FAIL_TO_PASS test lists
- `pass_to_pass/` - PASS_TO_PASS test lists
- `problem_statements/` - Problem descriptions
- `test_descriptions.json` - **Generated** - AI-generated test behavior descriptions
- `inferability_judgments.json` - **Generated** - Judgments on whether tests are inferable from issues
- `implementation_specificity.json` - **Generated** - Judgments on bug-focused vs implementation-specific tests

## Dataset Information

The SWE-bench-verified dataset is sourced from:
- HuggingFace: `princeton-nlp/SWE-bench_Verified`
- Paper: [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)

## License

This project uses the SWE-bench-verified dataset which is licensed under MIT License.