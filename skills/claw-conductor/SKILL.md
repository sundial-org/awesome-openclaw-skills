---
name: claw-conductor
description: Intelligent multi-model orchestration for OpenClaw. Automatically decomposes tasks and routes subtasks to the best AI model based on capability ratings, complexity analysis, and cost optimization.
version: 1.0.0
---

# Claw Conductor

**Orchestrate your AI models with precision.**

Claw Conductor is an intelligent task orchestration system that analyzes your requests, breaks them into subtasks, and routes each subtask to the optimal AI model based on:

- **Task category** (API development, frontend, testing, etc.)
- **Task complexity** (1-5 star rating system)
- **Model capabilities** (what each model excels at)
- **Cost optimization** (user-specific pricing)

## Quick Start

### Installation

**Option 1: Project Skill (Recommended - Shared with Team)**
```bash
# In your project directory
mkdir -p .claude/skills
cd .claude/skills
git clone <your-repo-url> claw-conductor
cd claw-conductor
chmod +x scripts/*.sh scripts/*.py
./scripts/setup.sh
```

**Option 2: User Skill (Personal Use)**
```bash
# Global installation
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone <your-repo-url> claw-conductor
cd claw-conductor
chmod +x scripts/*.sh scripts/*.py
./scripts/setup.sh
```

### First-Time Setup

```bash
./scripts/setup.sh
```

This interactive wizard will:
1. Detect your configured OpenClaw models
2. Ask about your cost structure for each model
3. Create your personalized agent registry
4. Set up routing preferences

### Usage

In Discord or OpenClaw chat:

```
@OpenClaw Build a user registration system with email verification
```

Claw Conductor will:
1. ✨ **Analyze** the task and identify subtasks
2. 🎯 **Score** each model for each subtask
3. 🎼 **Route** subtasks to optimal models
4. ⚡ **Execute** in parallel when possible
5. 🔗 **Consolidate** results into final deliverable

## How It Works

### 1. Task Decomposition

The orchestrator analyzes your request and breaks it into categorized subtasks:

```
Request: "Build user registration with email verification"

Subtasks:
├─ Database schema (database-operations, complexity: 3)
├─ Registration API (api-development, complexity: 3)
├─ Email verification flow (backend-development, complexity: 4)
├─ Registration form UI (frontend-development, complexity: 2)
└─ API tests (unit-test-generation, complexity: 3)
```

### 2. Intelligent Routing

Each subtask is scored against all available models:

```
Example: API Development (complexity: 3)

mistral-devstral-2512:
  Rating: 4★ (40 pts)
  Can handle complexity 3? Yes (40 pts)
  Cost: Free tier (+10 pts)
  Total: 90/100

llama-3.3-70b:
  Rating: 4★ (40 pts)
  Can handle complexity 3? Yes (40 pts)
  Cost: Free (+10 pts)
  Total: 90/100

Winner: Tie → Choose based on token availability or speed
```

### 3. Parallel Execution

Independent subtasks run simultaneously using different models:

```
┌─ mistral-devstral-2512 ────┐
│ - Database schema          │
│ - Email verification       │
└────────────────────────────┘

┌─ llama-3.3-70b ────────────┐
│ - Registration API         │
│ - API tests                │
└────────────────────────────┘

┌─ scientific-calculator ────┐
│ - Registration form UI     │
└────────────────────────────┘

All execute in parallel → Consolidate → Done
```

### 4. Automatic Fallback & Retry

Claw Conductor provides resilience against model failures with conservative fallback logic:

```
Strategy (for each subtask):
1. Try primary model (attempt #1)
2. If fails → Retry primary (attempt #2)
3. If still fails → Try first runner-up (attempt #3)
4. If fails → Retry runner-up (attempt #4)
5. If all fail → Report failure

Total: Maximum 4 attempts per task
Delay: 2 seconds between attempts
```

**Why conservative?**
- Later runner-ups may not even have the capability for the task
- Prevents wasteful cascading through irrelevant models
- Balances reliability with efficiency

**Example Execution:**

```
Task: Implement JWT authentication (backend-development, complexity=4)

Primary: mistral-devstral-2512
Runner-up: llama-3.3-70b

Attempt 1: mistral-devstral-2512 → ✗ Timeout
Attempt 2: mistral-devstral-2512 → ✗ API unavailable
Attempt 3: llama-3.3-70b         → ✓ Success!

Result: Task completed via fallback
Total time: ~4 seconds (2 failures × 2s delay + execution)
```

**Failure Tracking:**
- Models that fail repeatedly lose experience points
- Success rate is tracked per model
- Helps identify unreliable models over time

## Configuration

### Agent Registry

Located at `config/agent-registry.json`, this defines:

- **Available models** and their OpenClaw model IDs
- **Capability ratings** (1-5 stars) for each task category
- **Maximum complexity** each model can handle per category
- **User-specific costs** (verified during setup)

### Task Categories

Standard categories in `config/task-categories.json`:

