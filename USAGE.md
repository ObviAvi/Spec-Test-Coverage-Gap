# Test Patch Analysis with Gemini AI

This guide explains how to use the `generate_test_descriptions.py` script to analyze SWE-bench test patches using Google's Gemini AI.

## Overview

The script analyzes test patches from the SWE-bench-verified dataset and uses Gemini AI to generate human-readable descriptions of what new behavior each test is checking.

## Prerequisites

1. **Python 3.8+** installed
2. **Google API Key** for Gemini AI
   - Get one at: https://makersuite.google.com/app/apikey
3. **Dependencies** installed (see Installation below)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install datasets>=2.14.0
pip install unidiff>=0.7.5
pip install google-generativeai>=0.3.0
```

2. Set up your Google API key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.):
```bash
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Step 1: Download SWE-bench Data (if not already done)

```bash
python download_swebench.py
```

This will create the following directories:
- `test_patches/` - Test patch diff files
- `fail_to_pass/` - FAIL_TO_PASS test lists
- `pass_to_pass/` - PASS_TO_PASS test lists
- `problem_statements/` - Problem descriptions

### Step 2: Run the Analysis

**Analyze all test patches:**
```bash
python generate_test_descriptions.py
```

**Analyze a specific instance:**
```bash
python generate_test_descriptions.py django__django-14315
```

**Analyze and append to existing results:**
```bash
python generate_test_descriptions.py sphinx-doc__sphinx-9591 --append
```

**Use custom output file:**
```bash
python generate_test_descriptions.py --output my_results.json
```

The script will:
1. Find test patch(es) in `test_patches/`
2. Analyze using Gemini AI
3. Generate descriptions of what behavior is being tested
4. Save results to JSON file (default: `test_descriptions.json`)

### Step 3: View Results

The results are saved in `test_descriptions.json` with the format:
```json
{
  "instance-id": "Description of what the test checks...",
  "another-instance": "Another description..."
}
```

## Example Output

**Analyzing all patches:**
```
================================================================================
SWE-bench Test Patch Analyzer with Gemini AI
================================================================================

Mode: Analyzing all instances

Setting up Gemini AI...
✓ Gemini AI configured

Finding test patches...
✓ Found 200 test patches

[1/200] Analyzing sphinx-doc__sphinx-9591...
    → This patch tests that property type annotations in Python documentation are properly cross-referenced...

[2/200] Analyzing django__django-14315...
    → This patch verifies that the database client's runshell method correctly handles environment variables...

...

================================================================================
ANALYSIS COMPLETE
================================================================================
Total patches analyzed: 200
Successful: 198
Errors: 2

✓ Results saved to test_descriptions.json
```

**Analyzing a specific instance:**
```
================================================================================
SWE-bench Test Patch Analyzer with Gemini AI
================================================================================

Mode: Analyzing specific instance 'django__django-14315'

Setting up Gemini AI...
✓ Gemini AI configured

Finding test patches...
✓ Found 1 test patch(es)

[1/1] Analyzing django__django-14315...
    → This patch verifies that the database client's runshell method correctly handles environment variables...

================================================================================
ANALYSIS COMPLETE
================================================================================
Total patches analyzed: 1
Successful: 1
Errors: 0

✓ Results saved to test_descriptions.json

================================================================================
RESULTS
================================================================================

1. django__django-14315
   This patch verifies that the database client's runshell method correctly handles environment variables by passing None instead of an empty dictionary when no environment variables are needed, ensuring proper subprocess behavior.
```

## Sample Descriptions

Here are examples of the kind of descriptions the script generates:

**sphinx-doc__sphinx-9591:**
> "This patch tests that property type annotations in Python documentation are properly cross-referenced as pending_xref nodes rather than plain text, ensuring that type hints in @property decorators create clickable links to the referenced types."

**django__django-14315:**
> "This patch verifies that the database client's runshell method correctly handles environment variables by passing None instead of an empty dictionary when no environment variables are needed, ensuring proper subprocess behavior."

## Command Line Options

```
usage: generate_test_descriptions.py [-h] [-o OUTPUT] [-a] [instance_id]

Analyze SWE-bench test patches using Gemini AI

positional arguments:
  instance_id           Specific instance ID to analyze (e.g., django__django-14315).
                        If not provided, analyzes all instances.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output JSON file path (default: test_descriptions.json)
  -a, --append          Append results to existing output file instead of overwriting

Examples:
  # Analyze all test patches
  python generate_test_descriptions.py
  
  # Analyze a specific instance
  python generate_test_descriptions.py django__django-14315
  
  # Analyze specific instance and append to existing results
  python generate_test_descriptions.py sphinx-doc__sphinx-9591 --append
  
  # Use custom output file
  python generate_test_descriptions.py --output my_results.json
```

## Customization

You can modify the script to:

1. **Change the AI model**: Edit line 42 to use a different Gemini model
   ```python
   model = genai.GenerativeModel('gemini-1.5-pro')  # More powerful but slower
   ```

2. **Adjust the prompt**: Modify the `analyze_test_patch()` function to change how the AI analyzes patches

3. **Change output format**: Modify `save_results()` to save in different formats (CSV, Markdown, etc.)

## Troubleshooting

### "GOOGLE_API_KEY environment variable not set"
- Make sure you've exported your API key: `export GOOGLE_API_KEY='your-key'`
- Check it's set: `echo $GOOGLE_API_KEY`

### "test_patches/ directory not found"
- Run `python download_swebench.py` first to download the data

### Rate limiting or quota errors
- Gemini has rate limits. The script processes patches sequentially to avoid hitting limits
- If you hit limits, wait a few minutes and run again
- Consider using `gemini-1.5-flash` (default) instead of `gemini-1.5-pro` for better rate limits

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Activate your virtual environment if using one

## Cost Considerations

- **Gemini 1.5 Flash** (default): Free tier includes 15 requests per minute, 1 million tokens per day
- **Gemini 1.5 Pro**: More powerful but has lower rate limits
- For 200 patches, expect to use approximately 200-400K tokens total
- Check current pricing at: https://ai.google.dev/pricing

## Advanced Usage

### Analyze specific patches only

Modify the script to filter patches:
```python
# In get_all_test_patches(), add filtering:
patches = sorted(test_patches_dir.glob('django*-test-patch.diff'))  # Only Django
```

### Resume from interruption

The script processes sequentially. If interrupted, you can modify it to skip already-processed instances by checking the output file.

### Batch processing with delays

Add delays between requests to avoid rate limits:
```python
import time
# After each analysis:
time.sleep(1)  # Wait 1 second between requests
```

## Output Schema

The `test_descriptions.json` file contains:
```json
{
  "instance_id": "string - description of test behavior",
  ...
}
```

Each description follows the format:
- Starts with "This patch tests that..." or similar
- Describes the specific functionality being tested
- Mentions expected behavior
- Notes any edge cases or scenarios

## License

This script is provided as-is for analyzing SWE-bench data.