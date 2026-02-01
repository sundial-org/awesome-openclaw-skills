---
name: wandb
description: Monitor and analyze Weights & Biases training runs. Use when checking training status, detecting failures, analyzing loss curves, comparing runs, or monitoring experiments. Triggers on "wandb", "training runs", "how's training", "did my run finish", "any failures", "check experiments", "loss curve", "gradient norm", "compare runs".
---

# Weights & Biases

Monitor, analyze, and compare W&B training runs.

## Setup

```bash
wandb login
# Or set WANDB_API_KEY in environment
```

## Scripts

### Characterize a Run (Full Health Analysis)

```bash
~/clawd/venv/bin/python3 ~/clawd/skills/wandb/scripts/characterize_run.py ENTITY/PROJECT/RUN_ID
```

Analyzes:
- Loss curve trend (start → current, % change, direction)
- Gradient norm health (exploding/vanishing detection)  
- Eval metrics (if present)
- Stall detection (heartbeat age)
- Progress & ETA estimate
- Config highlights
- Overall health verdict

Options: `--json` for machine-readable output.

### Watch All Running Jobs

```bash
~/clawd/venv/bin/python3 ~/clawd/skills/wandb/scripts/watch_runs.py ENTITY [--projects p1,p2]
```

Quick health summary of all running jobs plus recent failures/completions. Ideal for morning briefings.

Options:
- `--projects p1,p2` — Specific projects to check
- `--all-projects` — Check all projects
- `--hours N` — Hours to look back for finished runs (default: 24)
- `--json` — Machine-readable output

### Compare Two Runs

```bash
~/clawd/venv/bin/python3 ~/clawd/skills/wandb/scripts/compare_runs.py ENTITY/PROJECT/RUN_A ENTITY/PROJECT/RUN_B
```

Side-by-side comparison:
- Config differences (highlights important params)
- Loss curves at same steps
- Gradient norm comparison
- Eval metrics
- Performance (tokens/sec, steps/hour)
- Winner verdict

## Python API Quick Reference

```python
import wandb
api = wandb.Api()

# Get runs
runs = api.runs("entity/project", {"state": "running"})

# Run properties
run.state      # running | finished | failed | crashed | canceled
run.name       # display name
run.id         # unique identifier
run.summary    # final/current metrics
run.config     # hyperparameters
run.heartbeat_at # stall detection

# Get history
history = list(run.scan_history(keys=["train/loss", "train/grad_norm"]))
```

## Metric Key Variations

Scripts handle these automatically:
- Loss: `train/loss`, `loss`, `train_loss`, `training_loss`
- Gradients: `train/grad_norm`, `grad_norm`, `gradient_norm`
- Steps: `train/global_step`, `global_step`, `step`, `_step`
- Eval: `eval/loss`, `eval_loss`, `eval/accuracy`, `eval_acc`

## Health Thresholds

- **Gradients > 10**: Exploding (critical)
- **Gradients > 5**: Spiky (warning)
- **Gradients < 0.0001**: Vanishing (warning)
- **Heartbeat > 30min**: Stalled (critical)
- **Heartbeat > 10min**: Slow (warning)

## Integration Notes

For morning briefings, use `watch_runs.py --json` and parse the output.

For detailed analysis of a specific run, use `characterize_run.py`.

For A/B testing or hyperparameter comparisons, use `compare_runs.py`.
