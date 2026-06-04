#!/usr/bin/env python3
"""
Judge whether test behaviors are inferable from problem statements.

This script:
1. Reads problem statements and test descriptions
2. Uses Gemini AI to judge if the test behavior is inferable from the issue
3. Categorizes as: directly specified, reasonably derivable, or overspecified
4. Saves results to a JSON file
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
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


def read_problem_statement(instance_id: str) -> Optional[str]:
    """Read problem statement for an instance."""
    filepath = Path('problem_statements') / f"{instance_id}.md"
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Remove the header line with instance ID
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            return '\n'.join(lines[2:])  # Skip header and empty line
        return content


def load_test_descriptions(filepath: str = 'test_descriptions.json') -> Dict[str, str]:
    """Load test descriptions from JSON file."""
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found!")
        print("Please run: python generate_test_descriptions.py")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def judge_inferability(model: genai.GenerativeModel, problem_statement: str, 
                       test_description: str, instance_id: str) -> Dict[str, str]:
    """
    Use Gemini to judge if test behavior is inferable from the problem statement.
    
    Args:
        model: Gemini model instance
        problem_statement: The issue/problem description
        test_description: Description of what the test checks
        instance_id: The instance ID for context
    
    Returns:
        Dictionary with 'category' and 'reasoning'
    """
    prompt = f"""You are a judge evaluating whether a test behavior could be predicted from an issue report.

**ISSUE REPORT:**
{problem_statement}

**TEST BEHAVIOR:**
{test_description}

**YOUR TASK:**
Given ONLY the issue report above (without seeing any test code), determine if a competent developer could predict that a correct fix must satisfy the specific test behavior described.

**CATEGORIES:**
1. **Directly specified**: The issue explicitly states this expected behavior
2. **Reasonably derivable**: A careful reader could infer this behavior from the issue context
3. **Overspecified**: The test encodes an implementation choice not suggested by the issue

**INSTRUCTIONS:**
- You must choose exactly ONE category
- Provide clear reasoning for your choice
- Focus on whether the SPECIFIC behavior tested is predictable from the issue
- Consider what a competent developer would reasonably infer

**RESPONSE FORMAT:**
Category: [directly specified | reasonably derivable | overspecified]
Reasoning: [Your explanation in 2-3 sentences]

Your response:"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse the response
        lines = text.split('\n')
        category = None
        reasoning = None
        
        for line in lines:
            if line.startswith('Category:'):
                category_text = line.replace('Category:', '').strip().lower()
                # Normalize category
                if 'directly' in category_text or 'explicit' in category_text:
                    category = 'directly_specified'
                elif 'derivable' in category_text or 'inferable' in category_text:
                    category = 'reasonably_derivable'
                elif 'overspecified' in category_text or 'over-specified' in category_text:
                    category = 'overspecified'
            elif line.startswith('Reasoning:'):
                reasoning = line.replace('Reasoning:', '').strip()
        
        # If reasoning spans multiple lines, capture it
        if reasoning and len(lines) > 2:
            reasoning_start = False
            full_reasoning = []
            for line in lines:
                if line.startswith('Reasoning:'):
                    reasoning_start = True
                    full_reasoning.append(line.replace('Reasoning:', '').strip())
                elif reasoning_start and line.strip():
                    full_reasoning.append(line.strip())
            if full_reasoning:
                reasoning = ' '.join(full_reasoning)
        
        if not category:
            category = 'unknown'
            reasoning = f"Failed to parse category from response: {text}"
        
        return {
            'category': category,
            'reasoning': reasoning or "No reasoning provided",
            'raw_response': text
        }
    
    except Exception as e:
        return {
            'category': 'error',
            'reasoning': f"Failed to analyze: {str(e)}",
            'raw_response': ''
        }


