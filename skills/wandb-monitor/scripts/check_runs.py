#!/usr/bin/env python3
"""
Check W&B runs status.

Usage:
    python check_runs.py ENTITY/PROJECT [--status STATUS] [--hours HOURS] [--json]

Examples:
    python check_runs.py myteam/training --status failed --hours 24
    python check_runs.py myteam/training --status running
    python check_runs.py myteam/training --hours 48 --json
"""

import argparse
import json
from datetime import datetime, timedelta, timezone

import wandb


def main():
    parser = argparse.ArgumentParser(description="Check W&B runs")
    parser.add_argument("path", help="entity/project path")
    parser.add_argument("--status", choices=["running", "finished", "failed", "crashed", "canceled"],
                        help="Filter by status")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default: 24)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    api = wandb.Api()
    
    # Build filters
    filters = {}
    if args.status:
        filters["state"] = args.status
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    
    try:
        runs = api.runs(args.path, filters=filters if filters else None)
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return 1

    results = []
    for run in runs:
        created = datetime.fromisoformat(run.created_at.replace("Z", "+00:00"))
        if created < cutoff:
            continue
            
        results.append({
            "id": run.id,
            "name": run.name,
            "state": run.state,
            "created_at": run.created_at,
            "url": run.url,
        })

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            status_msg = f" with status={args.status}" if args.status else ""
            print(f"No runs found{status_msg} in last {args.hours}h")
        else:
            print(f"Found {len(results)} run(s) in last {args.hours}h:\n")
            for r in results:
                status_icon = {"running": "🔄", "finished": "✅", "failed": "❌", "crashed": "💥", "canceled": "⏹️"}.get(r["state"], "❓")
                print(f"  {status_icon} {r['name']} ({r['state']})")
                print(f"     ID: {r['id']}")
                print(f"     Created: {r['created_at']}")
                print()

    # Exit code: 1 if any failed/crashed runs found
    failed_count = sum(1 for r in results if r["state"] in ("failed", "crashed"))
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    exit(main())
