#!/usr/bin/env python3
"""
Test runner for indirect prompt injection detection.

Validates the sanitize.py detector against the test case corpus
and reports accuracy metrics.

Usage:
    python run_tests.py
    python run_tests.py --verbose
    python run_tests.py --category instruction_override
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from sanitize import sanitize, determine_risk_level


# Risk level ordering for comparison
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def load_test_cases(test_file: Path) -> dict:
    """Load test cases from JSON file."""
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)


def risk_matches(expected: str, actual: str, strict: bool = False) -> bool:
    """
    Check if detected risk level matches expected.
    
    In non-strict mode, we consider it a match if:
    - Exact match
    - Actual is higher than expected (conservative is OK)
    
    In strict mode, only exact matches count.
    """
    if expected == actual:
        return True
    
    if not strict:
        # Higher risk than expected is acceptable (false positive is safer)
        return RISK_ORDER.get(actual, 0) >= RISK_ORDER.get(expected, 0)
    
    return False


def run_test_case(test_case: dict, verbose: bool = False) -> dict:
    """Run a single test case and return results."""
    content = test_case["content"]
    expected_risk = test_case["expected_risk"]
    
    # Run detection
    result = sanitize(content)
    actual_risk = result.risk_level
    
    # Evaluate
    passed = risk_matches(expected_risk, actual_risk, strict=False)
    exact_match = expected_risk == actual_risk
    
    test_result = {
        "id": test_case["id"],
        "category": test_case["category"],
        "expected_risk": expected_risk,
        "actual_risk": actual_risk,
        "score": result.risk_score,
        "passed": passed,
        "exact_match": exact_match,
        "findings_count": len(result.findings),
    }
    
    if verbose:
        test_result["findings"] = result.findings
        test_result["content_preview"] = content[:100] + "..." if len(content) > 100 else content
    
    return test_result


def run_all_tests(
    test_cases: list,
    category_filter: str = None,
    verbose: bool = False
) -> dict:
    """Run all test cases and aggregate results."""
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "exact_matches": 0,
        "by_category": {},
        "failed_cases": [],
        "test_results": []
    }
    
    for test_case in test_cases:
        # Filter by category if specified
        if category_filter and test_case["category"] != category_filter:
            continue
        
        test_result = run_test_case(test_case, verbose)
        results["test_results"].append(test_result)
        results["total"] += 1
        
        category = test_case["category"]
        if category not in results["by_category"]:
            results["by_category"][category] = {"total": 0, "passed": 0, "exact": 0}
        results["by_category"][category]["total"] += 1
        
        if test_result["passed"]:
            results["passed"] += 1
            results["by_category"][category]["passed"] += 1
        else:
            results["failed"] += 1
            results["failed_cases"].append(test_result)
        
        if test_result["exact_match"]:
            results["exact_matches"] += 1
            results["by_category"][category]["exact"] += 1
    
    # Calculate percentages
    if results["total"] > 0:
        results["pass_rate"] = results["passed"] / results["total"] * 100
        results["exact_rate"] = results["exact_matches"] / results["total"] * 100
    else:
        results["pass_rate"] = 0
        results["exact_rate"] = 0
    
    return results


def format_results(results: dict, verbose: bool = False) -> str:
    """Format test results as human-readable report."""
    lines = []
    
    # Header
    lines.append("=" * 60)
    lines.append("  INDIRECT PROMPT INJECTION DETECTION TEST RESULTS")
    lines.append("=" * 60)
    lines.append("")
    
    # Summary
    lines.append(f"Total Tests:    {results['total']}")
    lines.append(f"Passed:         {results['passed']} ({results['pass_rate']:.1f}%)")
    lines.append(f"Exact Matches:  {results['exact_matches']} ({results['exact_rate']:.1f}%)")
    lines.append(f"Failed:         {results['failed']}")
    lines.append("")
    
    # By category
    lines.append("Results by Category:")
    lines.append("-" * 40)
    for category, stats in sorted(results["by_category"].items()):
        pct = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        lines.append(f"  {category:25} {stats['passed']:2}/{stats['total']:2} ({pct:5.1f}%)")
    lines.append("")
    
    # Failed cases
    if results["failed_cases"]:
        lines.append("Failed Test Cases:")
        lines.append("-" * 40)
        for case in results["failed_cases"]:
            lines.append(f"  ❌ {case['id']}")
            lines.append(f"     Expected: {case['expected_risk']}, Got: {case['actual_risk']} (score: {case['score']})")
            if verbose and "content_preview" in case:
                lines.append(f"     Content: {case['content_preview']}")
        lines.append("")
    
    # Verbose: all test details
    if verbose:
        lines.append("All Test Results:")
        lines.append("-" * 40)
        for result in results["test_results"]:
            status = "✓" if result["passed"] else "❌"
            exact = "=" if result["exact_match"] else "≈" if result["passed"] else "✗"
            lines.append(
                f"  {status} {result['id']:15} "
                f"[{result['expected_risk']:8} {exact} {result['actual_risk']:8}] "
                f"score:{result['score']:3} findings:{result['findings_count']}"
            )
    
    # Final verdict
    lines.append("")
    if results["pass_rate"] >= 95:
        lines.append("✅ EXCELLENT: Detection accuracy is production-ready")
    elif results["pass_rate"] >= 85:
        lines.append("✓ GOOD: Detection accuracy is acceptable")
    elif results["pass_rate"] >= 70:
        lines.append("⚠ NEEDS WORK: Detection accuracy needs improvement")
    else:
        lines.append("❌ POOR: Detection accuracy is insufficient")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Run prompt injection detection tests"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed results for each test"
    )
    parser.add_argument(
        "--category", "-c",
        help="Filter tests by category"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--test-file", "-f",
        default=None,
        help="Path to test cases JSON file"
    )
    
    args = parser.parse_args()
    
    # Find test file
    if args.test_file:
        test_file = Path(args.test_file)
    else:
        # Look in standard locations
        script_dir = Path(__file__).parent
        test_file = script_dir.parent / "tests" / "test_cases.json"
        if not test_file.exists():
            test_file = script_dir / "test_cases.json"
    
    if not test_file.exists():
        print(f"Error: Test file not found: {test_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load and run tests
    data = load_test_cases(test_file)
    results = run_all_tests(
        data["test_cases"],
        category_filter=args.category,
        verbose=args.verbose
    )
    
    # Output
    if args.json:
        # Remove verbose data for cleaner JSON
        output = {k: v for k, v in results.items() if k != "test_results"}
        if args.verbose:
            output["test_results"] = results["test_results"]
        print(json.dumps(output, indent=2))
    else:
        print(format_results(results, verbose=args.verbose))
    
    # Exit code based on pass rate
    sys.exit(0 if results["pass_rate"] >= 85 else 1)


if __name__ == "__main__":
    main()
