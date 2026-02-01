# Claw Conductor Examples

This directory contains practical examples demonstrating different routing scenarios.

## Running Examples

Make sure you've run the setup wizard first:
```bash
cd ..
./scripts/setup.sh
```

Then run any example:
```bash
python3 examples/simple-bug-fix.py
python3 examples/complex-feature.py
```

## Available Examples

### 1. Simple Bug Fix ([simple-bug-fix.py](simple-bug-fix.py))

**Scenario:** Fix a timezone display bug (complexity=2)

**Demonstrates:**
- Routing simple tasks to appropriate models
- Cost optimization (preferring free models for simple work)
- Score breakdown explanation

**Expected behavior:**
- Routes to free model (Gemini Flash, DeepSeek, etc.) if available
- Shows why cheaper models are chosen for simple tasks
- Highlights cost savings

### 2. Complex Feature ([complex-feature.py](complex-feature.py))

**Scenario:** Build complete e-commerce checkout system (6 subtasks)

**Demonstrates:**
- Multi-subtask decomposition
- Complexity-based routing (tasks range from 2-5)
- Parallel execution planning
- Cost vs. quality trade-offs

**Expected behavior:**
- High complexity tasks → Expert models (Claude, GPT-4)
- Simple tasks → Free models when possible
- Multiple agents used in parallel
- Each model matched to its strengths

### 3. Custom Workflow (Create Your Own!)

Want to test your own scenario? Use this template:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.router import Router, Task

def main():
    registry_path = Path(__file__).parent.parent / 'config' / 'agent-registry.json'
    router = Router(str(registry_path))

    # Your task here
    task = Task(
        description="Your task description",
        category="your-category",  # See config/task-categories.json
        complexity=3  # 1-5
    )

    agent_id, details = router.route_task(task)

    if agent_id:
        print(f"Assigned to: {details.get('model_id')}")
        print(f"Score: {details.get('total_score')}/100")
    else:
        print(f"Error: {details.get('error')}")

if __name__ == '__main__':
    main()
```

## Understanding the Output

### Score Breakdown

```
Score: 85/100
  • Rating:     40/50 pts  (4★ model)
  • Complexity: 40/40 pts  (perfect match: task=3, max=3)
  • Experience: 5/10 pts   (5 previous tasks in this category)
  • Cost Bonus: 0/10 pts   (pay-per-use model)
```

**Interpretation:**
- **Rating**: Higher stars = more points (5★ = 50pts, 4★ = 40pts, etc.)
- **Complexity**: Best when gap=0 (perfect match), slight penalty for overqualification
- **Experience**: Bonus for models proven in this category
- **Cost**: 10pt bonus for free/free-tier models

### Routing Decision Factors

1. **Can the model handle it?**
   - If task complexity > max_complexity → DISQUALIFIED
   - Otherwise → calculate score

2. **What's the score?**
   - Higher score = better match
   - Ties broken by cost preference

3. **Is there a better option?**
   - Check all enabled models
   - Compare scores
   - Consider runner-ups

## Tips for Testing

### Test with Different Complexities

Try the same task at different complexity levels:

```python
# Simple version
task_simple = Task("Add logging", "code-generation-new-features", complexity=1)

# Complex version
task_complex = Task("Add distributed tracing", "code-generation-new-features", complexity=5)
```

Observe how routing changes!

### Test with Cost Tracking

Enable cost tracking in your registry:

```json
{
  "user_config": {
    "cost_tracking_enabled": true,
    "prefer_free_when_equal": true
  }
}
```

See how free models get priority for tied scores.

### Test After Rating Updates

1. Run example and note the routing
2. Update a capability rating:
   ```bash
   python3 scripts/update-capability.py \
     --agent gemini-flash \
     --category bug-detection-fixes \
     --rating 4
   ```
3. Run example again and observe changes

## Common Patterns

### Pattern 1: Cost-Conscious Routing

For non-critical work, set complexity conservatively and let free models handle it:

```python
Task("Generate API documentation", "documentation-generation", complexity=2)
# → Likely routes to Gemini Flash (free, 4★ docs)
```

### Pattern 2: Quality-First Routing

For critical work, use higher complexity to force expert models:

```python
Task("Implement payment processing", "backend-development", complexity=5)
# → Likely routes to Claude Sonnet (5★ backend, handles max=5)
```

### Pattern 3: Balanced Routing

Let the router optimize:

```python
Task("Create React component", "frontend-development", complexity=3)
# → Router chooses based on agent configuration and scoring
```

## Troubleshooting

### "No capable agents found"

**Problem:** No model can handle the task complexity.

**Solution:**
- Lower task complexity if reasonable
- Add a more capable model
- Check that models are enabled in registry

### "Always routes to the same model"

**Problem:** One model dominates routing.

**Solutions:**
- Verify other models are enabled
- Check capability ratings are realistic
- Adjust ratings based on your experience
- Enable cost tracking to prefer free models

### "Unexpected routing choice"

**Problem:** Router chose a different model than expected.

**Debug:**
1. Check the score breakdown
2. Look at runner-ups to see what was close
3. Verify capability ratings match your expectations
4. Consider complexity gap (perfect match gets bonus)

## Contributing Examples

Have an interesting routing scenario? Share it!

1. Create a new example file
2. Follow the existing format
3. Add clear comments explaining the scenario
4. Update this README
5. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
