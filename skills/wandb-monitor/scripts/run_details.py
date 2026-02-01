#!/usr/bin/env python3
"""
Get details for a specific W&B run.

Usage:
    python run_details.py ENTITY/PROJECT RUN_ID [--metrics KEY1,KEY2] [--json]

Examples:
    python run_details.py myteam/training abc123
    python run_details.py myteam/training abc123 --metrics loss,accuracy
    python run_details.py myteam/training abc123 --json
"""

import argparse
import json

import wandb


def main():
    parser = argparse.ArgumentParser(description="Get W&B run details")
    parser.add_argument("path", help="entity/project path")
    parser.add_argument("run_id", help="Run ID")
    parser.add_argument("--metrics", help="Comma-separated metric keys to fetch history")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    api = wandb.Api()
    
    try:
        run = api.run(f"{args.path}/{args.run_id}")
    except Exception as e:
        print(f"Error fetching run: {e}")
        return 1

    result = {
        "id": run.id,
        "name": run.name,
        "state": run.state,
        "created_at": run.created_at,
        "updated_at": getattr(run, "updated_at", None),
        "url": run.url,
        "config": dict(run.config),
        "summary": dict(run.summary),
        "tags": run.tags,
    }
    
    # Fetch specific metrics history if requested
    if args.metrics:
        keys = [k.strip() for k in args.metrics.split(",")]
        try:
            history = run.history(keys=keys)
            result["history"] = history.to_dict(orient="records") if not history.empty else []
        except Exception as e:
            result["history_error"] = str(e)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        status_icon = {"running": "🔄", "finished": "✅", "failed": "❌", "crashed": "💥", "canceled": "⏹️"}.get(run.state, "❓")
        print(f"{status_icon} {run.name}")
        print(f"   State: {run.state}")
        print(f"   ID: {run.id}")
        print(f"   Created: {run.created_at}")
        print(f"   URL: {run.url}")
        print()
        
        if run.tags:
            print(f"   Tags: {', '.join(run.tags)}")
            print()
        
        if run.config:
            print("   Config:")
            for k, v in list(run.config.items())[:10]:  # Limit to 10
                print(f"      {k}: {v}")
            if len(run.config) > 10:
                print(f"      ... and {len(run.config) - 10} more")
            print()
        
        if run.summary:
            print("   Summary (final metrics):")
            for k, v in list(run.summary.items())[:15]:  # Limit to 15
                if not k.startswith("_"):
                    print(f"      {k}: {v}")
            print()

    return 0


if __name__ == "__main__":
    exit(main())