- code-generation-new-features
- bug-detection-fixes
- multi-file-refactoring
- unit-test-generation
- api-development
- frontend-development
- backend-development
- database-operations
- security-vulnerability-detection
- documentation-generation
- algorithm-implementation
- boilerplate-generation
- And more...

### User Preferences

Your agent registry contains user configuration:

```json
{
  "user_config": {
    "cost_tracking_enabled": true,
    "prefer_free_when_equal": true,
    "max_parallel_tasks": 5,
    "default_complexity_if_unknown": 3,
    "fallback": {
      "enabled": true,
      "retry_delay_seconds": 2,
      "track_failures": true,
      "penalize_failures": true,
      "failure_penalty_points": 5
    }
  }
}
```

**Fallback Configuration:**
- `enabled`: Automatically retry with runner-up on failures
- `retry_delay_seconds`: Wait time between attempts (prevents rate limiting)
- `track_failures`: Record which models fail tasks
- `penalize_failures`: Reduce experience points for failing models
- `failure_penalty_points`: How many points to deduct per failure

## Pre-Configured Model Profiles

Claw Conductor ships with expert-rated profiles for popular models:

- **Claude Sonnet 4.5** - Expert at complex reasoning, testing, debugging
- **Mistral Devstral 2** - Expert at multi-file refactoring, frontend, dependencies
- **Llama 3.3 70B** - Expert at tests, boilerplate, algorithms
- **Perplexity Sonar** - Expert at research, exploration, documentation
- **GPT-4** - For users with OpenAI API access
- **DeepSeek** - For users with DeepSeek access

Profiles based on extensive benchmark research (SWE-bench, HumanEval, real-world testing).

## Examples

See `examples/` directory for detailed walkthroughs:

- [Basic Routing](examples/01-basic-routing.md) - Simple feature request
- [Cost Optimization](examples/02-cost-optimization.md) - Minimizing API costs
- [Custom Categories](examples/03-custom-categories.md) - Adding your own task types
- [Complex Orchestration](examples/04-complex-orchestration.md) - Full-stack application

## Advanced Features

### Custom Categories

Add domain-specific task categories:

```bash
python3 scripts/add-category.py \
  --name "towing-domain-logic" \
  --description "Towing industry business rules" \
  --complexity-examples "Simple: Basic booking, Complex: Dynamic pricing"
```

### Model Registration

Add new models to your registry:

```bash
python3 scripts/register-model.py \
  --model-id "anthropic/claude-sonnet-4.5" \
  --provider "anthropic" \
  --cost-type "pay-per-use" \
  --auto-rate
```

The `--auto-rate` flag uses benchmark data to suggest capability ratings, which you can override.

### Performance Tracking

Monitor which models perform best:

```bash
python3 scripts/performance-report.py --last-30-days
```

Generates report showing:
- Tasks completed per model
- Success rates
- Average completion times
- Cost per task

## Architecture

```
User Request (Discord/Chat)
     ↓
┌────────────────────────────┐
│  Task Analyzer             │
│  (uses Perplexity or       │
│   primary model)           │
└────────────────────────────┘
     ↓
┌────────────────────────────┐
│  Decomposer                │
│  - Identify subtasks       │
│  - Categorize each         │
│  - Assess complexity       │
└────────────────────────────┘
     ↓
┌────────────────────────────┐
│  Router                    │
│  - Load agent registry     │
│  - Score each model        │
│  - Assign best fit         │
└────────────────────────────┘
     ↓
┌────────────────────────────┐
│  Executor                  │
│  - Spawn parallel agents   │
│  - Monitor progress        │
│  - Handle failures         │
└────────────────────────────┘
     ↓
┌────────────────────────────┐
│  Consolidator              │
│  - Collect outputs         │
│  - Merge deliverables      │
│  - Validate completeness   │
└────────────────────────────┘
     ↓
   Result
```

## Troubleshooting

### Routing seems wrong

Check model capability ratings:
```bash
python3 scripts/show-capabilities.py --model mistral-devstral-2512
```

Adjust ratings in `config/agent-registry.json` if needed.

### Tasks failing with "can't handle complexity"

The model's `max_complexity` for that category is too low. Either:
- Use a more capable model for that category
- Simplify the task
- Override complexity assessment

### Cost tracking not working

Verify `user_cost` section in agent registry:
```bash
cat config/agent-registry.json | grep -A 5 "user_cost"
```

Re-run setup if cost info is incorrect.

## Contributing

Claw Conductor is open source! Contributions welcome:

- **Model profiles**: Submit benchmark-verified capability ratings
- **Task categories**: Propose new standard categories
- **Routing improvements**: Enhance scoring algorithm
- **Documentation**: Examples, guides, tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE)

## Credits

- **Capability ratings** based on SWE-bench, HumanEval, and real-world testing
- **Architecture** inspired by OpenClaw's multi-agent patterns
- **Research foundation**: Comprehensive model comparison (see references/)

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Discord**: [OpenClaw Community]

---

**Version**: 1.0.0
**Author**: jfasteroid
**Repository**: github.com/jfasteroid/claw-conductor
