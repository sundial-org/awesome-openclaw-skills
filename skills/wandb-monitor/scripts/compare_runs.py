#!/usr/bin/env python3
"""
Compare two W&B runs side-by-side.

Usage:
    compare_runs.py ENTITY/PROJECT/RUN_A ENTITY/PROJECT/RUN_B
    compare_runs.py RUN_A RUN_B --project PROJECT [--entity ENTITY]

Compares:
    - Config differences
    - Loss curves at same steps
    - Final metrics
    - Performance (tokens/sec, runtime)
"""

import argparse
import sys
from typing import Optional

import wandb


def get_metric(data: dict, *keys: str) -> Optional[float]:
    """Get first available metric from possible key names."""
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def parse_run_path(path: str, default_project: str = None, default_entity: str = None) -> tuple[str, str, str]:
    """Parse run path into (entity, project, run_id)."""
    parts = path.split("/")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return default_entity, parts[0], parts[1]
    elif len(parts) == 1:
        return default_entity, default_project, parts[0]
    else:
        raise ValueError(f"Invalid run path: {path}")


def get_loss_at_steps(history: list[dict], steps: list[int]) -> dict[int, float]:
    """Get loss values at specific steps."""
    result = {}
    step_key = None
    loss_key = None
    
    # Find the right keys
    if history:
        row = history[0]
        for k in ["_step", "step", "global_step", "train/global_step"]:
            if k in row:
                step_key = k
                break
        for k in ["train/loss", "loss", "train_loss"]:
            if k in row:
                loss_key = k
                break
    
    if not step_key or not loss_key:
        return result
    
    # Build step -> loss map
    step_loss = {}
    for row in history:
        s = row.get(step_key)
        l = row.get(loss_key)
        if s is not None and l is not None:
            step_loss[int(s)] = l
    
    # Find closest step for each target
    for target in steps:
        if target in step_loss:
            result[target] = step_loss[target]
        else:
            # Find closest
            closest = min(step_loss.keys(), key=lambda x: abs(x - target), default=None)
            if closest and abs(closest - target) < target * 0.1:  # Within 10%
                result[target] = step_loss[closest]
    
    return result


def compare_configs(config_a: dict, config_b: dict) -> dict:
    """Compare two configs and return differences."""
    all_keys = set(config_a.keys()) | set(config_b.keys())
    
    # Important keys to highlight
    important = {
        "learning_rate", "lr", "num_train_epochs", "num_epochs", "max_steps",
        "per_device_train_batch_size", "batch_size", "gradient_accumulation_steps",
        "warmup_steps", "warmup_ratio", "weight_decay", "adam_epsilon",
        "model_name", "model_name_or_path", "base_model",
        "lora_r", "lora_alpha", "lora_dropout",
        "max_seq_length", "max_length",
    }
    
    same = {}
    different = {}
    only_a = {}
    only_b = {}
    
    for key in all_keys:
        in_a = key in config_a
        in_b = key in config_b
        
        if in_a and in_b:
            if config_a[key] == config_b[key]:
                if key in important:
                    same[key] = config_a[key]
            else:
                different[key] = {"a": config_a[key], "b": config_b[key]}
        elif in_a:
            if key in important:
                only_a[key] = config_a[key]
        else:
            if key in important:
                only_b[key] = config_b[key]
    
    return {
        "same": same,
        "different": different,
        "only_a": only_a,
        "only_b": only_b,
    }


