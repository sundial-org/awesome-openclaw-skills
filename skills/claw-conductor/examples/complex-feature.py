#!/usr/bin/env python3
"""
Example: Complex Feature with Multiple Subtasks

Demonstrates how Claw Conductor decomposes a complex request
into multiple subtasks and routes each to the optimal model.
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

    print("=" * 80)
    print("EXAMPLE: E-Commerce Checkout System")
    print("=" * 80)
    print()
    print("Request: 'Build a complete e-commerce checkout flow with payment processing'")
    print()

    # Define subtasks with varying complexity
    tasks = [
        Task(
            description="Design checkout database schema (orders, payments, inventory)",
            category="database-operations",
            complexity=4  # Complex - multi-table relationships, transactions
        ),
        Task(
            description="Build Stripe payment integration API",
            category="api-development",
            complexity=5  # Very complex - payment security, webhooks, error handling
        ),
        Task(
            description="Create shopping cart state management",
            category="frontend-development",
            complexity=3  # Moderate - local storage, state updates
        ),
        Task(
            description="Implement checkout form with validation",
            category="frontend-development",
            complexity=2  # Simple - form UI with basic validation
        ),
        Task(
            description="Write integration tests for payment flow",
            category="unit-test-generation",
            complexity=4  # Complex - mock Stripe, test edge cases
        ),
        Task(
            description="Add inventory management logic",
            category="backend-development",
            complexity=4  # Complex - concurrency, stock tracking
        ),
    ]

    # Route all tasks
    results = router.route_multiple_tasks(tasks)

    # Print results
    router.print_routing_results(results)

    # Analysis
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    # Group by agent
    agent_tasks = {}
    total_cost_bonus = 0

    for result in results:
        agent = result['assigned_model'] or 'UNASSIGNED'
        if agent not in agent_tasks:
            agent_tasks[agent] = {
                'subtasks': [],
                'complexities': [],
                'categories': set()
            }
        agent_tasks[agent]['subtasks'].append(result['subtask_id'])
        agent_tasks[agent]['complexities'].append(result['complexity'])
        agent_tasks[agent]['categories'].add(result['category'])

        # Track cost savings
        breakdown = result.get('details', {}).get('breakdown', {})
        if 'cost' in breakdown:
            total_cost_bonus += breakdown['cost'].get('points', 0)

    print("Execution Plan:")
    print()
    for agent, info in agent_tasks.items():
        print(f"  {agent}:")
        print(f"    • Subtasks: {info['subtasks']}")
        print(f"    • Complexity range: {min(info['complexities'])}-{max(info['complexities'])}")
        print(f"    • Categories: {len(info['categories'])}")
        print()

    print(f"Total agents required: {len(agent_tasks)}")
    print(f"Parallel execution possible: YES (independent subtasks)")
    print()

    # Cost analysis
    if total_cost_bonus > 0:
        free_tasks = sum(1 for r in results
                        if r.get('details', {}).get('breakdown', {}).get('cost', {}).get('points', 0) > 0)
        print("Cost Optimization:")
        print(f"  • {free_tasks}/{len(tasks)} tasks routed to free models")
        print(f"  • Estimated savings: Significant (free tier usage where possible)")
        print()

    # Complexity matching
    print("Complexity Matching:")
    for result in results:
        complexity_info = result.get('details', {}).get('breakdown', {}).get('complexity', {})
        task_complexity = complexity_info.get('task_complexity')
        max_complexity = complexity_info.get('max_complexity')
        gap = complexity_info.get('gap', 0)

        match_type = "Perfect" if gap == 0 else "Slight over-qualification" if gap == 1 else "Over-qualified"

        print(f"  • Subtask #{result['subtask_id']} (complexity={task_complexity}): {match_type}")
        print(f"    Assigned model max={max_complexity}")

    print()
    print("=" * 80)
    print()
    print("Key Insights:")
    print("  1. High complexity tasks (4-5) routed to expert models (Claude, GPT-4)")
    print("  2. Simple tasks (2-3) can use free models to save costs")
    print("  3. Parallel execution minimizes total time")
    print("  4. Each model matched to its strengths (API, frontend, testing)")


if __name__ == '__main__':
    main()
