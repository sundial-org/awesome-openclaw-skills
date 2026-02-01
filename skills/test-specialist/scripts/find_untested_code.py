#!/usr/bin/env python3
"""
Find source files that don't have corresponding test files.

This script helps identify code that lacks test coverage by finding
source files without matching test files.

Usage:
    python find_untested_code.py [src-dir] [--pattern test|spec]
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Tuple

def find_source_files(src_dir: str, extensions: List[str] = None) -> Set[Path]:
    """Find all source files in directory."""
    if extensions is None:
        extensions = ['.ts', '.tsx', '.js', '.jsx']

    source_files = set()
    src_path = Path(src_dir)

    for ext in extensions:
        source_files.update(src_path.rglob(f'*{ext}'))

    # Exclude test files
    test_patterns = ['.test.', '.spec.', '__tests__', '__mocks__']
    source_files = {
        f for f in source_files
        if not any(pattern in str(f) for pattern in test_patterns)
    }

    return source_files

def find_test_files(src_dir: str, pattern: str = 'test') -> Set[Path]:
    """Find all test files in directory."""
    src_path = Path(src_dir)

    test_files = set()

    # Common test file patterns
    patterns = [
        f'*.{pattern}.ts',
        f'*.{pattern}.tsx',
        f'*.{pattern}.js',
        f'*.{pattern}.jsx',
    ]

    for p in patterns:
        test_files.update(src_path.rglob(p))

    # Also check __tests__ directories
    test_dirs = src_path.rglob('__tests__')
    for test_dir in test_dirs:
        if test_dir.is_dir():
            for ext in ['.ts', '.tsx', '.js', '.jsx']:
                test_files.update(test_dir.rglob(f'*{ext}'))

    return test_files

def get_tested_sources(test_files: Set[Path], src_dir: str) -> Set[Path]:
    """Determine which source files have tests."""
    src_path = Path(src_dir)
    tested = set()

    for test_file in test_files:
        # Get the base name without .test/.spec
        name = test_file.name
        for pattern in ['.test.', '.spec.']:
            name = name.replace(pattern, '.')

        # Look for matching source file
        # Check same directory
        source_file = test_file.parent / name
        if source_file.exists():
            tested.add(source_file)
            continue

        # Check parent if in __tests__ directory
        if '__tests__' in str(test_file):
            parent_source = test_file.parent.parent / name
            if parent_source.exists():
                tested.add(parent_source)

    return tested

def categorize_untested(untested: Set[Path], src_dir: str) -> dict:
    """Categorize untested files by type and importance."""
    categories = {
        'components': [],
        'services': [],
        'utils': [],
        'api': [],
        'hooks': [],
        'models': [],
        'other': []
    }

    for file in untested:
        rel_path = file.relative_to(src_dir)
        path_str = str(rel_path).lower()

        if 'component' in path_str or 'components' in path_str:
            categories['components'].append(file)
        elif 'service' in path_str or 'services' in path_str:
            categories['services'].append(file)
        elif 'util' in path_str or 'utils' in path_str or 'helper' in path_str:
            categories['utils'].append(file)
        elif 'api' in path_str or 'endpoint' in path_str:
            categories['api'].append(file)
        elif 'hook' in path_str or 'hooks' in path_str:
            categories['hooks'].append(file)
        elif 'model' in path_str or 'models' in path_str or 'schema' in path_str:
            categories['models'].append(file)
        else:
            categories['other'].append(file)

    return categories

def print_report(source_files: Set[Path], test_files: Set[Path],
                 untested: Set[Path], src_dir: str):
    """Print formatted report."""
    print("\n=== Test Coverage Analysis ===\n")
    print(f"📁 Source directory: {src_dir}")
    print(f"📄 Total source files: {len(source_files)}")
    print(f"✅ Test files found: {len(test_files)}")
    print(f"🔴 Untested files: {len(untested)}")

    coverage_pct = ((len(source_files) - len(untested)) / len(source_files) * 100) if source_files else 0
    print(f"📊 Test file coverage: {coverage_pct:.1f}%\n")

    if untested:
        print("=== Untested Files by Category ===\n")

        categories = categorize_untested(untested, src_dir)

        # Priority order
        priority_order = ['api', 'services', 'models', 'hooks', 'components', 'utils', 'other']

        for category in priority_order:
            files = categories[category]
            if files:
                print(f"{category.upper()} ({len(files)} files):")
                for file in sorted(files)[:10]:  # Show max 10 per category
                    rel_path = file.relative_to(src_dir)
                    print(f"   - {rel_path}")

                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more")
                print()

        print("\n💡 Recommendations:")
        print("   1. Prioritize testing API endpoints and services")
        print("   2. Add tests for business logic and data models")
        print("   3. Test custom hooks for correct behavior")
        print("   4. Consider testing complex components")
        print("   5. Utils can be tested as needed\n")
    else:
        print("🎉 All source files have corresponding test files!\n")

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else 'src'
    pattern = 'test'

    if '--pattern' in sys.argv:
        idx = sys.argv.index('--pattern')
        if idx + 1 < len(sys.argv):
            pattern = sys.argv[idx + 1]

    if not Path(src_dir).exists():
        print(f"Error: Source directory not found: {src_dir}")
        print("\nUsage: python find_untested_code.py [src-dir] [--pattern test|spec]")
        sys.exit(1)

    source_files = find_source_files(src_dir)
    test_files = find_test_files(src_dir, pattern)
    tested_sources = get_tested_sources(test_files, src_dir)
    untested = source_files - tested_sources

    print_report(source_files, test_files, untested, src_dir)

if __name__ == '__main__':
    main()
