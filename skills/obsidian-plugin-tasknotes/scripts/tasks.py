#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "python-dotenv"]
# ///
"""
TaskNotes CLI - Manage Obsidian tasks via TaskNotes plugin API.

Usage:
    python3 tasks.py list [--status STATUS] [--project PROJECT] [--limit N]
    python3 tasks.py create "Title" [--project PROJECT] [--priority PRIORITY] [--status STATUS]
    python3 tasks.py update "Tasks/file.md" [--status STATUS] [--priority PRIORITY]
    python3 tasks.py delete "Tasks/file.md"
    python3 tasks.py stats
    python3 tasks.py options

Environment:
    TASKNOTES_API_KEY - API authentication token (optional, depends on TaskNotes settings)
    TASKNOTES_API_PORT - API port (default: 8080)
"""

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from vault root
SCRIPT_DIR = Path(__file__).parent
VAULT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
load_dotenv(VAULT_ROOT / ".env")

API_KEY = os.getenv("TASKNOTES_API_KEY")
API_PORT = os.getenv("TASKNOTES_API_PORT", "8080")
BASE_URL = f"http://localhost:{API_PORT}/api"


def get_headers():
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def api_request(method: str, endpoint: str, params: dict = None, data: dict = None):
    """Make API request and return JSON response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(
            method, url, headers=get_headers(), params=params, json=data, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to TaskNotes API. Is Obsidian running with TaskNotes enabled?"}
    except requests.exceptions.HTTPError as e:
        try:
            return response.json()
        except:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def list_tasks(args):
    """List tasks with optional filters."""
    params = {}
    if args.status:
        params["status"] = args.status
    if args.project:
        params["project"] = args.project
    if args.priority:
        params["priority"] = args.priority
    if args.limit:
        params["limit"] = args.limit
    if args.overdue:
        params["overdue"] = "true"

    result = api_request("GET", "/tasks", params=params)

    if "error" in result:
        print(json.dumps(result, indent=2))
        return

    tasks = result.get("data", {}).get("tasks", [])

    if args.table:
        # Human-readable table format
        if not tasks:
            print("No tasks found.")
            return
        print(f"{'Status':<15} {'Priority':<10} {'Title':<50} {'Project'}")
        print("-" * 100)
        for t in tasks:
            status = t.get("status", "none")
            priority = t.get("priority", "none")
            title = t.get("title", "")[:48]
            projects = ", ".join(t.get("projects", []))[:30]
            print(f"{status:<15} {priority:<10} {title:<50} {projects}")
        print(f"\nTotal: {len(tasks)} tasks")
    else:
        # JSON output for agents
        output = {
            "success": True,
            "count": len(tasks),
            "tasks": [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "status": t.get("status"),
                    "priority": t.get("priority"),
                    "projects": t.get("projects", []),
                    "due": t.get("due"),
                    "scheduled": t.get("scheduled"),
                }
                for t in tasks
            ],
        }
        print(json.dumps(output, indent=2))


def create_task(args):
    """Create a new task."""
    data = {"title": args.title}

    if args.project:
        # Ensure project is wrapped in [[ ]] if not already
        project = args.project
        if not project.startswith("[["):
            project = f"[[{project}]]"
        data["projects"] = [project]

    if args.priority:
        data["priority"] = args.priority
    if args.status:
        data["status"] = args.status
    if args.due:
        data["due"] = args.due
    if args.scheduled:
        data["scheduled"] = args.scheduled
    if args.contexts:
        data["contexts"] = args.contexts.split(",")
    if args.time_estimate:
        data["timeEstimate"] = args.time_estimate
    if args.details:
        data["details"] = args.details

    result = api_request("POST", "/tasks", data=data)

    if args.table:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("success"):
            task = result.get("data", {})
            print(f"Created task: {task.get('title')}")
            print(f"  Path: {task.get('path')}")
            print(f"  Status: {task.get('status')}")
            print(f"  Priority: {task.get('priority')}")
    else:
        print(json.dumps(result, indent=2))


def update_task(args):
    """Update an existing task."""
    task_id = urllib.parse.quote(args.task_id, safe="")
    data = {}

    if args.status:
        data["status"] = args.status
    if args.priority:
        data["priority"] = args.priority
    if args.title:
        data["title"] = args.title
    if args.due:
        data["due"] = args.due
    if args.scheduled:
        data["scheduled"] = args.scheduled
    if args.details:
        data["details"] = args.details

    if not data:
        print(json.dumps({"error": "No updates specified"}))
        return

    result = api_request("PUT", f"/tasks/{task_id}", data=data)

    if args.table:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("success"):
            print(f"Updated task: {args.task_id}")
            task = result.get("data", {})
            if args.status:
                print(f"  New status: {task.get('status')}")
    else:
        print(json.dumps(result, indent=2))


def delete_task(args):
    """Delete a task."""
    task_id = urllib.parse.quote(args.task_id, safe="")
    result = api_request("DELETE", f"/tasks/{task_id}")

    if args.table:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("success"):
            print(f"Deleted task: {args.task_id}")
    else:
        print(json.dumps(result, indent=2))


def get_stats(args):
    """Get task statistics."""
    result = api_request("GET", "/stats")

    if args.table:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("success"):
            data = result.get("data", {})
            print("Task Statistics:")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Active: {data.get('active', 0)}")
            print(f"  Completed: {data.get('completed', 0)}")
            print(f"  Overdue: {data.get('overdue', 0)}")
            print(f"  Archived: {data.get('archived', 0)}")
    else:
        print(json.dumps(result, indent=2))


def get_options(args):
    """Get available filter options (projects, statuses, etc.)."""
    result = api_request("GET", "/filter-options")

    if args.table:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("success"):
            data = result.get("data", {})
            print("Available Projects:")
            for p in data.get("projects", []):
                print(f"  - {p}")
            print("\nAvailable Statuses:")
            for s in data.get("statuses", []):
                print(f"  - {s}")
            print("\nAvailable Priorities:")
            for p in data.get("priorities", []):
                print(f"  - {p}")
    else:
        print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="TaskNotes CLI")
    parser.add_argument("--table", action="store_true", help="Human-readable output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument("--priority", help="Filter by priority")
    list_parser.add_argument("--limit", type=int, help="Limit results")
    list_parser.add_argument("--overdue", action="store_true", help="Show overdue only")
    list_parser.add_argument("--table", action="store_true", help="Human-readable output")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--project", help="Project/goal name")
    create_parser.add_argument("--priority", help="Task priority (check your TaskNotes config for values)")
    create_parser.add_argument("--status", help="Task status (check your TaskNotes config for values)")
    create_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    create_parser.add_argument("--scheduled", help="Scheduled date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    create_parser.add_argument("--contexts", help="Comma-separated contexts")
    create_parser.add_argument("--time-estimate", type=int, help="Time estimate in minutes")
    create_parser.add_argument("--details", help="Task description/body content (agent handoff context)")
    create_parser.add_argument("--table", action="store_true", help="Human-readable output")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update task")
    update_parser.add_argument("task_id", help="Task file path (e.g., Tasks/my-task.md)")
    update_parser.add_argument("--status", help="Task status (check your TaskNotes config for values)")
    update_parser.add_argument("--priority", help="Task priority (check your TaskNotes config for values)")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    update_parser.add_argument("--scheduled", help="Scheduled date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    update_parser.add_argument("--details", help="Task description/body content (agent handoff context)")
    update_parser.add_argument("--table", action="store_true", help="Human-readable output")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete task")
    delete_parser.add_argument("task_id", help="Task file path")
    delete_parser.add_argument("--table", action="store_true", help="Human-readable output")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get statistics")
    stats_parser.add_argument("--table", action="store_true", help="Human-readable output")

    # Options command
    options_parser = subparsers.add_parser("options", help="Get filter options")
    options_parser.add_argument("--table", action="store_true", help="Human-readable output")

    args = parser.parse_args()

    commands = {
        "list": list_tasks,
        "create": create_task,
        "update": update_task,
        "delete": delete_task,
        "stats": get_stats,
        "options": get_options,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
