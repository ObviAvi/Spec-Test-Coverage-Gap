# Quick Start Guide

Get up and running with test patch analysis in 3 simple steps!

## Prerequisites

- Python 3.8 or higher
- Google API key for Gemini AI ([Get one here](https://makersuite.google.com/app/apikey))

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Your API Key

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

## Step 3: Run the Analysis

```bash
# If you haven't downloaded the data yet:
python download_swebench.py

# Analyze all test patches:
python generate_test_descriptions.py

# OR analyze just one specific instance:
python generate_test_descriptions.py django__django-14315
```

That's it! Results will be saved to `test_descriptions.json`.

## What You Get

The script analyzes each test patch and generates descriptions like:

```json
{
  "sphinx-doc__sphinx-9591": "This patch tests that property type annotations in Python documentation are properly cross-referenced as pending_xref nodes rather than plain text, ensuring that type hints in @property decorators create clickable links to the referenced types.",
  
  "django__django-14315": "This patch verifies that the database client's runshell method correctly handles environment variables by passing None instead of an empty dictionary when no environment variables are needed, ensuring proper subprocess behavior."
}
```

## View and Use Results

```bash
# See example usage and statistics:
python example_usage.py

# View the JSON:
cat test_descriptions.json | python -m json.tool | less

# Get help on all options:
python generate_test_descriptions.py --help
```

## Next Steps

- **Judge test inferability**: `python judge_test_inferability.py` (see [JUDGE_USAGE.md](JUDGE_USAGE.md))
- Read [USAGE.md](USAGE.md) for detailed documentation on test description generation
- Customize the analysis prompt in `generate_test_descriptions.py`
- Use `example_usage.py` to filter and export specific results

## Troubleshooting

**"GOOGLE_API_KEY not set"**
```bash
export GOOGLE_API_KEY='your-key'
echo $GOOGLE_API_KEY  # Verify it's set
```

**"test_patches/ directory not found"**
```bash
python download_swebench.py  # Download the data first
```

**Rate limiting**
- Wait a few minutes and try again
- The script uses Gemini 1.5 Flash which has generous free tier limits

## Cost

- **Free tier**: 15 requests/minute, 1M tokens/day
- **For ~200 patches**: Typically uses 200-400K tokens (well within free tier)
- Check pricing: https://ai.google.dev/pricing

---

Need help? Check [USAGE.md](USAGE.md) for detailed documentation.