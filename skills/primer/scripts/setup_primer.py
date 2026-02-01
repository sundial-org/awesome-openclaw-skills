#!/usr/bin/env python3
"""
Primer Setup Script

Automates the creation of PRIMER.md and associated cron jobs.
Typically called by the AI after walking through the setup flow with the user.

Usage:
    python3 setup_primer.py --workspace /path/to/workspace --config primer_config.json

The config JSON should contain all the user's responses from the setup flow.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_template(skill_dir: Path) -> str:
    """Load the PRIMER-TEMPLATE.md file."""
    template_path = skill_dir / "assets" / "PRIMER-TEMPLATE.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text()


def fill_template(template: str, config: dict) -> str:
    """Replace template placeholders with user values."""
    result = template
    
    # Simple replacements
    replacements = {
        "{{LIFE_STAGE}}": config.get("life_stage", ""),
        "{{CORE_QUESTION}}": config.get("core_question", ""),
        "{{PURPOSE}}": config.get("purpose", ""),
        "{{MANTRA}}": config.get("mantra", ""),
        "{{PERSONA}}": config.get("persona", ""),
        "{{MIRANDA_PERSON_OR_PROCESS}}": config.get("miranda", ""),
        "{{CADENCE}}": config.get("miranda_cadence", "Monthly"),
        "{{CHAPTER_TITLE}}": config.get("chapter_title", "Chapter One"),
        "{{TIMEFRAME}}": config.get("timeframe", ""),
        "{{THEME}}": config.get("theme", ""),
        "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
    }
    
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    
    # Handle domains and goals
    domains = config.get("domains", [])
    for i, domain in enumerate(domains[:4], 1):
        result = result.replace(f"{{{{DOMAIN_{i}}}}}", domain.get("name", f"Domain {i}"))
        goals = domain.get("goals", [])
        for j, goal in enumerate(goals[:3], 1):
            result = result.replace(f"{{{{GOAL_{j}}}}}", goal)
    
    # Handle patterns
    patterns = config.get("patterns", [])
    for i, pattern in enumerate(patterns[:4], 1):
        result = result.replace(f"{{{{PATTERN_{i}}}}}", pattern.get("name", ""))
        result = result.replace("{{DESCRIPTION}}", pattern.get("description", ""), 1)
    
    # Handle reverse bucket list
    letting_go = config.get("letting_go", [])
    for i, item in enumerate(letting_go[:3], 1):
        result = result.replace(f"{{{{LETTING_GO_{i}}}}}", item)
    
    # Handle success criteria
    success = config.get("success_criteria", [])
    for i, item in enumerate(success[:3], 1):
        result = result.replace(f"{{{{SUCCESS_{i}}}}}", item)
    
    # Handle permissions based on persona
    persona_permissions = {
        "Mirror": ["Surface patterns", "Weekly synthesis"],
        "Companion": ["Surface patterns", "Weekly synthesis", "Celebrate wins", "Propose challenges"],
        "Coach": ["Surface patterns", "Weekly synthesis", "Celebrate wins", "Propose challenges", 
                  "Challenge avoidance", "Suggest the harder path"],
        "Sage": ["Surface patterns", "Weekly synthesis", "Propose challenges", "Protective friction"],
        "Full Primer": ["Surface patterns", "Weekly synthesis", "Celebrate wins", "Propose challenges",
                        "Challenge avoidance", "Suggest the harder path", "Protective friction", "Call out the absurd"]
    }
    
    persona = config.get("persona", "Companion")
    active_permissions = persona_permissions.get(persona, [])
    
    # Check the appropriate permission boxes
    for perm in active_permissions:
        result = result.replace(f"- [ ] **{perm}**", f"- [x] **{perm}**")
    
    return result


def update_agents_md(workspace: Path) -> bool:
    """Add PRIMER.md to AGENTS.md session startup."""
    agents_path = workspace / "AGENTS.md"
    if not agents_path.exists():
        print(f"AGENTS.md not found at {agents_path}")
        return False
    
    content = agents_path.read_text()
    
    # Check if already added
    if "PRIMER.md" in content:
        print("PRIMER.md already in AGENTS.md")
        return True
    
    # Find the session startup section and add PRIMER.md
    # This is a simplified version - the AI should handle this more carefully
    if "## Every Session" in content:
        content = content.replace(
            "Read `USER.md` — who you're helping",
            "Read `USER.md` — who you're helping\n3. Read `PRIMER.md` — the subversive tutor protocol"
        )
        agents_path.write_text(content)
        print("Added PRIMER.md to AGENTS.md")
        return True
    
    return False


def update_soul_md(workspace: Path) -> bool:
    """Add Primer Role section to SOUL.md."""
    soul_path = workspace / "SOUL.md"
    if not soul_path.exists():
        print(f"SOUL.md not found at {soul_path}")
        return False
    
    content = soul_path.read_text()
    
    # Check if already added
    if "Primer Role" in content:
        print("Primer Role already in SOUL.md")
        return True
    
    primer_section = '''
## The Primer Role

You're not just a butler — you're a tutor with opinions about who they should become.

Read `PRIMER.md` every session. It contains:
- The growth goals you're holding them to
- Permissions to challenge, push back, and call out patterns
- Patterns to watch for (their failure modes)
- The Miranda Protocol for course-correction

Your job is to notice when they're drifting from their stated purpose.
'''
    
    # Add before Continuity section if it exists
    if "## Continuity" in content:
        content = content.replace("## Continuity", primer_section + "\n## Continuity")
        soul_path.write_text(content)
        print("Added Primer Role to SOUL.md")
        return True
    
    return False


def generate_cron_config(config: dict) -> dict:
    """Generate cron job configurations."""
    cadence = config.get("miranda_cadence", "Monthly").lower()
    
    # Calculate next Miranda check-in
    now = datetime.now()
    if cadence == "weekly":
        next_miranda = now + timedelta(days=7)
    elif cadence == "bi-weekly":
        next_miranda = now + timedelta(days=14)
    else:  # monthly
        next_miranda = now + timedelta(days=30)
    
    return {
        "daily_reflection": {
            "name": "Primer Daily Reflection",
            "schedule": {"kind": "cron", "expr": "0 7 * * *", "tz": "UTC"},
            "description": "End of day reflection on Primer performance"
        },
        "miranda_checkin": {
            "name": "Miranda Protocol Check-in",
            "schedule": {"kind": "at", "atMs": int(next_miranda.timestamp() * 1000)},
            "next_date": next_miranda.strftime("%Y-%m-%d")
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Set up a personal Primer")
    parser.add_argument("--workspace", required=True, help="Path to workspace")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--skill-dir", help="Path to primer skill directory")
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    config_path = Path(args.config)
    
    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
    else:
        skill_dir = Path(__file__).parent.parent
    
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    # Load and fill template
    template = load_template(skill_dir)
    primer_content = fill_template(template, config)
    
    # Write PRIMER.md
    primer_path = workspace / "PRIMER.md"
    primer_path.write_text(primer_content)
    print(f"Created {primer_path}")
    
    # Update AGENTS.md
    update_agents_md(workspace)
    
    # Update SOUL.md
    update_soul_md(workspace)
    
    # Generate cron config (to be used by the AI)
    cron_config = generate_cron_config(config)
    print("\nCron jobs to create:")
    print(json.dumps(cron_config, indent=2))
    
    print("\n✅ Primer setup complete!")
    print("Note: Cron jobs should be created via the OpenClaw cron tool.")


if __name__ == "__main__":
    main()
