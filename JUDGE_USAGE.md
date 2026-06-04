# Test Inferability Judge - Usage Guide

This guide explains how to use the `judge_test_inferability.py` script to evaluate whether test behaviors could be predicted from problem statements alone.

## Overview

The judge analyzes pairs of (problem statement, test description) and determines if a competent developer could predict the test behavior from reading only the issue report, without seeing any test code.

## Categories

The judge assigns one of three categories:

1. **Directly specified**: The issue explicitly states this expected behavior
2. **Reasonably derivable**: A careful reader could infer this behavior from the issue context
3. **Overspecified**: The test encodes an implementation choice not suggested by the issue

## Prerequisites

1. **Test descriptions generated**: Run `generate_test_descriptions.py` first
2. **Problem statements downloaded**: Run `download_swebench.py` first
3. **Google API Key**: Set `GOOGLE_API_KEY` environment variable

## Usage

### Judge All Instances

```bash
python judge_test_inferability.py
```

This will:
- Load all test descriptions from `test_descriptions.json`
- Read corresponding problem statements from `problem_statements/`
- Judge each pair using Gemini AI
- Save results to `inferability_judgments.json`

### Judge Specific Instance

```bash
python judge_test_inferability.py django__django-14315
```

### Custom Input/Output Files

```bash
python judge_test_inferability.py --input my_tests.json --output my_judgments.json
```

## Command Line Options

```
usage: judge_test_inferability.py [-h] [-i INPUT] [-o OUTPUT] [instance_id]

Judge whether test behaviors are inferable from problem statements

positional arguments:
  instance_id           Specific instance ID to judge (e.g., django__django-14315).
                        If not provided, judges all instances.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input JSON file with test descriptions (default: test_descriptions.json)
  -o OUTPUT, --output OUTPUT
                        Output JSON file path (default: inferability_judgments.json)

Examples:
  # Judge all test descriptions
  python judge_test_inferability.py
  
  # Judge a specific instance
  python judge_test_inferability.py django__django-14315
  
  # Use custom input/output files
  python judge_test_inferability.py --input my_tests.json --output my_judgments.json
```

## Example Output

### Console Output

```
================================================================================
Test Inferability Judge with Gemini AI
================================================================================

Mode: Judging all instances

Setting up Gemini AI...
✓ Gemini AI configured

Loading test descriptions from test_descriptions.json...
✓ Loaded 200 test description(s)

[1/200] Judging sphinx-doc__sphinx-9591...
    → Category: directly_specified
    → The issue explicitly mentions that property type annotations should be cross-referenced...

[2/200] Judging django__django-14315...
    → Category: reasonably_derivable
    → While not explicitly stated, the subprocess environment handling convention is...

...

================================================================================
JUDGMENT COMPLETE
================================================================================
Total instances: 200
Successfully judged: 195
Missing problem statements: 3
Errors: 2

================================================================================
JUDGMENT STATISTICS
================================================================================
Total instances judged: 195

Breakdown by category:
  directly_specified: 89 (45.6%)
  reasonably_derivable: 78 (40.0%)
  overspecified: 28 (14.4%)

✓ Results saved to inferability_judgments.json
```

### JSON Output Format

The output file contains:

```json
{
  "instance_id": {
    "test_description": "Description of what the test checks...",
    "judgment": {
      "category": "directly_specified | reasonably_derivable | overspecified",
      "reasoning": "Explanation of why this category was chosen...",
      "raw_response": "Full response from Gemini..."
    }
  }
}
```

## Example Judgments

### Directly Specified

```json
{
  "sphinx-doc__sphinx-9591": {
    "test_description": "This patch tests that property type annotations in Python documentation are properly cross-referenced as pending_xref nodes...",
    "judgment": {
      "category": "directly_specified",
      "reasoning": "The issue explicitly states that 'A documented type in property's type annotation does not get cross-referenced' and shows examples of properties with type annotations that should be cross-referenced. The test directly verifies this stated requirement."
    }
  }
}
```

### Reasonably Derivable

