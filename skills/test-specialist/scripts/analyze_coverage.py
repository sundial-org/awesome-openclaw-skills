#!/usr/bin/env python3
"""
Analyze test coverage and identify gaps.

This script parses coverage reports and provides insights on:
- Files with low coverage
- Uncovered critical paths
- Coverage trends

Usage:
    python analyze_coverage.py [coverage-file]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def parse_coverage_json(filepath: str) -> Dict:
    """Parse Jest/Istanbul coverage JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_file_coverage(file_data: Dict) -> Dict:
    """Analyze coverage for a single file."""
    statements = file_data.get('s', {})
    branches = file_data.get('b', {})
    functions = file_data.get('f', {})
    lines = file_data.get('l', {})

    # Count covered vs total
    def count_coverage(data):
        if isinstance(data, dict):
            values = list(data.values())
            if not values:
                return 0, 0
            # Handle branch coverage (nested arrays)
            if isinstance(values[0], list):
                total = sum(len(v) for v in values)
                covered = sum(sum(1 for x in v if x > 0) for v in values)
            else:
                total = len(values)
                covered = sum(1 for v in values if v > 0)
            return covered, total
        return 0, 0

    stmt_covered, stmt_total = count_coverage(statements)
    branch_covered, branch_total = count_coverage(branches)
    func_covered, func_total = count_coverage(functions)

    def pct(covered, total):
        return (covered / total * 100) if total > 0 else 100

    return {
        'statements': {'pct': pct(stmt_covered, stmt_total), 'covered': stmt_covered, 'total': stmt_total},
        'branches': {'pct': pct(branch_covered, branch_total), 'covered': branch_covered, 'total': branch_total},
        'functions': {'pct': pct(func_covered, func_total), 'covered': func_covered, 'total': func_total},
    }

def identify_coverage_gaps(coverage_data: Dict, threshold: float = 80.0) -> List[Tuple[str, Dict]]:
    """Identify files with coverage below threshold."""
    gaps = []

    for filepath, file_data in coverage_data.items():
        if 'path' in file_data:
            filepath = file_data['path']

        analysis = analyze_file_coverage(file_data)

        # Check if any metric is below threshold
        below_threshold = any(
            metric['pct'] < threshold
            for metric in analysis.values()
        )

        if below_threshold:
            gaps.append((filepath, analysis))

    return sorted(gaps, key=lambda x: min(m['pct'] for m in x[1].values()))

def print_coverage_report(gaps: List[Tuple[str, Dict]]):
    """Print formatted coverage report."""
    print("\n=== Coverage Gap Analysis ===\n")

    if not gaps:
        print("✅ All files meet coverage threshold!")
        return

    print(f"Found {len(gaps)} files with coverage gaps:\n")

    for filepath, analysis in gaps:
        print(f"📄 {filepath}")
        print(f"   Statements: {analysis['statements']['pct']:.1f}% ({analysis['statements']['covered']}/{analysis['statements']['total']})")
        print(f"   Branches:   {analysis['branches']['pct']:.1f}% ({analysis['branches']['covered']}/{analysis['branches']['total']})")
        print(f"   Functions:  {analysis['functions']['pct']:.1f}% ({analysis['functions']['covered']}/{analysis['functions']['total']})")
        print()

def get_priority_files(gaps: List[Tuple[str, Dict]]) -> List[str]:
    """Identify high-priority files to test (lowest coverage)."""
    return [filepath for filepath, _ in gaps[:5]]

def main():
    if len(sys.argv) < 2:
        # Try to find coverage file automatically
        common_paths = [
            'coverage/coverage-final.json',
            'coverage/coverage.json',
            '.coverage/coverage-final.json',
        ]

        coverage_file = None
        for path in common_paths:
            if Path(path).exists():
                coverage_file = path
                break

        if not coverage_file:
            print("Usage: python analyze_coverage.py [coverage-file]")
            print("\nCommon coverage file locations:")
            print("  - coverage/coverage-final.json")
            print("  - coverage/coverage.json")
            sys.exit(1)
    else:
        coverage_file = sys.argv[1]

    if not Path(coverage_file).exists():
        print(f"Error: Coverage file not found: {coverage_file}")
        sys.exit(1)

    print(f"Analyzing coverage from: {coverage_file}")

    coverage_data = parse_coverage_json(coverage_file)
    gaps = identify_coverage_gaps(coverage_data)

    print_coverage_report(gaps)

    if gaps:
        print("\n🎯 Priority files to improve (top 5):")
        for filepath in get_priority_files(gaps):
            print(f"   - {filepath}")
        print()

if __name__ == '__main__':
    main()
