#!/usr/bin/env python3
"""
Example: Conservative Fallback Routing

Demonstrates Claw Conductor's conservative fallback strategy:
1. Try primary model (attempt 1)
2. Try primary model (attempt 2)
3. If both fail, try first runner-up (attempt 3)
4. Try first runner-up again (attempt 4)
5. If all fail, give up

This prevents cascading through irrelevant models that may not even
have the capability for the task.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.router import Router, Task


def simulate_execution(agent_id: str, task: Task, fail_pattern: dict = None):
    """
    Simulate task execution with controllable failures.

    Args:
        agent_id: ID of agent attempting the task
        task: The task being executed
        fail_pattern: Dict like {"mistral-devstral-2512": [1, 2], "llama-3.3-70b": []}
                     where the list contains which attempts should fail

    Returns:
        (success, error_msg): Execution result
    """
    fail_pattern = fail_pattern or {}

    # Track attempt number per agent
    if not hasattr(simulate_execution, 'attempt_counts'):
        simulate_execution.attempt_counts = {}

    if agent_id not in simulate_execution.attempt_counts:
        simulate_execution.attempt_counts[agent_id] = 0

    simulate_execution.attempt_counts[agent_id] += 1
    attempt_num = simulate_execution.attempt_counts[agent_id]

    # Check if this attempt should fail
    if agent_id in fail_pattern and attempt_num in fail_pattern[agent_id]:
        return False, f"Model '{agent_id}' failed on attempt #{attempt_num} (simulated failure)"
    else:
        return True, None


def reset_attempt_counts():
    """Reset attempt counter for new scenario."""
    if hasattr(simulate_execution, 'attempt_counts'):
        simulate_execution.attempt_counts = {}


def main():
    # Initialize router
    registry_path = Path(__file__).parent.parent / 'config' / 'agent-registry.json'
    router = Router(str(registry_path))

    print("=" * 80)
    print("EXAMPLE: Conservative Fallback Routing")
    print("=" * 80)
    print()

    # Define a task
    task = Task(
        description="Implement user authentication with JWT tokens",
        category="backend-development",
        complexity=4
    )

    print(f"Task: {task.description}")
    print(f"Category: {task.category}")
    print(f"Complexity: {task.complexity}")
    print()

    # First, show what the router would do (no execution)
    primary_agent, primary_details = router.route_task_with_fallback(task, execution_callback=None)
    print("Routing Plan:")
    print(f"  Primary: {primary_details.get('model_id')} (score: {primary_details.get('total_score')})")

    if primary_details.get('fallback_available'):
        print(f"  Fallback: {primary_details.get('fallback_model')}")
    else:
        print(f"  Fallback: None available")

    print()
    print("Strategy: Try primary 2x → If fail, try fallback 2x → Give up")
    print()
    input("Press Enter to see scenarios...")
    print()

    # Scenario 1: Success on first attempt
    print("-" * 80)
    print("SCENARIO 1: Primary Succeeds on First Attempt")
    print("-" * 80)
    print()

    reset_attempt_counts()

    def scenario1_callback(agent_id, task_obj):
        # Everything succeeds
        return simulate_execution(agent_id, task_obj, fail_pattern={})

    agent_id, details = router.route_task_with_fallback(task, execution_callback=scenario1_callback)

    if agent_id:
        exec_info = details.get('execution', {})
        print(f"✓ Task completed successfully")
        print(f"  Model: {details.get('model_id')}")
        print(f"  Total attempts: {len(exec_info.get('attempts', []))}")
        print(f"  Fallback used: {exec_info.get('fallback_used', False)}")

        print()
        print("Attempt Log:")
        for attempt in exec_info.get('attempts', []):
            status = "✓" if attempt['success'] else "✗"
            print(f"  [{status}] Attempt {attempt['attempt']}: {attempt['model_id']} ({attempt['type']})")

    print()
    input("Press Enter for next scenario...")
    print()

    # Scenario 2: Primary fails once, succeeds on retry
    print("-" * 80)
    print("SCENARIO 2: Primary Fails Once, Succeeds on Retry")
    print("-" * 80)
    print()

    reset_attempt_counts()
    primary_id = primary_agent

    def scenario2_callback(agent_id, task_obj):
        # Primary fails on attempt 1, succeeds on attempt 2
        fail_pattern = {primary_id: [1]}
        return simulate_execution(agent_id, task_obj, fail_pattern=fail_pattern)

    agent_id, details = router.route_task_with_fallback(task, execution_callback=scenario2_callback)

    if agent_id:
        exec_info = details.get('execution', {})
        print(f"✓ Task completed after retry")
        print(f"  Model: {details.get('model_id')}")
        print(f"  Total attempts: {len(exec_info.get('attempts', []))}")
        print(f"  Retry used: {exec_info.get('retry_used', False)}")

        print()
        print("Attempt Log:")
        for attempt in exec_info.get('attempts', []):
            status = "✓" if attempt['success'] else "✗"
            print(f"  [{status}] Attempt {attempt['attempt']}: {attempt['model_id']} ({attempt['type']})")
            if attempt.get('error'):
                print(f"       → {attempt['error']}")

    print()
    input("Press Enter for next scenario...")
    print()

    # Scenario 3: Primary fails twice, fallback succeeds
    print("-" * 80)
    print("SCENARIO 3: Primary Fails 2x, Fallback Succeeds")
    print("-" * 80)
    print()

    reset_attempt_counts()

    def scenario3_callback(agent_id, task_obj):
        # Primary fails both attempts
        fail_pattern = {primary_id: [1, 2]}
        return simulate_execution(agent_id, task_obj, fail_pattern=fail_pattern)

    agent_id, details = router.route_task_with_fallback(task, execution_callback=scenario3_callback)

    if agent_id:
        exec_info = details.get('execution', {})
        print(f"✓ Task completed via fallback")
        print(f"  Model: {details.get('model_id')}")
        print(f"  Total attempts: {len(exec_info.get('attempts', []))}")
        print(f"  Fallback used: {exec_info.get('fallback_used', False)}")

        print()
        print("Attempt Log:")
        for attempt in exec_info.get('attempts', []):
            status = "✓" if attempt['success'] else "✗"
            print(f"  [{status}] Attempt {attempt['attempt']}: {attempt['model_id']} ({attempt['type']})")
            if attempt.get('error'):
                print(f"       → {attempt['error']}")

        print()
        print("Analysis:")
        print("  • Primary model failed twice → automatically switched to fallback")
        print("  • Fallback succeeded immediately → task completed")
        print("  • Total delay: ~4 seconds (2 failures × 2s retry delay)")

    print()
    input("Press Enter for final scenario...")
    print()

    # Scenario 4: All attempts fail
    print("-" * 80)
    print("SCENARIO 4: All Attempts Fail (4 total)")
    print("-" * 80)
    print()

    reset_attempt_counts()

    # Get fallback agent ID
    fallback_id = None
    if primary_details.get('runner_ups'):
        fallback_id = primary_details['runner_ups'][0]['agent_id']

    def scenario4_callback(agent_id, task_obj):
        # Both models fail all attempts
        fail_pattern = {
            primary_id: [1, 2],
            fallback_id: [1, 2] if fallback_id else []
        }
        return simulate_execution(agent_id, task_obj, fail_pattern=fail_pattern)

    agent_id, details = router.route_task_with_fallback(task, execution_callback=scenario4_callback)

    if not agent_id:
        print(f"✗ Task failed after all attempts")
        exec_info = details.get('execution', {})
        print(f"  Error: {details.get('error')}")
        print(f"  Total attempts: {exec_info.get('total_attempts', 0)}")
        print(f"  Primary attempts: {exec_info.get('primary_attempts', 0)}")
        print(f"  Fallback attempts: {exec_info.get('fallback_attempts', 0)}")

        print()
        print("Attempt Log:")
        for attempt in exec_info.get('attempts', []):
            status = "✓" if attempt['success'] else "✗"
            print(f"  [{status}] Attempt {attempt['attempt']}: {attempt['model_id']} ({attempt['type']})")
            if attempt.get('error'):
                print(f"       → {attempt['error']}")

        print()
        print("Next Steps:")
        print("  1. Check if models are experiencing outages")
        print("  2. Queue task for retry after delay")
        print("  3. Alert user about the failure")
        print("  4. Consider adding more fallback models")

    print()
    print("=" * 80)
    print()
    print("Key Insights:")
    print("  1. Conservative approach: Only tries 2 models (primary + 1 fallback)")
    print("  2. Each model gets 2 attempts before giving up")
    print("  3. Total maximum attempts: 4 (2 primary + 2 fallback)")
    print("  4. Prevents wasteful cascading through irrelevant models")
    print("  5. 2-second retry delay prevents API rate limiting")


if __name__ == '__main__':
    main()