def print_comparison(run_a, run_b, history_a: list, history_b: list, config_diff: dict):
    """Print side-by-side comparison."""
    print(f"\n{'='*70}")
    print("🔬 RUN COMPARISON")
    print(f"{'='*70}")
    
    # Basic info
    print(f"\n{'Run A':<35} {'Run B':<35}")
    print(f"{'-'*35} {'-'*35}")
    print(f"{run_a.project}/{run_a.name:<25} {run_b.project}/{run_b.name:<25}")
    print(f"ID: {run_a.id:<29} ID: {run_b.id:<29}")
    print(f"State: {run_a.state:<27} State: {run_b.state:<27}")
    
    # Runtime
    summary_a = run_a.summary._json_dict
    summary_b = run_b.summary._json_dict
    runtime_a = summary_a.get("_runtime", 0) / 3600
    runtime_b = summary_b.get("_runtime", 0) / 3600
    print(f"Runtime: {runtime_a:<24.2f}h Runtime: {runtime_b:<24.2f}h")
    
    # Config differences
    print(f"\n⚙️ CONFIG DIFFERENCES")
    print("-" * 70)
    if config_diff["different"]:
        for key, vals in config_diff["different"].items():
            print(f"   {key}:")
            print(f"      A: {vals['a']}")
            print(f"      B: {vals['b']}")
    else:
        print("   No differences in key config values")
    
    if config_diff["only_a"]:
        print(f"\n   Only in A: {config_diff['only_a']}")
    if config_diff["only_b"]:
        print(f"\n   Only in B: {config_diff['only_b']}")
    
    # Loss comparison
    print(f"\n📉 LOSS COMPARISON")
    print("-" * 70)
    
    # Get losses at various steps
    loss_a = [get_metric(r, "train/loss", "loss") for r in history_a if get_metric(r, "train/loss", "loss")]
    loss_b = [get_metric(r, "train/loss", "loss") for r in history_b if get_metric(r, "train/loss", "loss")]
    
    if loss_a and loss_b:
        print(f"   {'Metric':<20} {'Run A':<20} {'Run B':<20} {'Winner':<10}")
        print(f"   {'-'*20} {'-'*20} {'-'*20} {'-'*10}")
        
        # Starting loss
        winner = "A" if loss_a[0] < loss_b[0] else "B" if loss_b[0] < loss_a[0] else "Tie"
        print(f"   {'Start loss':<20} {loss_a[0]:<20.4f} {loss_b[0]:<20.4f} {winner:<10}")
        
        # Current/final loss
        winner = "A ✓" if loss_a[-1] < loss_b[-1] else "B ✓" if loss_b[-1] < loss_a[-1] else "Tie"
        print(f"   {'Current loss':<20} {loss_a[-1]:<20.4f} {loss_b[-1]:<20.4f} {winner:<10}")
        
        # Min loss
        min_a, min_b = min(loss_a), min(loss_b)
        winner = "A ✓" if min_a < min_b else "B ✓" if min_b < min_a else "Tie"
        print(f"   {'Min loss':<20} {min_a:<20.4f} {min_b:<20.4f} {winner:<10}")
        
        # Improvement %
        imp_a = (1 - loss_a[-1] / loss_a[0]) * 100 if loss_a[0] > 0 else 0
        imp_b = (1 - loss_b[-1] / loss_b[0]) * 100 if loss_b[0] > 0 else 0
        winner = "A ✓" if imp_a > imp_b else "B ✓" if imp_b > imp_a else "Tie"
        print(f"   {'Improvement %':<20} {imp_a:<20.1f} {imp_b:<20.1f} {winner:<10}")
    else:
        print("   Insufficient loss data for comparison")
    
    # Gradient comparison
    print(f"\n📊 GRADIENT NORM")
    print("-" * 70)
    grads_a = [get_metric(r, "train/grad_norm", "grad_norm") for r in history_a if get_metric(r, "train/grad_norm", "grad_norm")]
    grads_b = [get_metric(r, "train/grad_norm", "grad_norm") for r in history_b if get_metric(r, "train/grad_norm", "grad_norm")]
    
    if grads_a and grads_b:
        mean_a = sum(grads_a) / len(grads_a)
        mean_b = sum(grads_b) / len(grads_b)
        print(f"   Mean: {mean_a:.4f} (A) vs {mean_b:.4f} (B)")
        print(f"   Max:  {max(grads_a):.4f} (A) vs {max(grads_b):.4f} (B)")
    
    # Eval metrics
    print(f"\n🎯 EVAL METRICS")
    print("-" * 70)
    eval_loss_a = get_metric(summary_a, "eval/loss", "eval_loss")
    eval_loss_b = get_metric(summary_b, "eval/loss", "eval_loss")
    eval_acc_a = get_metric(summary_a, "eval/accuracy", "eval_acc", "accuracy")
    eval_acc_b = get_metric(summary_b, "eval/accuracy", "eval_acc", "accuracy")
    
    if eval_loss_a or eval_loss_b:
        print(f"   Eval Loss: {eval_loss_a or 'N/A'} (A) vs {eval_loss_b or 'N/A'} (B)")
    if eval_acc_a or eval_acc_b:
        print(f"   Eval Acc:  {eval_acc_a or 'N/A'} (A) vs {eval_acc_b or 'N/A'} (B)")
    if not eval_loss_a and not eval_loss_b and not eval_acc_a and not eval_acc_b:
        print("   No eval metrics available")
    
    # Performance
    print(f"\n⚡ PERFORMANCE")
    print("-" * 70)
    tps_a = get_metric(summary_a, "train/train_tokens_per_second", "tokens_per_second")
    tps_b = get_metric(summary_b, "train/train_tokens_per_second", "tokens_per_second")
    if tps_a or tps_b:
        print(f"   Tokens/sec: {tps_a or 'N/A'} (A) vs {tps_b or 'N/A'} (B)")
    
    steps_a = get_metric(summary_a, "train/global_step", "global_step", "_step")
    steps_b = get_metric(summary_b, "train/global_step", "global_step", "_step")
    if steps_a and steps_b and runtime_a > 0 and runtime_b > 0:
        sph_a = steps_a / runtime_a
        sph_b = steps_b / runtime_b
        print(f"   Steps/hour: {sph_a:.1f} (A) vs {sph_b:.1f} (B)")
    
    # Verdict
    print(f"\n{'='*70}")
    print("📋 VERDICT")
    print("-" * 70)
    
    if loss_a and loss_b:
        if loss_a[-1] < loss_b[-1]:
            diff = ((loss_b[-1] - loss_a[-1]) / loss_b[-1]) * 100
            print(f"   🏆 Run A has {diff:.1f}% lower loss")
        elif loss_b[-1] < loss_a[-1]:
            diff = ((loss_a[-1] - loss_b[-1]) / loss_a[-1]) * 100
            print(f"   🏆 Run B has {diff:.1f}% lower loss")
        else:
            print("   🤝 Runs are performing similarly")
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Compare two W&B runs")
    parser.add_argument("run_a", help="First run path")
    parser.add_argument("run_b", help="Second run path")
    parser.add_argument("--project", "-p", help="Default project")
    parser.add_argument("--entity", "-e", help="Default entity")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    api = wandb.Api()
    
    # Parse run paths
    try:
        entity_a, project_a, run_id_a = parse_run_path(args.run_a, args.project, args.entity)
        entity_b, project_b, run_id_b = parse_run_path(args.run_b, args.project, args.entity)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Build paths
    path_a = f"{entity_a}/{project_a}/{run_id_a}" if entity_a else f"{project_a}/{run_id_a}"
    path_b = f"{entity_b}/{project_b}/{run_id_b}" if entity_b else f"{project_b}/{run_id_b}"
    
    # Fetch runs
    try:
        run_a = api.run(path_a)
        run_b = api.run(path_b)
    except wandb.errors.CommError as e:
        print(f"Error fetching runs: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch histories
    history_a = list(run_a.scan_history())
    history_b = list(run_b.scan_history())
    
    # Compare configs
    config_diff = compare_configs(run_a.config, run_b.config)
    
    if args.json:
        import json
        output = {
            "run_a": {"id": run_a.id, "name": run_a.name, "project": run_a.project, "state": run_a.state},
            "run_b": {"id": run_b.id, "name": run_b.name, "project": run_b.project, "state": run_b.state},
            "config_diff": config_diff,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_comparison(run_a, run_b, history_a, history_b, config_diff)


if __name__ == "__main__":
    main()
