#!/usr/bin/env python3
"""
Characterize a W&B training run.

Usage:
    characterize_run.py ENTITY/PROJECT/RUN_ID
    characterize_run.py PROJECT/RUN_ID          # uses default entity
    characterize_run.py RUN_ID --project PROJECT [--entity ENTITY]

Analyzes:
    - Loss curve trend
    - Gradient norm health
    - Eval metrics (if present)
    - System metrics (GPU temp/util)
    - Stall detection
    - Progress estimation
"""

import argparse
import sys
from datetime import datetime, timezone
from typing import Optional

import wandb


def get_metric(row: dict, *keys: str) -> Optional[float]:
    """Get first available metric from a list of possible key names."""
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def analyze_loss(history: list[dict]) -> dict:
    """Analyze loss curve from training history."""
    losses = []
    for row in history:
        loss = get_metric(row, "train/loss", "loss", "train_loss", "training_loss")
        if loss is not None:
            losses.append(loss)
    
    if not losses:
        return {"status": "no_data"}
    
    result = {
        "status": "ok",
        "count": len(losses),
        "start": losses[0],
        "current": losses[-1],
        "min": min(losses),
        "max": max(losses),
    }
    
    # Trend analysis
    if len(losses) >= 10:
        first_10 = sum(losses[:10]) / 10
        last_10 = sum(losses[-10:]) / 10
        result["avg_first_10"] = first_10
        result["avg_last_10"] = last_10
        result["pct_change"] = ((last_10 - first_10) / first_10) * 100
        result["decreasing"] = last_10 < first_10
    elif len(losses) >= 2:
        result["pct_change"] = ((losses[-1] - losses[0]) / losses[0]) * 100
        result["decreasing"] = losses[-1] < losses[0]
    
    result["recent"] = losses[-10:] if len(losses) >= 10 else losses
    
    return result


def analyze_gradients(history: list[dict]) -> dict:
    """Analyze gradient norms for health issues."""
    grads = []
    for row in history:
        grad = get_metric(row, "train/grad_norm", "grad_norm", "gradient_norm")
        if grad is not None:
            grads.append(grad)
    
    if not grads:
        return {"status": "no_data"}
    
    result = {
        "status": "ok",
        "count": len(grads),
        "mean": sum(grads) / len(grads),
        "min": min(grads),
        "max": max(grads),
        "current": grads[-1],
    }
    
    # Health check
    if max(grads) > 10:
        result["health"] = "exploding"
        result["health_msg"] = f"⚠️ EXPLODING - max grad norm {max(grads):.2f} > 10"
    elif max(grads) > 5:
        result["health"] = "spiky"
        result["health_msg"] = f"⚠️ SPIKY - max grad norm {max(grads):.2f}, possible instability"
    elif result["mean"] < 0.0001:
        result["health"] = "vanishing"
        result["health_msg"] = f"⚠️ VANISHING - mean grad norm {result['mean']:.6f}"
    else:
        result["health"] = "healthy"
        result["health_msg"] = f"✅ Healthy (range {min(grads):.4f} - {max(grads):.4f})"
    
    return result


def analyze_evals(history: list[dict]) -> dict:
    """Extract eval metrics if present."""
    eval_losses = []
    eval_accs = []
    
    for row in history:
        eval_loss = get_metric(row, "eval/loss", "eval_loss", "validation_loss", "val_loss")
        eval_acc = get_metric(row, "eval/accuracy", "eval_accuracy", "eval/acc", "accuracy")
        if eval_loss is not None:
            eval_losses.append(eval_loss)
        if eval_acc is not None:
            eval_accs.append(eval_acc)
    
    if not eval_losses and not eval_accs:
        return {"status": "no_data"}
    
    result = {"status": "ok"}
    
    if eval_losses:
        result["loss"] = {
            "count": len(eval_losses),
            "current": eval_losses[-1],
            "best": min(eval_losses),
            "recent": eval_losses[-5:] if len(eval_losses) >= 5 else eval_losses,
        }
    
    if eval_accs:
        result["accuracy"] = {
            "count": len(eval_accs),
            "current": eval_accs[-1],
            "best": max(eval_accs),
            "recent": eval_accs[-5:] if len(eval_accs) >= 5 else eval_accs,
        }
    
    return result


