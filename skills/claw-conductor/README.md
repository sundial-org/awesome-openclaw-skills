# 🎼 Claw Conductor

**Intelligent Multi-Model Orchestration for OpenClaw**

Stop manually choosing which AI model to use for each task. Let Claw Conductor automatically route your work to the optimal model based on capability ratings, complexity analysis, and cost preferences.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://claude.com/claude-code)

## 🚀 What is This?

Claw Conductor is an **intelligent routing system** that analyzes your coding tasks and automatically selects the best AI model to handle each subtask. Think of it as a conductor orchestrating different instruments (models) to create a harmonious performance.

### The Problem

You have access to multiple AI models:
- **Claude Sonnet 4.5** - Expert at complex debugging and testing
- **GPT-4 Turbo** - Great for API development
- **Gemini 2.0 Flash** - Free and fast for simple tasks
- **DeepSeek V3** - Strong at algorithms, free
- **Qwen 2.5 72B** - Multilingual, free when available

But which one should you use for each task? Making the wrong choice wastes time and money.

### The Solution

```
User Request: "Build a user registration system with email verification"

↓ Claw Conductor analyzes and decomposes ↓

Subtask 1: Database schema → Mistral Devstral (5★ database expert)
Subtask 2: API endpoint → GPT-4 Turbo (4★ API development)
Subtask 3: Email verification → Claude Sonnet (5★ backend complexity)
Subtask 4: Registration UI → Gemini Flash (4★ frontend, FREE)
Subtask 5: Unit tests → Llama 3.3 70B (5★ test generation, FREE)

Result: 2 agents execute in parallel, optimal quality, minimized cost
```

## ✨ Key Features

- **🎯 Intelligent Routing** - Automatically selects the best model for each subtask
- **⭐ Capability Ratings** - 1-5 star ratings per model per task category
- **🔢 Complexity Analysis** - Hard ceilings prevent overwhelming models
- **💰 Cost Optimization** - Prefers free models when capabilities are equal
- **📊 Experience Tracking** - Learns which models perform best over time
- **🔄 Parallel Execution** - Routes independent tasks to different models simultaneously
- **🎨 Customizable** - Override ratings based on your real-world experience

## 📋 How It Works

### 1. Capability Rating System

Each model gets rated (1-5 stars) for each task category:

| Category | Claude 4.5 | GPT-4 | Gemini Flash | DeepSeek V3 |
|----------|------------|-------|--------------|-------------|
| **Bug Fixes** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Frontend** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Algorithms** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Tests** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 2. Complexity Levels

Tasks are rated 1-5 for complexity:
- **1 - Trivial**: Simple variable rename, add console.log
- **2 - Simple**: Basic CRUD endpoint, simple form validation
- **3 - Moderate**: Multi-step workflow, state management
- **4 - Complex**: Authentication system, real-time features
- **5 - Very Complex**: Distributed system, advanced algorithms

### 3. Scoring Algorithm

Models are scored 0-100: `Rating (50pts) + Complexity (40pts) + Experience (10pts) + Cost (10pts)`

Tasks exceeding a model's `max_complexity` are **disqualified** (hard ceiling enforcement).

## 🛠️ Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/claw-conductor.git
cd claw-conductor

# Copy example configuration
cp config/agent-registry.example.json config/agent-registry.json

# Run setup wizard
./scripts/setup.sh
```

The wizard will:
1. Check prerequisites
2. Configure your preferences
3. Add models from default profiles
4. Create your personalized agent registry

**Note:** `agent-registry.json` is gitignored - it contains your personal model configurations and API settings.

### Manual Setup

1. **Copy a default profile:**
   ```bash
   cp config/defaults/claude-sonnet-4.5.json my-agent.json
   ```

2. **Update cost information:**
   ```json
   {
     "user_cost": {
       "type": "free-tier",  // or "pay-per-use", "subscription", "free"
       "verified_date": "2026-01-31"
     }
   }
   ```

3. **Add to registry:**
   ```bash
   python3 scripts/update-capability.py --agent claude-sonnet --rating 5 --category bug-detection-fixes
   ```

## 📚 Usage

### Test the Router

```bash
# Run test scenario (user registration system)
python3 scripts/router.py --test
```

Output:
```
════════════════════════════════════════════════════════════════════
CLAW CONDUCTOR - INTELLIGENT ROUTING RESULTS
════════════════════════════════════════════════════════════════════