```json
{
  "django__django-14315": {
    "test_description": "This patch verifies that the database client's runshell method correctly handles environment variables by passing None instead of an empty dictionary...",
    "judgment": {
      "category": "reasonably_derivable",
      "reasoning": "While the issue doesn't explicitly specify None vs empty dict, a competent developer familiar with subprocess conventions would understand that None is the proper way to indicate 'use parent environment' rather than an empty dict."
    }
  }
}
```

### Overspecified

```json
{
  "matplotlib__matplotlib-12345": {
    "test_description": "This patch tests that the internal cache uses a specific data structure (OrderedDict) with a maximum size of 128 entries...",
    "judgment": {
      "category": "overspecified",
      "reasoning": "The issue mentions caching behavior but doesn't specify implementation details like the exact data structure or cache size. These are implementation choices that go beyond what the issue requires."
    }
  }
}
```

## Analyzing Results

### Load and Analyze

```python
import json

# Load judgments
with open('inferability_judgments.json', 'r') as f:
    judgments = json.load(f)

# Count by category
categories = {}
for instance_id, data in judgments.items():
    if 'judgment' in data:
        cat = data['judgment']['category']
        categories[cat] = categories.get(cat, 0) + 1

print(categories)
```

### Filter by Category

```python
# Get all overspecified tests
overspecified = {
    k: v for k, v in judgments.items()
    if 'judgment' in v and v['judgment']['category'] == 'overspecified'
}

print(f"Found {len(overspecified)} overspecified tests")
for instance_id in list(overspecified.keys())[:5]:
    print(f"  - {instance_id}")
```

### Export to CSV

```python
import csv

with open('judgments.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Instance ID', 'Category', 'Reasoning'])
    
    for instance_id, data in judgments.items():
        if 'judgment' in data:
            writer.writerow([
                instance_id,
                data['judgment']['category'],
                data['judgment']['reasoning']
            ])
```

## Understanding the Categories

### Directly Specified
- The issue explicitly mentions the expected behavior
- Test validates exactly what the issue describes
- Example: "The function should return None when..." → test checks it returns None

### Reasonably Derivable
- Not explicitly stated but logically follows from the issue
- Requires domain knowledge or understanding of conventions
- Example: Issue mentions "fix crash" → test checks no exception is raised

### Overspecified
- Test checks implementation details not mentioned in the issue
- Goes beyond what's necessary to fix the reported problem
- Example: Issue says "improve performance" → test checks specific algorithm used

## Tips for Interpretation

1. **Context Matters**: Some behaviors may seem overspecified but are actually standard conventions in that domain

2. **Multiple Behaviors**: A single test may check multiple things - the judgment considers the overall test behavior

3. **Edge Cases**: Tests for edge cases are usually "reasonably derivable" if the issue implies they should be handled

4. **Implementation Details**: Checking specific data structures, algorithms, or internal state is usually "overspecified"

## Troubleshooting

### "test_descriptions.json not found"
Run `generate_test_descriptions.py` first to create test descriptions.

### "Problem statement not found"
Some instances may not have problem statements. The script will skip these and note them in the output.

### Rate Limiting
If you hit Gemini API rate limits:
- Wait a few minutes
- Process instances in smaller batches using the instance_id argument
- The free tier allows 15 requests/minute

### Inconsistent Judgments
The AI may occasionally produce inconsistent judgments. For critical analysis:
- Review the reasoning provided
- Consider running multiple times and comparing results
- Manually review edge cases

## Cost Considerations

- Uses Gemini 1.5 Flash (free tier: 15 requests/minute)
- Each judgment is one API call
- For 200 instances: ~200 API calls, typically completes in 15-20 minutes
- Well within free tier limits

## Advanced Usage

### Batch Processing

Process in chunks to avoid rate limits:

```bash
# Get list of instances
python -c "import json; print('\n'.join(json.load(open('test_descriptions.json')).keys()))" > instances.txt

# Process in batches
for instance in $(head -50 instances.txt); do
    python judge_test_inferability.py "$instance" --append
    sleep 0.5
done
```

### Custom Analysis

Modify the prompt in `judge_inferability()` function to:
- Add more categories
- Change evaluation criteria
- Include additional context

## Related Scripts

- `generate_test_descriptions.py` - Generate test descriptions (prerequisite)
- `download_swebench.py` - Download problem statements (prerequisite)
- `example_usage.py` - Examples of working with the data