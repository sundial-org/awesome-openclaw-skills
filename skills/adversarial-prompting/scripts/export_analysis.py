#!/usr/bin/env python3
"""
Export adversarial prompting analysis to markdown file.
"""

import sys
from datetime import datetime
from pathlib import Path


def export_analysis(content: str, problem_summary: str = "analysis") -> str:
    """
    Export analysis content to a markdown file.
    
    Args:
        content: The full analysis content to export
        problem_summary: Brief description for filename (default: "analysis")
    
    Returns:
        Path to the created file
    """
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize problem_summary for filename
    safe_summary = "".join(c for c in problem_summary if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_summary = safe_summary.replace(' ', '_')[:50]  # Limit length
    
    filename = f"adversarial_analysis_{safe_summary}_{timestamp}.md"
    filepath = Path.home() / filename
    
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Adversarial Analysis: {problem_summary}\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("---\n\n")
        f.write(content)
    
    return str(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_analysis.py <content> [problem_summary]")
        sys.exit(1)
    
    content = sys.argv[1]
    problem_summary = sys.argv[2] if len(sys.argv) > 2 else "analysis"
    
    filepath = export_analysis(content, problem_summary)
    print(f"✅ Analysis exported to: {filepath}")
