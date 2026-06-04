#!/usr/bin/env python3
"""
Download SWE-bench-verified dataset and organize into folders:
- test_patches/: Test patch diffs
- fail_to_pass/: FAIL_TO_PASS test lists
- pass_to_pass/: PASS_TO_PASS test lists  
- problem_statements/: Problem descriptions
"""

import json
import os
from pathlib import Path
from datasets import load_dataset


def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'test_patches',
        'fail_to_pass',
        'pass_to_pass',
        'problem_statements'
    ]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Created directories")


def save_test_patch(instance_id, test_patch):
    """Save test patch to file."""
    if test_patch:
        filepath = f"test_patches/{instance_id}-test-patch.diff"
        with open(filepath, 'w') as f:
            f.write(test_patch)
        return True
    return False


def save_fail_to_pass_tests(instance_id, fail_to_pass):
    """Save FAIL_TO_PASS tests to JSON file."""
    if fail_to_pass:
        # The field is a JSON string, parse it first
        if isinstance(fail_to_pass, str):
            tests = json.loads(fail_to_pass)
        else:
            tests = fail_to_pass
        
        # Only save if there are actual tests
        if tests:
            filepath = f"fail_to_pass/{instance_id}.json"
            with open(filepath, 'w') as f:
                json.dump(tests, f, indent=2)
            return True
    return False


def save_pass_to_pass_tests(instance_id, pass_to_pass):
    """Save PASS_TO_PASS tests to JSON file."""
    if pass_to_pass:
        # The field is a JSON string, parse it first
        if isinstance(pass_to_pass, str):
            tests = json.loads(pass_to_pass)
        else:
            tests = pass_to_pass
        
        # Only save if there are actual tests
        if tests:
            filepath = f"pass_to_pass/{instance_id}.json"
            with open(filepath, 'w') as f:
                json.dump(tests, f, indent=2)
            return True
    return False


def save_problem_statement(instance_id, problem_statement):
    """Save problem statement to markdown file."""
    if problem_statement:
        filepath = f"problem_statements/{instance_id}.md"
        with open(filepath, 'w') as f:
            f.write(f"# {instance_id}\n\n")
            f.write(problem_statement)
        return True
    return False


def download_and_organize():
    """Download SWE-bench-verified dataset and organize files."""
    print("Loading SWE-bench-verified dataset from HuggingFace...")
    print("This may take a few minutes on first run...\n")
    
    # Load the dataset
    dataset = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    
    print(f"✓ Loaded {len(dataset)} instances\n")
    
    stats = {
        'total': len(dataset),
        'test_patches': 0,
        'fail_to_pass': 0,
        'pass_to_pass': 0,
        'problem_statements': 0
    }
    
    # Process each instance
    for idx, instance in enumerate(dataset, 1):
        instance_id = instance['instance_id']
        
        print(f"[{idx}/{len(dataset)}] Processing {instance_id}...")
        
        # Save test patch
        if save_test_patch(instance_id, instance.get('test_patch')):
            stats['test_patches'] += 1
        
        # Save FAIL_TO_PASS tests
        if save_fail_to_pass_tests(instance_id, instance.get('FAIL_TO_PASS', [])):
            stats['fail_to_pass'] += 1
        
        # Save PASS_TO_PASS tests
        if save_pass_to_pass_tests(instance_id, instance.get('PASS_TO_PASS', [])):
            stats['pass_to_pass'] += 1
        
        # Save problem statement
        if save_problem_statement(instance_id, instance.get('problem_statement')):
            stats['problem_statements'] += 1
    
    # Print summary
    print("\n" + "="*80)
    print("DOWNLOAD COMPLETE")
    print("="*80)
    print(f"Total instances: {stats['total']}")
    print(f"  - Test patches saved: {stats['test_patches']}")
    print(f"  - FAIL_TO_PASS lists saved: {stats['fail_to_pass']}")
    print(f"  - PASS_TO_PASS lists saved: {stats['pass_to_pass']}")
    print(f"  - Problem statements saved: {stats['problem_statements']}")
    print("\nFiles organized in:")
    print("  - test_patches/")
    print("  - fail_to_pass/")
    print("  - pass_to_pass/")
    print("  - problem_statements/")


def main():
    """Main entry point."""
    print("="*80)
    print("SWE-bench-verified Dataset Downloader")
    print("="*80)
    print()
    
    # Create directories
    create_directories()
    
    # Download and organize
    download_and_organize()


if __name__ == "__main__":
    main()

# Made with Bob
