#!/usr/bin/env python3
"""
Analyze SWE-bench test patches using Gemini AI to determine what new behavior is being tested.

This script:
1. Reads all test patch files from test_patches/
2. Uses Google Gemini AI to analyze each patch
3. Generates a description of what new behavior is being tested
4. Saves results to a JSON file
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import google.generativeai as genai


def setup_gemini(api_key: Optional[str] = None) -> genai.GenerativeModel:
    """
    Setup Gemini AI with API key.
    
    Args:
        api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
    
    Returns:
        Configured Gemini model
    """
    if api_key is None:
        api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set!")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    # Use Gemini 1.5 Flash for fast, cost-effective analysis
    model = genai.GenerativeModel('gemini-2.5-flash')
    return model


def read_test_patch(filepath: str) -> str:
    """Read test patch file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_test_patch(model: genai.GenerativeModel, patch_content: str, instance_id: str) -> str:
    """
    Use Gemini to analyze a test patch and determine what new behavior is being tested.
    
    Args:
        model: Gemini model instance
        patch_content: The diff content of the test patch
        instance_id: The instance ID for context
    
    Returns:
        Description of what new behavior is being tested
    """
    prompt = f"""You are analyzing a test patch from the SWE-bench dataset

The test patch shows changes to test files that verify a bug fix or new feature. Your task is to analyze the patch and describe what NEW BEHAVIOR is being tested.

Here is the test patch:

```diff
{patch_content}
```

Please provide a concise, technical description of what new behavior this test is checking. Focus on:
1. What specific functionality is now being tested
2. What the test expects to happen
3. What edge cases or scenarios are being validated

Format your response as a single natural language paragraph"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: Failed to analyze patch - {str(e)}"


def get_all_test_patches(instance_id: Optional[str] = None) -> List[str]:
    """
    Get list of test patch files.
    
    Args:
        instance_id: If provided, only return the patch for this instance.
                    Otherwise, return all patches.
    
    Returns:
        List of patch file paths
    """
    test_patches_dir = Path('test_patches')
    if not test_patches_dir.exists():
        print("ERROR: test_patches/ directory not found!")
        sys.exit(1)
    
    if instance_id:
        # Look for specific instance
        patch_file = test_patches_dir / f"{instance_id}-test-patch.diff"
        if not patch_file.exists():
            print(f"ERROR: Test patch not found for instance '{instance_id}'")
            print(f"Expected file: {patch_file}")
            sys.exit(1)
        return [str(patch_file)]
    else:
        # Return all patches
        patches = sorted(test_patches_dir.glob('*-test-patch.diff'))
        return [str(p) for p in patches]


def extract_instance_id(filepath: str) -> str:
    """Extract instance ID from filepath."""
    filename = Path(filepath).name
    # Remove '-test-patch.diff' suffix
    return filename.replace('-test-patch.diff', '')


def save_results(results: Dict[str, str], output_file: str = 'test_descriptions.json', append: bool = False):
    """
    Save analysis results to JSON file.
    
    Args:
        results: Dictionary of instance_id -> description
        output_file: Path to output JSON file
        append: If True and file exists, merge with existing results
    """
    if append and Path(output_file).exists():
        # Load existing results and merge
        with open(output_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        existing.update(results)
        results = existing
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to {output_file}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze SWE-bench test patches using Gemini AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all test patches
  python generate_test_descriptions.py
  
  # Analyze a specific instance
  python generate_test_descriptions.py django__django-14315
  
  # Analyze specific instance and append to existing results
  python generate_test_descriptions.py sphinx-doc__sphinx-9591 --append
  
  # Use custom output file
  python generate_test_descriptions.py --output my_results.json
        """
    )
    parser.add_argument(
        'instance_id',
        nargs='?',
        help='Specific instance ID to analyze (e.g., django__django-14315). If not provided, analyzes all instances.'
    )
    parser.add_argument(
        '-o', '--output',
        default='test_descriptions.json',
        help='Output JSON file path (default: test_descriptions.json)'
    )
    parser.add_argument(
        '-a', '--append',
        action='store_true',
        help='Append results to existing output file instead of overwriting'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    print("="*80)
    print("SWE-bench Test Patch Analyzer with Gemini AI")
    print("="*80)
    print()
    
    if args.instance_id:
        print(f"Mode: Analyzing specific instance '{args.instance_id}'")
    else:
        print("Mode: Analyzing all instances")
    print()
    
    # Setup Gemini
    print("Setting up Gemini AI...")
    model = setup_gemini()
    print("✓ Gemini AI configured\n")
    
    # Get test patches
    print("Finding test patches...")
    patch_files = get_all_test_patches(args.instance_id)
    print(f"✓ Found {len(patch_files)} test patch(es)\n")
    
    # Analyze each patch
    results = {}
    errors = []
    
    for idx, patch_file in enumerate(patch_files, 1):
        instance_id = extract_instance_id(patch_file)
        print(f"[{idx}/{len(patch_files)}] Analyzing {instance_id}...")
        
        try:
            # Read patch content
            patch_content = read_test_patch(patch_file)
            
            # Analyze with Gemini
            description = analyze_test_patch(model, patch_content, instance_id)
            
            # Store result
            results[instance_id] = description
            
            # Print preview
            preview = description[:100] + "..." if len(description) > 100 else description
            print(f"    → {preview}\n")
            
            # Check for errors
            if description.startswith("ERROR:"):
                errors.append(instance_id)
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            results[instance_id] = error_msg
            errors.append(instance_id)
            print(f"    → {error_msg}\n")
    
    # Save results
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"Total patches analyzed: {len(patch_files)}")
    print(f"Successful: {len(patch_files) - len(errors)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nInstances with errors:")
        for instance_id in errors:
            print(f"  - {instance_id}")
    
    save_results(results, args.output, args.append)
    
    # Print results
    print("\n" + "="*80)
    if len(results) <= 3:
        print("RESULTS")
        print("="*80)
        for idx, (instance_id, description) in enumerate(results.items(), 1):
            print(f"\n{idx}. {instance_id}")
            print(f"   {description}")
    else:
        print("SAMPLE RESULTS (first 3)")
        print("="*80)
        for idx, (instance_id, description) in enumerate(list(results.items())[:3], 1):
            print(f"\n{idx}. {instance_id}")
            print(f"   {description}")


if __name__ == "__main__":
    main()

# Made with Bob
