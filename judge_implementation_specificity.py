#!/usr/bin/env python3
"""
Judge whether test patches check for bug fixes or specific implementation choices.

This script:
1. Reads problem statements and test patches (actual test code)
2. Uses Gemini AI to judge if the test checks "was the bug fixed?" or 
   "was the bug fixed in this specific way?"
3. Categorizes tests as bug-focused or implementation-specific
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


def read_test_patch(instance_id: str) -> Optional[str]:
    """Read test patch for an instance."""
    filepath = Path('test_patches') / f"{instance_id}-test-patch.diff"
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def get_all_instances() -> list:
    """Get list of all instances that have both problem statements and test patches."""
    problem_dir = Path('problem_statements')
    test_dir = Path('test_patches')
    
    if not problem_dir.exists() or not test_dir.exists():
        print("ERROR: Required directories not found!")
        print("Please run: python download_swebench.py")
        sys.exit(1)
    
    # Get instances that have both files
    problem_instances = {f.stem for f in problem_dir.glob('*.md')}
    test_instances = {f.stem.replace('-test-patch', '') for f in test_dir.glob('*-test-patch.diff')}
    
    common_instances = problem_instances & test_instances
    return sorted(list(common_instances))


def judge_implementation_specificity(model: genai.GenerativeModel, problem_statement: str, 
                                     test_patch: str, instance_id: str) -> Dict[str, str]:
    """
    Use Gemini to judge if test checks for bug fix or specific implementation.
    
    Args:
        model: Gemini model instance
        problem_statement: The issue/problem description
        test_patch: The actual test code changes (diff)
        instance_id: The instance ID for context
    
    Returns:
        Dictionary with 'category', 'reasoning', and 'specificity_score'
    """
    prompt = f"""You are analyzing a test patch from the SWE-bench dataset to determine what it actually validates.

**ISSUE REPORT:**
{problem_statement}

**TEST PATCH (actual test code changes):**
```diff
{test_patch}
```

**YOUR TASK:**
Determine whether this FAIL_TO_PASS test primarily checks:
1. **Bug-focused**: "Was the reported bug/issue fixed?" (tests the WHAT)
2. **Implementation-specific**: "Was the bug fixed in this specific way?" (tests the HOW)

**KEY DISTINCTIONS:**

**Bug-focused tests** validate:
- The reported problem no longer occurs
- Expected behavior from the issue is achieved
- Edge cases mentioned in the issue work correctly
- The fix solves the stated problem (regardless of how)

**Implementation-specific tests** validate:
- Specific data structures or algorithms used
- Internal implementation details not mentioned in the issue
- Particular code organization or patterns
- Specific method calls or function signatures beyond what the issue requires
- Implementation choices that could vary while still fixing the bug

**ANALYSIS CRITERIA:**
1. Does the test check something explicitly mentioned in the issue? → Bug-focused
2. Does the test verify internal details not in the issue? → Implementation-specific
3. Could the bug be fixed differently while failing this test? → Implementation-specific
4. Does the test encode "how" rather than "what"? → Implementation-specific

**RESPONSE FORMAT:**
Category: [bug_focused | implementation_specific | mixed]
Specificity Score: [1-5, where 1=purely bug-focused, 5=highly implementation-specific]
Reasoning: [2-3 sentences explaining your judgment]

Focus on what the test ACTUALLY checks in the code, not just what it claims to test.

Your response:"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse the response
        lines = text.split('\n')
        category = None
        specificity_score = None
        reasoning = None
        
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith('category:'):
                category_text = line.replace('Category:', '').replace('category:', '').strip().lower()
                # Normalize category
                if 'bug' in category_text and 'focus' in category_text:
                    category = 'bug_focused'
                elif 'implementation' in category_text or 'specific' in category_text:
                    category = 'implementation_specific'
                elif 'mixed' in category_text:
                    category = 'mixed'
            elif line_lower.startswith('specificity score:'):
                score_text = line.replace('Specificity Score:', '').replace('specificity score:', '').strip()
                # Extract number
                import re
                match = re.search(r'(\d+)', score_text)
                if match:
                    specificity_score = int(match.group(1))
            elif line_lower.startswith('reasoning:'):
                reasoning = line.split(':', 1)[1].strip()
        
        # If reasoning spans multiple lines, capture it
        if reasoning and len(lines) > 3:
            reasoning_start = False
            full_reasoning = []
            for line in lines:
                if line.lower().startswith('reasoning:'):
                    reasoning_start = True
                    full_reasoning.append(line.split(':', 1)[1].strip())
                elif reasoning_start and line.strip() and not line.lower().startswith('category') and not line.lower().startswith('specificity'):
                    full_reasoning.append(line.strip())
            if full_reasoning:
                reasoning = ' '.join(full_reasoning)
        
        if not category:
            category = 'unknown'
            reasoning = f"Failed to parse category from response: {text}"
        
        return {
            'category': category,
            'specificity_score': specificity_score or 0,
            'reasoning': reasoning or "No reasoning provided",
            'raw_response': text
        }
    
    except Exception as e:
        return {
            'category': 'error',
            'specificity_score': 0,
            'reasoning': f"Failed to analyze: {str(e)}",
            'raw_response': ''
        }


