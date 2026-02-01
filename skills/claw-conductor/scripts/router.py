#!/usr/bin/env python3
"""
Claw Conductor Router
Intelligent routing of subtasks to optimal AI models based on capability ratings.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class Task:
    """Represents a subtask to be routed."""

    def __init__(self, description: str, category: str, complexity: int,
                 tech_stack: List[str] = None):
        self.description = description
        self.category = category
        self.complexity = complexity
        self.tech_stack = tech_stack or []

    def __repr__(self):
        return f"Task({self.category}, complexity={self.complexity})"


class Router:
    """Routes tasks to optimal models based on capability ratings."""

    def __init__(self, registry_path: str):
        """Initialize router with agent registry."""
        with open(registry_path, 'r') as f:
            self.registry = json.load(f)

        self.agents = self.registry.get('agents', {})
        self.user_config = self.registry.get('user_config', {})

    def score_agent_for_task(self, agent_id: str, task: Task) -> Tuple[int, Dict]:
        """
        Score an agent's suitability for a task.

        Returns:
            (score, details): Score 0-100 and breakdown dict
        """
        agent = self.agents.get(agent_id)

        if not agent:
            return 0, {"error": "Agent not found"}

        if not agent.get('enabled', False):
            return 0, {"error": "Agent disabled"}

        capabilities = agent.get('capabilities', {})
        capability = capabilities.get(task.category)

        if not capability:
            return 0, {"error": f"No {task.category} capability"}

        score = 0
        details = {
            "agent_id": agent_id,
            "model_id": agent.get('model_id'),
            "category": task.category,
            "breakdown": {}
        }

        # 1. Rating Score (50 points max)
        rating = capability.get('rating', 0)
        rating_points = rating * 10  # 1★=10pts, 5★=50pts
        score += rating_points
        details["breakdown"]["rating"] = {
            "stars": rating,
            "points": rating_points,
            "max": 50
        }

        # 2. Complexity Ceiling (40 points)
        max_complexity = capability.get('max_complexity', 0)

        if max_complexity < task.complexity:
            # CANNOT handle this complexity - disqualify
            return 0, {"error": f"Complexity {task.complexity} exceeds max {max_complexity}"}

        # Calculate complexity points
        gap = max_complexity - task.complexity
        if gap == 0:
            complexity_points = 40  # Perfect match
        elif gap == 1:
            complexity_points = 35  # Slightly overqualified
        else:
            complexity_points = 30  # Very overqualified

        score += complexity_points
        details["breakdown"]["complexity"] = {
            "task_complexity": task.complexity,
            "max_complexity": max_complexity,
            "gap": gap,
            "points": complexity_points,
            "max": 40
        }

        # 3. Experience Bonus (10 points)
        experience = capability.get('experience_count', 0)
        experience_points = min(experience, 10)
        score += experience_points
        details["breakdown"]["experience"] = {
            "count": experience,
            "points": experience_points,
            "max": 10
        }

        # 4. Cost Bonus (10 points) - only if cost tracking enabled
        if self.user_config.get('cost_tracking_enabled', False):
            cost_type = agent.get('user_cost', {}).get('type', 'unknown')

            if cost_type in ['free', 'free-tier']:
                cost_points = 10
            else:
                cost_points = 0

            score += cost_points
            details["breakdown"]["cost"] = {
                "type": cost_type,
                "points": cost_points,
                "max": 10
            }

        details["total_score"] = min(score, 100)
        details["rating_summary"] = f"{rating}★ complexity≤{max_complexity}"

        return min(score, 100), details

    def route_task(self, task: Task) -> Tuple[Optional[str], Dict]:
        """
        Find the best agent for a task.

        Returns:
            (agent_id, details): Best agent ID and scoring details
        """
        scores = []

        for agent_id in self.agents.keys():
            score, details = self.score_agent_for_task(agent_id, task)
            if score > 0:
                scores.append((score, agent_id, details))

        if not scores:
            return None, {
                "error": "No capable agents found",
                "task": task.category,
                "complexity": task.complexity
            }

        # Sort by score (highest first)
        scores.sort(reverse=True, key=lambda x: x[0])

        # Check for ties
        top_score = scores[0][0]
        tied_agents = [(s, aid, d) for s, aid, d in scores if s == top_score]

        if len(tied_agents) > 1:
            # Tiebreaker: prefer free models
            if self.user_config.get('prefer_free_when_equal', True):
                free_agents = [
                    (s, aid, d) for s, aid, d in tied_agents
                    if self.agents[aid].get('user_cost', {}).get('type') in ['free', 'free-tier']
                ]
                if free_agents:
                    tied_agents = free_agents

            # If still tied, pick first (stable)
            winner = tied_agents[0]
        else:
            winner = scores[0]

        score, agent_id, details = winner

        # Add runner-ups to details
        details["runner_ups"] = [
            {
                "agent_id": aid,
                "model_id": self.agents[aid].get('model_id'),
                "score": s,
                "rating": d.get("rating_summary")
            }
            for s, aid, d in scores[1:4]  # Top 3 runner-ups
        ]

        return agent_id, details

    def route_task_with_fallback(self, task: Task,
                                   execution_callback=None) -> Tuple[Optional[str], Dict]:
        """
        Route a task with automatic fallback to first runner-up on failure.

        Strategy:
        - Try primary model twice
        - If both fail, try first runner-up twice
        - If that fails, give up (don't try all runner-ups)

        Args:
            task: The task to route
            execution_callback: Optional function(agent_id, task) -> (success, error_msg)
                               If None, just returns routing without execution

        Returns:
            (agent_id, details): Agent that succeeded and execution details
        """
        fallback_config = self.user_config.get('fallback', {})
        retry_delay = fallback_config.get('retry_delay_seconds', 2)
        track_failures = fallback_config.get('track_failures', True)

        # Get primary agent + runner-ups
        agent_id, details = self.route_task(task)

        if not agent_id:
            # No capable agents found
            return None, details

        # Build attempt list: Try primary twice, then first runner-up twice
        agents_to_try = [
            (agent_id, details, "primary"),  # Primary attempt 1
            (agent_id, details, "primary"),  # Primary attempt 2
        ]

        # Add first runner-up if available
        runner_ups = details.get('runner_ups', [])
        if runner_ups:
            first_runner_up = runner_ups[0]
            ru_agent_id = first_runner_up['agent_id']
            # Get full details for runner-up
            ru_score, ru_details = self.score_agent_for_task(ru_agent_id, task)
            if ru_score > 0:
                agents_to_try.append((ru_agent_id, ru_details, "fallback"))  # Fallback attempt 1
                agents_to_try.append((ru_agent_id, ru_details, "fallback"))  # Fallback attempt 2

        # Track execution attempts
        execution_log = []

        # If no callback provided, just return primary routing
        if execution_callback is None:
            details['fallback_available'] = len(runner_ups) > 0
            details['fallback_model'] = runner_ups[0]['model_id'] if runner_ups else None
            return agent_id, details

        # Try each attempt in order
        import time

        for attempt_num, (attempt_agent_id, attempt_details, attempt_type) in enumerate(agents_to_try, 1):
            attempt_model_id = self.agents[attempt_agent_id].get('model_id')

            log_entry = {
                "attempt": attempt_num,
                "agent_id": attempt_agent_id,
                "model_id": attempt_model_id,
                "type": attempt_type,
                "score": attempt_details.get('total_score', 0)
            }

            try:
                # Execute with the agent
                success, error_msg = execution_callback(attempt_agent_id, task)

                log_entry['success'] = success
                log_entry['error'] = error_msg

                if success:
                    # Success! Update metrics and return
                    if track_failures:
                        self._update_success_metrics(attempt_agent_id, task.category)

                    execution_log.append(log_entry)

                    # Add execution details to response
                    attempt_details['execution'] = {
                        'attempts': execution_log,
                        'succeeded_on_attempt': attempt_num,
                        'fallback_used': attempt_type == "fallback",
                        'retry_used': attempt_num > 1 and attempt_type == "primary"
                    }

                    return attempt_agent_id, attempt_details
                else:
                    # Failure, log and continue
                    execution_log.append(log_entry)

                    if track_failures:
                        self._update_failure_metrics(attempt_agent_id, task.category)

                    # Wait before retry
                    if attempt_num < len(agents_to_try):
                        time.sleep(retry_delay)

            except Exception as e:
                log_entry['success'] = False
                log_entry['error'] = str(e)
                log_entry['exception'] = True
                execution_log.append(log_entry)

                if track_failures:
                    self._update_failure_metrics(attempt_agent_id, task.category)

                # Wait before retry
                if attempt_num < len(agents_to_try):
                    time.sleep(retry_delay)

        # All attempts failed
        return None, {
            "error": "All attempts failed (primary x2, fallback x2)",
            "task": task.category,
            "complexity": task.complexity,
            "execution": {
                "attempts": execution_log,
                "total_attempts": len(execution_log),
                "all_failed": True,
                "primary_attempts": 2,
                "fallback_attempts": len(execution_log) - 2 if len(execution_log) > 2 else 0
            }
        }

    def _update_success_metrics(self, agent_id: str, category: str):
        """Update success metrics for an agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        # Update performance metrics
        metrics = agent.get('performance_metrics', {})
        metrics['tasks_completed'] = metrics.get('tasks_completed', 0) + 1

        # Update success rate
        total = metrics.get('tasks_completed', 0)
        if total > 0:
            successes = total  # We only increment on success
            metrics['success_rate'] = successes / total

    def _update_failure_metrics(self, agent_id: str, category: str):
        """Update failure metrics and apply penalties."""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        fallback_config = self.user_config.get('fallback', {})
        penalize = fallback_config.get('penalize_failures', True)
        penalty = fallback_config.get('failure_penalty_points', 5)

        if penalize and category in agent.get('capabilities', {}):
            capability = agent['capabilities'][category]

            # Track failure count
            failure_count = capability.get('failure_count', 0)
            capability['failure_count'] = failure_count + 1

            # Apply penalty to experience (can go negative)
            current_exp = capability.get('experience_count', 0)
            capability['experience_count'] = max(0, current_exp - penalty)

    def route_multiple_tasks(self, tasks: List[Task]) -> List[Dict]:
        """
        Route multiple tasks to optimal agents.

        Returns:
            List of routing results with agent assignments
        """
        results = []

        for i, task in enumerate(tasks):
            agent_id, details = self.route_task(task)

            result = {
                "subtask_id": i + 1,
                "description": task.description,
                "category": task.category,
                "complexity": task.complexity,
                "assigned_agent": agent_id,
                "assigned_model": self.agents[agent_id].get('model_id') if agent_id else None,
                "score": details.get('total_score', 0),
                "details": details
            }

            results.append(result)

        return results

    def print_routing_results(self, results: List[Dict]):
        """Pretty print routing results."""
        print("\n" + "="*80)
        print("CLAW CONDUCTOR - INTELLIGENT ROUTING RESULTS")
        print("="*80 + "\n")

        for result in results:
            print(f"Subtask #{result['subtask_id']}: {result['description']}")
            print(f"  Category: {result['category']} | Complexity: {result['complexity']}")

            if result['assigned_agent']:
                print(f"  ✓ Assigned to: {result['assigned_model']}")
                print(f"  Score: {result['score']}/100")

                breakdown = result['details'].get('breakdown', {})
                if breakdown:
                    print(f"    - Rating: {breakdown.get('rating', {}).get('points', 0)}/50 pts")
                    print(f"    - Complexity: {breakdown.get('complexity', {}).get('points', 0)}/40 pts")
                    print(f"    - Experience: {breakdown.get('experience', {}).get('points', 0)}/10 pts")
                    if 'cost' in breakdown:
                        print(f"    - Cost Bonus: {breakdown.get('cost', {}).get('points', 0)}/10 pts")

                runner_ups = result['details'].get('runner_ups', [])
                if runner_ups:
                    print(f"  Runner-ups:")
                    for ru in runner_ups:
                        print(f"    - {ru['model_id']}: {ru['score']}/100 ({ru['rating']})")
            else:
                error = result['details'].get('error', 'Unknown error')
                print(f"  ✗ No agent found: {error}")

            print()


def main():
    """CLI interface for testing the router."""
    import argparse

    parser = argparse.ArgumentParser(description='Route tasks to optimal AI models')
    parser.add_argument('--registry', default='config/agent-registry.json',
                        help='Path to agent registry')
    parser.add_argument('--test', action='store_true',
                        help='Run test routing scenario')

    args = parser.parse_args()

    # Get absolute path
    base_dir = Path(__file__).parent.parent
    registry_path = base_dir / args.registry

    router = Router(str(registry_path))

    if args.test:
        # Test scenario: User registration system
        print("Test Scenario: User Registration System with Email Verification\n")

        tasks = [
            Task(
                description="Design database schema (users, verification_tokens tables)",
                category="database-operations",
                complexity=3
            ),
            Task(
                description="Build registration API endpoint (POST /api/register)",
                category="api-development",
                complexity=3
            ),
            Task(
                description="Implement email verification flow",
                category="backend-development",
                complexity=4
            ),
            Task(
                description="Create registration form UI",
                category="frontend-development",
                complexity=2
            ),
            Task(
                description="Write API tests (unit + integration)",
                category="unit-test-generation",
                complexity=3
            )
        ]

        results = router.route_multiple_tasks(tasks)
        router.print_routing_results(results)

        # Summary
        print("="*80)
        print("EXECUTION PLAN")
        print("="*80 + "\n")

        agent_tasks = {}
        for result in results:
            agent = result['assigned_model'] or 'UNASSIGNED'
            if agent not in agent_tasks:
                agent_tasks[agent] = []
            agent_tasks[agent].append(result['subtask_id'])

        for agent, task_ids in agent_tasks.items():
            print(f"{agent}:")
            print(f"  Subtasks: {task_ids}")

        print(f"\n{len(agent_tasks)} agent(s) required for parallel execution")
    else:
        print("Use --test to run a test routing scenario")
        print("Or import this module to use programmatically")


if __name__ == '__main__':
    main()
