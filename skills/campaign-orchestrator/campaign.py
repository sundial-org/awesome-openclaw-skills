#!/usr/bin/env python3
"""
Campaign Orchestrator - Main CLI

Usage:
    python3 campaign.py <command> [options]

Commands:
    start <template> --lead <name> [--delay N] [--attio-id <id>]
    status <lead>
    list
    stop <lead> --reason <reason>
    remove <lead>
    check <lead>
    templates
    preview <template>
    pending                     # Show all pending campaign steps
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE = os.environ.get("WORKSPACE", "/home/art/niemand")
STATE_DIR = Path(f"{WORKSPACE}/state/campaign-orchestrator")
STATE_FILE = STATE_DIR / "campaigns.json"
SKILL_DIR = Path(__file__).parent

# Ensure state directory exists
STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_campaigns():
    """Load campaign state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"campaigns": {}, "templates": {}}


def save_campaigns(data):
    """Save campaign state to file."""
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_templates():
    """Load available templates."""
    templates = {}
    for f in SKILL_DIR.glob("*.md"):
        if f.name == "SKILL.md":
            continue
        templates[f.stem] = f.read_text()
    return templates


def get_template_delays(template_name):
    """Get default delays for a template (in hours)."""
    defaults = {
        "post-demo": {"sms": 0, "email": 4},
        "primary": {"sms": 4, "email": 24},
        "secondary": {"sms": 24, "email": 96},
        "tertiary": {"sms": 96, "email": 168},
        "quaternary": {"sms": 168, "email": 336},
        "re-engagement": {"sms": 72, "email": 96},  # Day 3 SMS follow-up
    }
    return defaults.get(template_name, {"sms": 24, "email": 48})


def check_exclusions(data, lead_name):
    """Check if lead is in exclusion list."""
    exclusions = data.get("exclusions", [])
    for exclusion in exclusions:
        if exclusion.get("name") == lead_name:
            return exclusion
    return None


def cmd_start(args):
    """Start a new campaign."""
    template_name = args.template
    lead_name = args.lead
    attio_id = args.attio_id
    delay_override = args.delay

    templates = load_templates()
    if template_name not in templates:
        print(f"Error: Template '{template_name}' not found.")
        print(f"Available: {', '.join(templates.keys())}")
        sys.exit(1)

    data = load_campaigns()

    # Check exclusion list
    exclusion = check_exclusions(data, lead_name)
    if exclusion:
        print(f"❌ CANNOT START CAMPAIGN: '{lead_name}' is in exclusion list")
        print(f"   Reason: {exclusion.get('reason', 'Unknown')}")
        print(f"   Added: {exclusion.get('added_at', 'Unknown')}")
        sys.exit(1)

    # Check if campaign already exists
    if lead_name in data["campaigns"] and data["campaigns"][lead_name]["status"] == "active":
        print(f"Error: Active campaign already exists for '{lead_name}'")
        print(f"Use '/campaign status {lead_name}' to check, or '/campaign stop {lead_name}' first.")
        sys.exit(1)

    delays = get_template_delays(template_name)
    now = datetime.now()
    steps = []

    sms_delay = delay_override if delay_override is not None else delays.get("sms", 4)
    steps.append({
        "id": f"sms_{template_name}",
        "type": "sms",
        "scheduled": (now + timedelta(hours=sms_delay)).isoformat(),
        "template": template_name,
        "status": "pending",
        "sent_at": None,
        "response_received": False
    })

    email_delay = delay_override if delay_override is not None else delays.get("email", 24)
    steps.append({
        "id": f"email_{template_name}",
        "type": "email",
        "scheduled": (now + timedelta(hours=email_delay)).isoformat(),
        "template": template_name,
        "status": "pending",
        "sent_at": None,
        "response_received": False
    })

    campaign = {
        "template": template_name,
        "lead": lead_name,
        "attio_id": attio_id,
        "started": now.isoformat(),
        "steps": steps,
        "current_step": 0,
        "status": "active",
        "history": [],
        "last_checked": now.isoformat()
    }

    data["campaigns"][lead_name] = campaign
    save_campaigns(data)

    print(f"✅ Campaign started for '{lead_name}'")
    print(f"   Template: {template_name}")
    print(f"   Steps: {len(steps)}")
    print(f"   First step: {steps[0]['type']} at {steps[0]['scheduled']}")


