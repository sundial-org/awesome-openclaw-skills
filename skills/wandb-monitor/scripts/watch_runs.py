#!/usr/bin/env python3
"""
Watch all running W&B jobs with quick health summaries.

Usage:
    watch_runs.py ENTITY [--projects PROJECT1,PROJECT2,...]
    watch_runs.py ENTITY --all-projects
    watch_runs.py  # uses default entity from config

Designed for morning briefings and periodic monitoring.
"""

import argparse
import sys
from datetime import datetime, timezone
from typing import Optional

import wandb


def get_metric(row: dict, *keys: str) -> Optional[float]:
    """Get first available metric from possible key names."""
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def quick_health_check(run) -> dict:
    """Quick health assessment without full history scan."""
    result = {
        "run_id": run.id,
        "name": run.name,
        "project": run.project,
        "state": run.state,
        "issues": [],
        "status": "healthy",
    }
    
    # Runtime
    summary = run.summary._json_dict
    runtime = summary.get("_runtime", 0)
    result["runtime_hours"] = runtime / 3600
    
    # Heartbeat check
    if run.heartbeat_at:
        hb = datetime.fromisoformat(run.heartbeat_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        mins_since = (now - hb).total_seconds() / 60
        result["heartbeat_mins"] = mins_since
        if mins_since > 30:
            result["issues"].append(f"STALLED ({mins_since:.0f}m no heartbeat)")
            result["status"] = "critical"
        elif mins_since > 10:
            result["issues"].append(f"Slow heartbeat ({mins_since:.1f}m)")
            result["status"] = "warning"
    
    # Loss from summary
    loss = get_metric(summary, "train/loss", "loss", "train_loss")
    if loss is not None:
        result["loss"] = loss
    
    # Gradient norm from summary
    grad = get_metric(summary, "train/grad_norm", "grad_norm")
    if grad is not None:
        result["grad_norm"] = grad
        if grad > 10:
            result["issues"].append(f"Exploding gradients ({grad:.2f})")
            result["status"] = "critical" if result["status"] != "critical" else result["status"]
        elif grad > 5:
            result["issues"].append(f"High gradients ({grad:.2f})")
            if result["status"] == "healthy":
                result["status"] = "warning"
    
    # Progress
    epoch = get_metric(summary, "train/epoch", "epoch")
    step = get_metric(summary, "train/global_step", "global_step", "step")
    if epoch is not None:
        result["epoch"] = epoch
    if step is not None:
        result["step"] = int(step)
    
    # Config for context
    config = run.config
    total_epochs = config.get("num_train_epochs", config.get("num_epochs"))
    if total_epochs and epoch:
        result["progress_pct"] = (epoch / total_epochs) * 100
    
    return result


def get_running_runs(api, entity: str, projects: Optional[list[str]] = None) -> list:
    """Get all running runs across specified projects."""
    running = []
    
    if projects:
        project_list = projects
    else:
        # Get all projects for entity
        try:
            project_list = [p.name for p in api.projects(entity)]
        except Exception:
            project_list = []
    
    for project in project_list:
        try:
            runs = api.runs(f"{entity}/{project}", {"state": "running"}, per_page=20)
            running.extend(list(runs))
        except Exception:
            pass  # Project might not exist or no access
    
    return running


def get_recent_finished(api, entity: str, projects: Optional[list[str]] = None, hours: int = 24) -> list:
    """Get recently finished/failed runs."""
    from datetime import timedelta
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
    
    finished = []
    
    if projects:
        project_list = projects
    else:
        try:
            project_list = [p.name for p in api.projects(entity)]
        except Exception:
            project_list = []
    
    for project in project_list:
        try:
            # Get finished runs
            runs = api.runs(f"{entity}/{project}", {
                "$and": [
                    {"state": {"$in": ["finished", "failed", "crashed"]}},
                    {"created_at": {"$gt": cutoff_str}}
                ]
            }, per_page=10)
            finished.extend(list(runs))
        except Exception:
            pass
    
    return finished


def print_report(running: list, recent: list, entity: str):
    """Print the watch report."""
    print(f"\n{'='*70}")
    print(f"🔭 W&B WATCH - {entity}")
    print(f"{'='*70}")
    
    # Running jobs
    print(f"\n🟢 RUNNING ({len(running)})")
    print("-" * 70)
    
    if not running:
        print("   No jobs currently running")
    else:
        for run in running:
            health = quick_health_check(run)
            
            # Status emoji
            status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "🚨"}
            emoji = status_emoji.get(health["status"], "❓")
            
            # Progress string
            progress = ""
            if "progress_pct" in health:
                progress = f" ({health['progress_pct']:.0f}%)"
            elif "epoch" in health:
                progress = f" (ep {health['epoch']:.2f})"
            elif "step" in health:
                progress = f" (step {health['step']})"
            
            # Loss string
            loss_str = f" loss={health['loss']:.4f}" if "loss" in health else ""
            
            print(f"   {emoji} {health['project']}/{health['name']}{progress}{loss_str}")
            print(f"      Runtime: {health['runtime_hours']:.1f}h | ID: {health['run_id']}")
            
            if health["issues"]:
                for issue in health["issues"]:
                    print(f"      ⚠️ {issue}")
            print()
    
    # Recent finished/failed
    failed = [r for r in recent if r.state in ("failed", "crashed")]
    finished = [r for r in recent if r.state == "finished"]
    
    if failed:
        print(f"\n🔴 FAILED/CRASHED (last 24h): {len(failed)}")
        print("-" * 70)
        for run in failed[:5]:
            print(f"   💀 {run.project}/{run.name} ({run.state})")
            print(f"      ID: {run.id} | Created: {run.created_at}")
    
    if finished:
        print(f"\n✅ FINISHED (last 24h): {len(finished)}")
        print("-" * 70)
        for run in finished[:5]:
            summary = run.summary._json_dict
            loss = get_metric(summary, "train/loss", "loss", "eval/loss")
            loss_str = f" | Final loss: {loss:.4f}" if loss else ""
            print(f"   ✓ {run.project}/{run.name}{loss_str}")
    
    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Watch W&B training runs")
    parser.add_argument("entity", nargs="?", default="chrisvoncsefalvay", help="W&B entity (username/org)")
    parser.add_argument("--projects", "-p", help="Comma-separated project names")
    parser.add_argument("--all-projects", "-a", action="store_true", help="Check all projects")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back for finished runs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    api = wandb.Api()
    
    projects = None
    if args.projects:
        projects = [p.strip() for p in args.projects.split(",")]
    elif not args.all_projects:
        # Default projects to check
        projects = ["med_school_llama", "llamafactory", "grpo-clinical-reasoning", "dx-reasoning-qwen", "usmle-reasoning"]
    
    running = get_running_runs(api, args.entity, projects)
    recent = get_recent_finished(api, args.entity, projects, args.hours)
    
    if args.json:
        import json
        output = {
            "entity": args.entity,
            "running": [quick_health_check(r) for r in running],
            "recent_failed": [{"id": r.id, "name": r.name, "project": r.project, "state": r.state} 
                            for r in recent if r.state in ("failed", "crashed")],
            "recent_finished": [{"id": r.id, "name": r.name, "project": r.project} 
                               for r in recent if r.state == "finished"],
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_report(running, recent, args.entity)


if __name__ == "__main__":
    main()