def save_results(results: Dict[str, Dict], output_file: str = 'implementation_specificity.json'):
    """Save judgment results to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to {output_file}")


def print_statistics(results: Dict[str, Dict]):
    """Print statistics about the judgments."""
    categories = {}
    scores = []
    
    for instance_id, result in results.items():
        if 'judgment' in result:
            cat = result['judgment']['category']
            categories[cat] = categories.get(cat, 0) + 1
            score = result['judgment']['specificity_score']
            if score > 0:
                scores.append(score)
    
    print("\n" + "="*80)
    print("JUDGMENT STATISTICS")
    print("="*80)
    print(f"Total instances judged: {len(results)}")
    
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"\nAverage specificity score: {avg_score:.2f} / 5.0")
        print(f"  1-2: Bug-focused ({sum(1 for s in scores if s <= 2)} instances)")
        print(f"  3: Mixed ({sum(1 for s in scores if s == 3)} instances)")
        print(f"  4-5: Implementation-specific ({sum(1 for s in scores if s >= 4)} instances)")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Judge whether tests check bug fixes or implementation specifics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Judge all instances
  python judge_implementation_specificity.py
  
  # Judge a specific instance
  python judge_implementation_specificity.py django__django-14315
  
  # Use custom output file
  python judge_implementation_specificity.py --output my_judgments.json
        """
    )
    parser.add_argument(
        'instance_id',
        nargs='?',
        help='Specific instance ID to judge (e.g., django__django-14315). If not provided, judges all instances.'
    )
    parser.add_argument(
        '-o', '--output',
        default='implementation_specificity.json',
        help='Output JSON file path (default: implementation_specificity.json)'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    print("="*80)
    print("Test Implementation Specificity Judge with Gemini AI")
    print("="*80)
    print()
    
    if args.instance_id:
        print(f"Mode: Judging specific instance '{args.instance_id}'")
        instances = [args.instance_id]
    else:
        print("Mode: Judging all instances")
        print("\nFinding instances with both problem statements and test patches...")
        instances = get_all_instances()
        print(f"✓ Found {len(instances)} instances\n")
    
    # Setup Gemini
    print("Setting up Gemini AI...")
    model = setup_gemini()
    print("✓ Gemini AI configured\n")
    
    # Judge each instance
    results = {}
    errors = []
    missing_data = []
    
    for idx, instance_id in enumerate(instances, 1):
        print(f"[{idx}/{len(instances)}] Judging {instance_id}...")
        
        # Read problem statement
        problem_statement = read_problem_statement(instance_id)
        if not problem_statement:
            print(f"    ⚠ Problem statement not found, skipping\n")
            missing_data.append(instance_id)
            results[instance_id] = {'error': 'Problem statement not found'}
            continue
        
        # Read test patch
        test_patch = read_test_patch(instance_id)
        if not test_patch:
            print(f"    ⚠ Test patch not found, skipping\n")
            missing_data.append(instance_id)
            results[instance_id] = {'error': 'Test patch not found'}
            continue
        
        try:
            # Judge implementation specificity
            judgment = judge_implementation_specificity(model, problem_statement, test_patch, instance_id)
            
            # Store result
            results[instance_id] = {'judgment': judgment}
            
            # Print result
            category = judgment['category']
            score = judgment['specificity_score']
            reasoning_preview = judgment['reasoning'][:80] + "..." if len(judgment['reasoning']) > 80 else judgment['reasoning']
            print(f"    → Category: {category} (Score: {score}/5)")
            print(f"    → {reasoning_preview}\n")
            
            # Check for errors
            if category == 'error':
                errors.append(instance_id)
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            results[instance_id] = {'error': error_msg}
            errors.append(instance_id)
            print(f"    → {error_msg}\n")
    
    # Save results
    print("\n" + "="*80)
    print("JUDGMENT COMPLETE")
    print("="*80)
    print(f"Total instances: {len(instances)}")
    print(f"Successfully judged: {len(instances) - len(errors) - len(missing_data)}")
    print(f"Missing data: {len(missing_data)}")
    print(f"Errors: {len(errors)}")
    
    if missing_data:
        print("\nInstances with missing data:")
        for instance_id in missing_data[:5]:
            print(f"  - {instance_id}")
        if len(missing_data) > 5:
            print(f"  ... and {len(missing_data) - 5} more")
    
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
            print(f"   Specificity Score: {result['judgment']['specificity_score']}/5")
            print(f"   Reasoning: {result['judgment']['reasoning']}")


if __name__ == "__main__":
    main()

# Made with Bob