def cmd_status(args):
    """Show campaign status."""
    lead_name = args.lead

    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    if lead_name not in campaigns:
        print(f"No campaign for '{lead_name}'")
        sys.exit(1)

    campaign = campaigns[lead_name]
    print(f"Campaign: {lead_name}")
    print(f"  Template: {campaign['template']}")
    print(f"  Status: {campaign['status']}")
    print(f"  Started: {campaign['started']}")
    print(f"  Step: {campaign['current_step'] + 1}/{len(campaign['steps'])}")

    for i, step in enumerate(campaign["steps"]):
        status_icon = "✅" if step["status"] == "completed" else "⏳" if step["status"] == "pending" else "❌"
        sent = step.get("sent_at", "not sent")
        response = "❌ No" if not step.get("response_received") else "✅ Yes"
        print(f"  {status_icon} Step {i+1}: {step['type']} - {step['status']}")
        print(f"      Scheduled: {step['scheduled']}")
        print(f"      Sent: {sent}")
        print(f"      Response received: {response}")


def cmd_list(args):
    """List all active campaigns."""
    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    active = {k: v for k, v in campaigns.items() if v["status"] == "active"}

    if not active:
        print("No active campaigns")
        return

    print(f"Active Campaigns: {len(active)}")
    print("-" * 50)
    for lead, campaign in active.items():
        step = campaign["current_step"] + 1
        total = len(campaign["steps"])
        next_step = campaign["steps"][campaign["current_step"]] if campaign["current_step"] < total else None
        next_time = next_step["scheduled"] if next_step else "N/A"
        print(f"  {lead}: {campaign['template']} ({step}/{total})")
        print(f"      Next: {next_time}")


def cmd_stop(args):
    """Stop a campaign."""
    lead_name = args.lead
    reason = args.reason

    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    if lead_name not in campaigns:
        print(f"No campaign found for '{lead_name}'")
        sys.exit(1)

    campaign = campaigns[lead_name]
    campaign["status"] = "terminated"
    campaign["terminated_reason"] = reason
    campaign["terminated_at"] = datetime.now().isoformat()

    for step in campaign["steps"]:
        if step["status"] == "pending":
            step["status"] = "cancelled"

    save_campaigns(data)

    print(f"❌ Campaign terminated for '{lead_name}'")
    print(f"   Reason: {reason}")
    print(f"   Steps completed: {campaign['current_step']}/{len(campaign['steps'])}")


def cmd_remove(args):
    """Remove a lead from campaigns (opted out, not interested, etc.)."""
    lead_name = args.lead

    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    if lead_name not in campaigns:
        print(f"No campaign found for '{lead_name}'")
        sys.exit(1)

    campaign = campaigns[lead_name]
    removed_campaign = campaigns.pop(lead_name)
    save_campaigns(data)

    print(f"🗑️  Removed '{lead_name}' from campaigns")
    print(f"   Template: {campaign['template']}")
    print(f"   Steps completed: {campaign['current_step']}/{len(campaign['steps'])}")
    print(f"   History preserved in state for records")


def cmd_check(args):
    """Check for responses before sending next step."""
    lead_name = args.lead

    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    if lead_name not in campaigns:
        print(f"No campaign for '{lead_name}'")
        sys.exit(1)

    campaign = campaigns[lead_name]

    print(f"Response Check: {lead_name}")
    print("-" * 40)

    # Check each completed step for responses
    has_response = False
    for i, step in enumerate(campaign["steps"]):
        if step["status"] == "completed":
            response = step.get("response_received", False)
            if response:
                has_response = True
                print(f"  ✅ Step {i+1} ({step['type']}): Response received!")
            else:
                print(f"  ⏳ Step {i+1} ({step['type']}): No response")

    if has_response:
        print("\n⚠️  Lead has responded - consider terminating campaign")
        print(f"   Use: /campaign stop \"{lead_name}\" --reason \"lead_replied\"")
    else:
        print("\n✅ No responses detected - safe to proceed with next step")

    campaign["last_checked"] = datetime.now().isoformat()
    save_campaigns(data)


def cmd_pending(args):
    """Show all pending campaign steps sorted by time."""
    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    pending = []

    for lead, campaign in campaigns.items():
        if campaign["status"] != "active":
            continue

        for i, step in enumerate(campaign["steps"]):
            if step["status"] == "pending":
                scheduled = datetime.fromisoformat(step["scheduled"])
                pending.append({
                    "lead": lead,
                    "step": i + 1,
                    "type": step["type"],
                    "template": step["template"],
                    "scheduled": scheduled,
                    "hours_until": (scheduled - datetime.now()).total_seconds() / 3600
                })

    if not pending:
        print("No pending campaign steps")
        return

    # Sort by scheduled time
    pending.sort(key=lambda x: x["scheduled"])

    print(f"Pending Steps: {len(pending)}")
    print("-" * 60)
    print(f"{'Lead':<25} {'Step':<6} {'Type':<6} {'When':<20}")
    print("-" * 60)

    now = datetime.now()
    for p in pending:
        if p["hours_until"] <= 0:
            when = "DUE NOW!"
        else:
            hours = int(p["hours_until"])
            if hours < 24:
                when = f"in {hours}h"
            else:
                days = hours // 24
                when = f"in {days}d"

        print(f"{p['lead']:<25} {p['step']}/{len(campaign['steps'])}   {p['type']:<6} {when:<20}")