def save_results(results: Dict[str, Dict], output_file: str = 'inferability_judgments.json'):
    """Save judgment results to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to {output_file}")


def print_statistics(results: Dict[str, Dict]):
    """Print statistics about the judgments."""
    categories = {}
    for instance_id, result in results.items():
        if 'judgment' in result:
            cat = result['judgment']['category']
            categories[cat] = categories.get(cat, 0) + 1
    
    print("\n" + "="*80)
    print("JUDGMENT STATISTICS")
    print("="*80)
    print(f"Total instances judged: {len(results)}")
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Judge whether test behaviors are inferable from problem statements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Judge all test descriptions
  python judge_test_inferability.py
  
  # Judge a specific instance
  python judge_test_inferability.py django__django-14315
  
  # Use custom input/output files
  python judge_test_inferability.py --input my_tests.json --output my_judgments.json
        """
    )
    parser.add_argument(
        'instance_id',
        nargs='?',
        help='Specific instance ID to judge (e.g., django__django-14315). If not provided, judges all instances.'
    )
    parser.add_argument(
        '-i', '--input',
        default='test_descriptions.json',
        help='Input JSON file with test descriptions (default: test_descriptions.json)'
    )
    parser.add_argument(
        '-o', '--output',
        default='inferability_judgments.json',
        help='Output JSON file path (default: inferability_judgments.json)'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    print("="*80)
    print("Test Inferability Judge with Gemini AI")
    print("="*80)
    print()
    
    if args.instance_id:
        print(f"Mode: Judging specific instance '{args.instance_id}'")
    else:
        print("Mode: Judging all instances")
    print()
    
    # Setup Gemini
    print("Setting up Gemini AI...")
    model = setup_gemini()
    print("✓ Gemini AI configured\n")
    
    # Load test descriptions
    print(f"Loading test descriptions from {args.input}...")
    test_descriptions = load_test_descriptions(args.input)
    
    # Filter to specific instance if requested
    if args.instance_id:
        if args.instance_id not in test_descriptions:
            print(f"ERROR: Instance '{args.instance_id}' not found in {args.input}")
            sys.exit(1)
        test_descriptions = {args.instance_id: test_descriptions[args.instance_id]}
    
    print(f"✓ Loaded {len(test_descriptions)} test description(s)\n")
    
    # Judge each instance
    results = {}
    errors = []
    missing_problems = []
    
    for idx, (instance_id, test_desc) in enumerate(test_descriptions.items(), 1):
        print(f"[{idx}/{len(test_descriptions)}] Judging {instance_id}...")
        
        # Read problem statement
        problem_statement = read_problem_statement(instance_id)
        if not problem_statement:
            print(f"    ⚠ Problem statement not found, skipping\n")
            missing_problems.append(instance_id)
            results[instance_id] = {
                'test_description': test_desc,
                'error': 'Problem statement not found'
            }
            continue
        
        try:
            # Judge inferability
            judgment = judge_inferability(model, problem_statement, test_desc, instance_id)
            
            # Store result
            results[instance_id] = {
                'test_description': test_desc,
                'judgment': judgment
            }
            
            # Print result
            category = judgment['category']
            reasoning_preview = judgment['reasoning'][:80] + "..." if len(judgment['reasoning']) > 80 else judgment['reasoning']
            print(f"    → Category: {category}")
            print(f"    → {reasoning_preview}\n")
            
            # Check for errors
            if category == 'error':
                errors.append(instance_id)
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            results[instance_id] = {
                'test_description': test_desc,
                'error': error_msg
            }
            errors.append(instance_id)
            print(f"    → {error_msg}\n")
    
    # Save results
    print("\n" + "="*80)
    print("JUDGMENT COMPLETE")
    print("="*80)
    print(f"Total instances: {len(test_descriptions)}")
    print(f"Successfully judged: {len(test_descriptions) - len(errors) - len(missing_problems)}")
    print(f"Missing problem statements: {len(missing_problems)}")
    print(f"Errors: {len(errors)}")
    
    if missing_problems:
        print("\nInstances with missing problem statements:")
        for instance_id in missing_problems[:5]:
            print(f"  - {instance_id}")
        if len(missing_problems) > 5:
            print(f"  ... and {len(missing_problems) - 5} more")
    
    if errors:
        print("\nInstances with errors:")
        for instance_id in errors[:5]:
            print(f"  - {instance_id}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
    
    save_results(results, args.output)
    
    # Print statistics
    if len(results) > 0:
        print_statistics(results)
    
    # Print sample results
    successful_results = {k: v for k, v in results.items() if 'judgment' in v and v['judgment']['category'] != 'error'}
    if successful_results:
        print("\n" + "="*80)
        sample_count = min(3, len(successful_results))
        print(f"SAMPLE RESULTS (first {sample_count})")
        print("="*80)
        for idx, (instance_id, result) in enumerate(list(successful_results.items())[:sample_count], 1):
            print(f"\n{idx}. {instance_id}")
            print(f"   Category: {result['judgment']['category']}")
            print(f"   Reasoning: {result['judgment']['reasoning']}")


if __name__ == "__main__":
    main()

# Made with Bob