Subtask #1: Design database schema (users, verification_tokens tables)
  Category: database-operations | Complexity: 3
  ✓ Assigned to: mistral/devstral-2512
  Score: 85/100
    - Rating: 30/50 pts
    - Complexity: 40/40 pts (perfect match)
    - Experience: 5/10 pts
    - Cost Bonus: 10/10 pts

  Runner-ups:
    - llama-3.3-70b: 75/100 (3★ complexity≤3)

...

════════════════════════════════════════════════════════════════════
EXECUTION PLAN
════════════════════════════════════════════════════════════════════

mistral/devstral-2512:
  Subtasks: [1, 2, 3, 4]

llama-3.3-70b:
  Subtasks: [5]

2 agent(s) required for parallel execution
```

### Update Capability Ratings

Based on your experience, customize the ratings:

```bash
# Increase rating after great experience
python3 scripts/update-capability.py \
  --agent claude-sonnet \
  --category frontend-development \
  --rating 5 \
  --max-complexity 5 \
  --notes "Excellent at React components"

# Increment experience count
python3 scripts/update-capability.py \
  --agent gpt-4-turbo \
  --category api-development \
  --increment-experience

# View all capabilities for a model
python3 scripts/update-capability.py --agent claude-sonnet --show

# List all configured agents
python3 scripts/update-capability.py --list
```

## 📖 Task Categories

Claw Conductor supports 23+ task categories based on SWE-bench and HumanEval benchmarks:

- **code-generation-new-features** - Creating new functionality from scratch
- **bug-detection-fixes** - Finding and fixing bugs
- **multi-file-refactoring** - Architectural changes across 10+ files
- **unit-test-generation** - Writing comprehensive test suites
- **api-development** - REST/GraphQL API endpoints
- **frontend-development** - UI components and interactions
- **backend-development** - Server logic, business rules
- **database-operations** - Schema design, migrations, queries
- **algorithm-implementation** - Data structures, optimization
- **documentation-generation** - README, API docs, comments
- **codebase-exploration** - Understanding large codebases
- **security-vulnerability-detection** - Finding security issues
- **performance-optimization** - Speed and memory improvements
- And more...

See [`config/task-categories.json`](config/task-categories.json) for the full list.

## 🎯 Default Model Profiles

We provide pre-configured profiles for popular models:

| Model | Provider | Cost | Best For |
|-------|----------|------|----------|
| **Claude Sonnet 4.5** | Anthropic | $3-15/M tokens | Complex debugging, testing, algorithms |
| **GPT-4 Turbo** | OpenAI | $10-30/M tokens | General-purpose, API development |
| **Gemini 2.0 Flash** | Google | Free tier | Fast generation, huge context (1M) |
| **DeepSeek V3** | OpenRouter | Free | Cost-conscious, strong reasoning |
| **Qwen 2.5 72B** | OpenRouter | Free | Multilingual, math/coding tasks |

See [`config/defaults/`](config/defaults/) for all profiles.

## 🔧 Configuration

All configuration is in `config/agent-registry.json` (created by setup wizard).

Key settings:
- **cost_tracking_enabled** - Factor cost into routing
- **prefer_free_when_equal** - Tiebreaker for free models
- **fallback** - Automatic retry configuration

See [`config/agent-registry.example.json`](config/agent-registry.example.json) for the full schema.

## 🎓 Examples

Run the included examples:
```bash
python3 examples/simple-bug-fix.py       # Simple routing
python3 examples/complex-feature.py      # Multi-subtask routing
python3 examples/fallback-routing.py     # Fallback scenarios
```

See [`examples/README.md`](examples/README.md) for detailed walkthroughs.

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Add new model profiles** - Share your benchmark data
2. **Improve rating accuracy** - Submit real-world performance data
3. **Add task categories** - Suggest new categories with examples
4. **Report issues** - Help us improve routing accuracy

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

## 📄 License

GNU AGPL v3 - see [`LICENSE`](LICENSE) for details.

This copyleft license requires anyone running a modified version on a server to make the source code available to users.

## 🙏 Acknowledgments

- Capability ratings derived from [SWE-bench](https://www.swebench.com/), [HumanEval](https://github.com/openai/human-eval), and real-world testing
- Built for the [OpenClaw](https://claude.com/claude-code) ecosystem
- Inspired by the need for intelligent model selection in multi-model workflows

## 🔗 Links

- [ClawHub.ai Skills](https://www.clawhub.ai/skills) - Discover more OpenClaw skills
- [OpenClaw Documentation](https://claude.com/claude-code) - Learn about OpenClaw
- [Model Comparison Research](references/model-comparison.md) - Detailed benchmark analysis

---

**Made with 🎼 for the OpenClaw community**

*Stop guessing which model to use. Let the Conductor orchestrate.*
