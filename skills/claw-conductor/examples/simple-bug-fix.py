#!/usr/bin/env python3
"""
Example: Simple Bug Fix Routing

Demonstrates how Claw Conductor routes a simple bug fix to
an appropriate model, preferring free options when possible.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.router import Router, Task


def main():
    # Initialize router
    registry_path = Path(__file__).parent.parent / 'config' / 'agent-registry.json'
    router = Router(str(registry_path))

    # Define a simple bug fix task
    task = Task(
        description="Fix timezone display bug showing UTC instead of local time",
        category="bug-detection-fixes",
        complexity=2  # Simple - just formatting logic
    )

    print("=" * 80)
    print("EXAMPLE: Simple Bug Fix Routing")
    print("=" * 80)
    print()
    print(f"Task: {task.description}")
    print(f"Category: {task.category}")
    print(f"Complexity: {task.complexity} (Simple)")
    print()

    # Route the task
    agent_id, details = router.route_task(task)

    if agent_id:
        print("✓ ROUTING DECISION")
        print("-" * 80)
        print(f"Assigned to: {details.get('model_id')}")
        print(f"Score: {details.get('total_score')}/100")
        print()
        print(f"Rating: {details.get('rating_summary')}")
        print()

        # Show breakdown
        breakdown = details.get('breakdown', {})
        if breakdown:
            print("Score Breakdown:")
            print(f"  • Rating:     {breakdown.get('rating', {}).get('points', 0)}/50 pts")
            print(f"  • Complexity: {breakdown.get('complexity', {}).get('points', 0)}/40 pts")
            print(f"  • Experience: {breakdown.get('experience', {}).get('points', 0)}/10 pts")
            if 'cost' in breakdown:
                print(f"  • Cost Bonus: {breakdown.get('cost', {}).get('points', 0)}/10 pts")

        # Show why this model was chosen
        print()
        print("Why this model?")
        complexity_info = breakdown.get('complexity', {})
        gap = complexity_info.get('gap', 0)

        if gap == 0:
            print("  ✓ Perfect complexity match (no over/under qualification)")
        elif gap == 1:
            print("  ✓ Slightly overqualified (good safety margin)")
        else:
            print("  ✓ Overqualified but best available option")

        cost_info = breakdown.get('cost', {})
        if cost_info and cost_info.get('points', 0) > 0:
            print(f"  ✓ Free tier model ({cost_info.get('type')})")

        # Show runner-ups
        runner_ups = details.get('runner_ups', [])
        if runner_ups:
            print()
            print("Alternative models considered:")
            for ru in runner_ups:
                print(f"  • {ru['model_id']}: {ru['score']}/100 ({ru['rating']})")

    else:
        print("✗ NO MODEL FOUND")
        print("-" * 80)
        print(f"Error: {details.get('error')}")

    print()
    print("=" * 80)
    print()
    print("Key Insight:")
    print("For simple bugs (complexity=2), Claw Conductor often prefers free models")
    print("like Gemini Flash or DeepSeek V3, saving costs while maintaining quality.")


if __name__ == '__main__':
    main()
