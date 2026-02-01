#!/usr/bin/env python3
"""
Update capability ratings for agents in the registry.
Allows fine-tuning of ratings based on your real-world experience.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_registry(registry_path: str) -> dict:
    """Load the agent registry."""
    with open(registry_path, 'r') as f:
        return json.load(f)


def save_registry(registry_path: str, registry: dict):
    """Save the agent registry with pretty formatting."""
    registry['last_updated'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)


def update_capability(registry: dict, agent_id: str, category: str,
                      rating: int = None, max_complexity: int = None,
                      notes: str = None, experience: int = None) -> bool:
    """
    Update a specific capability for an agent.

    Args:
        registry: The agent registry dict
        agent_id: ID of the agent to update
        category: Task category to update
        rating: New rating (1-5 stars)
        max_complexity: New max complexity (1-5)
        notes: Optional notes about the capability
        experience: Experience count

    Returns:
        True if updated successfully
    """
    if agent_id not in registry['agents']:
        print(f"Error: Agent '{agent_id}' not found in registry")
        print(f"Available agents: {', '.join(registry['agents'].keys())}")
        return False

    agent = registry['agents'][agent_id]

    # Ensure capabilities dict exists
    if 'capabilities' not in agent:
        agent['capabilities'] = {}

    # Get or create capability
    if category not in agent['capabilities']:
        agent['capabilities'][category] = {}

    capability = agent['capabilities'][category]

    # Update fields
    if rating is not None:
        if not 1 <= rating <= 5:
            print(f"Error: Rating must be between 1 and 5")
            return False
        capability['rating'] = rating

    if max_complexity is not None:
        if not 1 <= max_complexity <= 5:
            print(f"Error: Max complexity must be between 1 and 5")
            return False
        capability['max_complexity'] = max_complexity

    if notes is not None:
        capability['notes'] = notes

    if experience is not None:
        if experience < 0:
            print(f"Error: Experience count must be non-negative")
            return False
        capability['experience_count'] = experience

    return True


def list_agents(registry: dict):
    """List all agents in the registry."""
    print("\nConfigured Agents:")
    print("=" * 80)

    for agent_id, agent in registry['agents'].items():
        enabled = "✓" if agent.get('enabled', False) else "✗"
        model_id = agent.get('model_id', 'unknown')
        cost_type = agent.get('user_cost', {}).get('type', 'unknown')
        cap_count = len(agent.get('capabilities', {}))

        print(f"\n{enabled} {agent_id}")
        print(f"  Model: {model_id}")
        print(f"  Cost: {cost_type}")
        print(f"  Capabilities: {cap_count}")


def show_capability(registry: dict, agent_id: str, category: str = None):
    """Show capabilities for an agent."""
    if agent_id not in registry['agents']:
        print(f"Error: Agent '{agent_id}' not found")
        return

    agent = registry['agents'][agent_id]
    capabilities = agent.get('capabilities', {})

    print(f"\nCapabilities for {agent_id}:")
    print("=" * 80)

    if category:
        # Show specific category
        if category not in capabilities:
            print(f"No capability defined for category: {category}")
            return

        cap = capabilities[category]
        print(f"\n{category}:")
        print(f"  Rating: {cap.get('rating', 'N/A')}★")
        print(f"  Max Complexity: {cap.get('max_complexity', 'N/A')}")
        if 'notes' in cap:
            print(f"  Notes: {cap['notes']}")
        if 'experience_count' in cap:
            print(f"  Experience: {cap['experience_count']} tasks")
    else:
        # Show all categories
        if not capabilities:
            print("No capabilities defined")
            return

        for cat, cap in capabilities.items():
            print(f"\n{cat}:")
            print(f"  Rating: {cap.get('rating', 'N/A')}★")
            print(f"  Max Complexity: {cap.get('max_complexity', 'N/A')}")
            if 'notes' in cap:
                print(f"  Notes: {cap['notes']}")
            if 'experience_count' in cap:
                print(f"  Experience: {cap['experience_count']} tasks")


def list_categories(registry_path: str):
    """List available task categories."""
    base_dir = Path(registry_path).parent
    categories_file = base_dir / 'task-categories.json'

    if not categories_file.exists():
        print("Task categories file not found")
        return

    with open(categories_file, 'r') as f:
        categories = json.load(f)

    print("\nAvailable Task Categories:")
    print("=" * 80)

    for cat_id, category in categories.get('categories', {}).items():
        name = category.get('name', cat_id)
        desc = category.get('description', '')
        print(f"\n{cat_id}")
        print(f"  Name: {name}")
        print(f"  Description: {desc}")


def increment_experience(registry: dict, agent_id: str, category: str) -> bool:
    """Increment experience count for a capability."""
    if agent_id not in registry['agents']:
        print(f"Error: Agent '{agent_id}' not found")
        return False

    agent = registry['agents'][agent_id]

    if 'capabilities' not in agent or category not in agent['capabilities']:
        print(f"Error: No capability defined for {category}")
        return False

    capability = agent['capabilities'][category]
    current = capability.get('experience_count', 0)
    capability['experience_count'] = current + 1

    print(f"Updated {agent_id}.{category} experience: {current} → {current + 1}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Update agent capability ratings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Update rating and complexity
  %(prog)s --agent mistral-devstral --category frontend-development --rating 5 --max-complexity 5

  # Add notes
  %(prog)s --agent gpt-4-turbo --category bug-detection-fixes --notes "Excellent at finding edge cases"

  # Increment experience after using a model
  %(prog)s --agent claude-sonnet --category unit-test-generation --increment-experience

  # List all agents
  %(prog)s --list

  # Show capabilities for an agent
  %(prog)s --agent claude-sonnet --show

  # List available categories
  %(prog)s --list-categories
        ''')

    parser.add_argument('--registry', default='config/agent-registry.json',
                        help='Path to agent registry')
    parser.add_argument('--agent', '--model',
                        help='Agent ID to update')
    parser.add_argument('--category',
                        help='Task category to update')
    parser.add_argument('--rating', type=int,
                        help='Rating (1-5 stars)')
    parser.add_argument('--max-complexity', type=int,
                        help='Maximum complexity (1-5)')
    parser.add_argument('--notes',
                        help='Notes about this capability')
    parser.add_argument('--experience', type=int,
                        help='Experience count (number of tasks)')
    parser.add_argument('--increment-experience', action='store_true',
                        help='Increment experience count by 1')
    parser.add_argument('--list', action='store_true',
                        help='List all agents')
    parser.add_argument('--show', action='store_true',
                        help='Show capabilities for an agent')
    parser.add_argument('--list-categories', action='store_true',
                        help='List available task categories')

    args = parser.parse_args()

    # Get absolute path
    base_dir = Path(__file__).parent.parent
    registry_path = base_dir / args.registry

    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}")
        print("Run scripts/setup.sh first to create the registry")
        sys.exit(1)

    registry = load_registry(str(registry_path))

    # Handle list operations
    if args.list:
        list_agents(registry)
        return

    if args.list_categories:
        list_categories(str(registry_path))
        return

    if args.show:
        if not args.agent:
            print("Error: --agent required with --show")
            sys.exit(1)
        show_capability(registry, args.agent, args.category)
        return

    # Handle updates
    if not args.agent or not args.category:
        print("Error: --agent and --category required for updates")
        print("Use --list to see available agents")
        print("Use --list-categories to see available categories")
        sys.exit(1)

    # Perform update
    success = False

    if args.increment_experience:
        success = increment_experience(registry, args.agent, args.category)
    else:
        success = update_capability(
            registry, args.agent, args.category,
            rating=args.rating,
            max_complexity=args.max_complexity,
            notes=args.notes,
            experience=args.experience
        )

    if success:
        save_registry(str(registry_path), registry)
        print(f"\n✓ Updated {args.agent}.{args.category}")

        # Show updated capability
        show_capability(registry, args.agent, args.category)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