def cmd_templates(args):
    """List available templates."""
    templates = load_templates()

    print("Available Templates:")
    print("-" * 40)
    for name, content in templates.items():
        lines = content.strip().split("\n")
        title = lines[0].replace("#", "").strip() if lines else name
        print(f"  {name}: {title}")


def cmd_preview(args):
    """Preview a template."""
    template_name = args.template

    templates = load_templates()
    if template_name not in templates:
        print(f"Template '{template_name}' not found")
        sys.exit(1)

    print(f"=== {template_name} ===")
    print(templates[template_name])


def cmd_exclude(args):
    """Add lead to exclusion list."""
    lead_name = args.lead
    reason = args.reason
    email = args.email

    data = load_campaigns()

    if "exclusions" not in data:
        data["exclusions"] = []

    # Check if already excluded
    for exclusion in data["exclusions"]:
        if exclusion.get("name") == lead_name:
            print(f"⚠️  '{lead_name}' is already in exclusion list")
            print(f"   Reason: {exclusion.get('reason')}")
            return

    exclusion = {
        "name": lead_name,
        "reason": reason,
        "added_at": datetime.now().isoformat()
    }
    if email:
        exclusion["email"] = email

    data["exclusions"].append(exclusion)
    save_campaigns(data)

    print(f"✅ Added '{lead_name}' to exclusion list")
    print(f"   Reason: {reason}")
    if email:
        print(f"   Email: {email}")


def cmd_exclusions(args):
    """List all excluded leads."""
    data = load_campaigns()
    exclusions = data.get("exclusions", [])

    if not exclusions:
        print("No leads in exclusion list")
        return

    print(f"Excluded Leads: {len(exclusions)}")
    print("-" * 60)
    for exclusion in exclusions:
        name = exclusion.get("name", "Unknown")
        reason = exclusion.get("reason", "Unknown")
        email = exclusion.get("email", "")
        added = exclusion.get("added_at", "Unknown")[:10]  # Just date
        email_str = f" ({email})" if email else ""
        print(f"  {name}{email_str}")
        print(f"      Reason: {reason}")
        print(f"      Added: {added}")


def main():
    parser = argparse.ArgumentParser(
        description="Campaign Orchestrator CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a new campaign")
    start_parser.add_argument("template", help="Template name")
    start_parser.add_argument("--lead", required=True, help="Lead/company name")
    start_parser.add_argument("--delay", type=int, help="Override delay in hours")
    start_parser.add_argument("--attio-id", help="Attio deal/company ID")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check campaign status")
    status_parser.add_argument("lead", help="Lead/company name")

    # List command
    subparsers.add_parser("list", help="List all active campaigns")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a campaign")
    stop_parser.add_argument("lead", help="Lead/company name")
    stop_parser.add_argument("--reason", required=True, help="Termination reason")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove lead from campaigns")
    remove_parser.add_argument("lead", help="Lead/company name")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check for responses before next step")
    check_parser.add_argument("lead", help="Lead/company name")

    # Pending command
    subparsers.add_parser("pending", help="Show all pending steps sorted by time")

    # Templates command
    subparsers.add_parser("templates", help="List available templates")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview a template")
    preview_parser.add_argument("template", help="Template name to preview")

    # Exclusions command
    exclude_parser = subparsers.add_parser("exclude", help="Add lead to exclusion list")
    exclude_parser.add_argument("lead", help="Lead name to exclude")
    exclude_parser.add_argument("--reason", required=True, help="Reason for exclusion")
    exclude_parser.add_argument("--email", help="Email to exclude")

    # List exclusions command
    subparsers.add_parser("exclusions", help="List all excluded leads")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "remove":
        cmd_remove(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "pending":
        cmd_pending(args)
    elif args.command == "templates":
        cmd_templates(args)
    elif args.command == "preview":
        cmd_preview(args)
    elif args.command == "exclude":
        cmd_exclude(args)
    elif args.command == "exclusions":
        cmd_exclusions(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