def check_stall(run) -> dict:
    """Check if run appears stalled."""
    if not run.heartbeat_at:
        return {"status": "unknown", "msg": "No heartbeat recorded"}
    
    hb = datetime.fromisoformat(run.heartbeat_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    mins_since = (now - hb).total_seconds() / 60
    
    result = {
        "status": "ok",
        "heartbeat_at": run.heartbeat_at,
        "mins_since": mins_since,
    }
    
    if mins_since > 30:
        result["status"] = "stalled"
        result["msg"] = f"🚨 STALLED - no heartbeat in {mins_since:.0f} minutes"
    elif mins_since > 10:
        result["status"] = "warning"
        result["msg"] = f"⚠️ Slow heartbeat - {mins_since:.1f} minutes ago"
    else:
        result["msg"] = f"✅ Active (heartbeat {mins_since:.1f}m ago)"
    
    return result


def get_progress(run, history: list[dict]) -> dict:
    """Get training progress and estimate completion."""
    result = {}
    
    # Get epoch/step from history or summary
    summary = run.summary._json_dict
    
    epoch = get_metric(summary, "train/epoch", "epoch")
    step = get_metric(summary, "train/global_step", "global_step", "step", "_step")
    
    if epoch is not None:
        result["epoch"] = epoch
    if step is not None:
        result["step"] = int(step)
    
    # Runtime
    runtime = summary.get("_runtime", 0)
    result["runtime_hours"] = runtime / 3600
    
    # Try to estimate completion
    config = run.config
    total_epochs = config.get("num_train_epochs", config.get("num_epochs"))
    max_steps = config.get("max_steps", -1)
    
    if total_epochs and epoch:
        result["total_epochs"] = total_epochs
        result["epoch_progress_pct"] = (epoch / total_epochs) * 100
        if epoch > 0:
            est_total_hours = (runtime / 3600) / (epoch / total_epochs)
            result["est_total_hours"] = est_total_hours
            result["est_remaining_hours"] = est_total_hours - (runtime / 3600)
    
    if max_steps > 0 and step:
        result["max_steps"] = max_steps
        result["step_progress_pct"] = (step / max_steps) * 100
    
    return result


def print_report(run, loss: dict, grads: dict, evals: dict, stall: dict, progress: dict):
    """Print the full characterization report."""
    state_emoji = {"running": "🟢", "finished": "✅", "failed": "🔴", "crashed": "💀", "canceled": "⏹️"}
    
    print(f"\n{'='*70}")
    print(f"{state_emoji.get(run.state, '❓')} {run.project}/{run.name}")
    print(f"{'='*70}")
    print(f"   State: {run.state.upper()}")
    print(f"   ID: {run.id}")
    print(f"   Started: {run.created_at}")
    
    # Stall check
    print(f"\n🔄 HEARTBEAT")
    print(f"   {stall['msg']}")
    
    # Progress
    print(f"\n⏱️ PROGRESS")
    print(f"   Runtime: {progress.get('runtime_hours', 0):.2f}h")
    if "epoch" in progress:
        epoch_str = f"Epoch: {progress['epoch']:.2f}"
        if "total_epochs" in progress:
            epoch_str += f" / {progress['total_epochs']} ({progress['epoch_progress_pct']:.1f}%)"
        print(f"   {epoch_str}")
    if "step" in progress:
        step_str = f"Step: {progress['step']}"
        if "max_steps" in progress:
            step_str += f" / {progress['max_steps']} ({progress['step_progress_pct']:.1f}%)"
        print(f"   {step_str}")
    if "est_remaining_hours" in progress:
        print(f"   Est. remaining: {progress['est_remaining_hours']:.1f}h")
    
    # Loss
    print(f"\n📉 LOSS CURVE")
    if loss["status"] == "no_data":
        print("   No loss data logged")
    else:
        print(f"   Samples: {loss['count']}")
        print(f"   Start: {loss['start']:.4f} → Current: {loss['current']:.4f}")
        print(f"   Min: {loss['min']:.4f} | Max: {loss['max']:.4f}")
        if "pct_change" in loss:
            direction = "📉" if loss.get("decreasing") else "📈"
            status = "✅" if loss.get("decreasing") else "⚠️"
            print(f"   {status} Change: {loss['pct_change']:+.1f}% {direction}")
        if "recent" in loss:
            recent_str = " → ".join([f"{l:.4f}" for l in loss["recent"][-5:]])
            print(f"   Recent: {recent_str}")
    
    # Gradients
    print(f"\n📊 GRADIENT NORM")
    if grads["status"] == "no_data":
        print("   No gradient data logged")
    else:
        print(f"   {grads['health_msg']}")
        print(f"   Mean: {grads['mean']:.4f} | Current: {grads['current']:.4f}")
        print(f"   Range: {grads['min']:.4f} - {grads['max']:.4f}")
    
    # Evals
    print(f"\n🎯 EVAL METRICS")
    if evals["status"] == "no_data":
        print("   No eval metrics logged (yet)")
    else:
        if "loss" in evals:
            el = evals["loss"]
            print(f"   Eval Loss: {el['current']:.4f} (best: {el['best']:.4f}, n={el['count']})")
        if "accuracy" in evals:
            ea = evals["accuracy"]
            print(f"   Eval Acc: {ea['current']:.4f} (best: {ea['best']:.4f}, n={ea['count']})")
    
    # Config highlights
    print(f"\n⚙️ CONFIG")
    config = run.config
    config_keys = [
        "model_name", "model_name_or_path", "base_model",
        "learning_rate", "lr",
        "per_device_train_batch_size", "batch_size", "train_batch_size",
        "num_train_epochs", "num_epochs", "epochs",
        "max_steps",
        "gradient_accumulation_steps",
        "warmup_steps", "warmup_ratio",
    ]
    shown = 0
    for key in config_keys:
        if key in config and shown < 8:
            print(f"   {key}: {config[key]}")
            shown += 1
    
    # Overall assessment
    print(f"\n{'='*70}")
    print("📋 SUMMARY")
    
    issues = []
    if stall["status"] == "stalled":
        issues.append("Run appears stalled")
    if grads["status"] == "ok" and grads["health"] != "healthy":
        issues.append(f"Gradient issues ({grads['health']})")
    if loss["status"] == "ok" and not loss.get("decreasing", True):
        issues.append("Loss not decreasing")
    
    if not issues:
        print("   ✅ Run looks healthy")
    else:
        for issue in issues:
            print(f"   ⚠️ {issue}")
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Characterize a W&B training run")
    parser.add_argument("run_path", help="Run path: ENTITY/PROJECT/RUN_ID or PROJECT/RUN_ID or RUN_ID")
    parser.add_argument("--project", "-p", help="Project name (if not in run_path)")
    parser.add_argument("--entity", "-e", help="Entity name (if not in run_path)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    # Parse run path
    parts = args.run_path.split("/")
    if len(parts) == 3:
        entity, project, run_id = parts
    elif len(parts) == 2:
        entity = args.entity
        project, run_id = parts
    elif len(parts) == 1:
        entity = args.entity
        project = args.project
        run_id = parts[0]
    else:
        print(f"Invalid run path: {args.run_path}", file=sys.stderr)
        sys.exit(1)
    
    if not project:
        print("Project required. Use ENTITY/PROJECT/RUN_ID or --project", file=sys.stderr)
        sys.exit(1)
    
    # Build full path
    if entity:
        full_path = f"{entity}/{project}/{run_id}"
    else:
        full_path = f"{project}/{run_id}"
    
    # Fetch run
    api = wandb.Api()
    try:
        run = api.run(full_path)
    except wandb.errors.CommError as e:
        print(f"Error fetching run: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch history
    history = list(run.scan_history())
    
    # Analyze
    loss = analyze_loss(history)
    grads = analyze_gradients(history)
    evals = analyze_evals(history)
    stall = check_stall(run)
    progress = get_progress(run, history)
    
    if args.json:
        import json
        output = {
            "run": {"id": run.id, "name": run.name, "project": run.project, "state": run.state},
            "loss": loss,
            "gradients": grads,
            "evals": evals,
            "stall": stall,
            "progress": progress,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_report(run, loss, grads, evals, stall, progress)


if __name__ == "__main__":
    main()
