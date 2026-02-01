# Contributing to Claw Conductor

Thank you for your interest in contributing to Claw Conductor! This project thrives on community input, especially real-world performance data and model profiles.

## 🎯 How You Can Help

### 1. Share Model Profiles

Have access to a model we don't cover? Add it!

**What we need:**
- Model ID and provider
- Benchmark scores (SWE-bench, HumanEval, MATH, etc.)
- Real-world testing examples
- Cost information
- Capability ratings with justification

**How to submit:**
1. Create a JSON profile in `config/defaults/`
2. Follow the existing format (see `claude-sonnet-4.5.json`)
3. Include a comment block with data sources
4. Submit a PR with your profile

**Example:**
```json
{
  "model_id": "anthropic/claude-opus-4.5",
  "provider": "anthropic",
  "context_window": 200000,
  "enabled": false,
  "user_cost": {
    "type": "pay-per-use",
    "input_cost_per_million": 15.00,
    "output_cost_per_million": 75.00,
    "notes": "Anthropic API pricing as of 2026-01-31",
    "verified_date": "2026-01-31"
  },
  "capabilities": {
    "code-generation-new-features": {
      "rating": 5,
      "max_complexity": 5,
      "notes": "Expert - SWE-bench: 85.2%, HumanEval: 96.3%"
    },
    // ... more capabilities
  },
  "performance_notes": "Highest quality, best for very complex tasks",
  "_data_sources": [
    "SWE-bench verified leaderboard 2026-01-15",
    "HumanEval+ benchmark 2026-01-20",
    "Real-world testing with 50+ complex tasks"
  ]
}
```

### 2. Improve Rating Accuracy

See different results than our ratings suggest? Let us know!

**Report format:**
```markdown
**Model:** claude-sonnet-4.5
**Category:** frontend-development
**Current Rating:** 4★, max_complexity=4
**Suggested Rating:** 5★, max_complexity=5

**Justification:**
Tested with 20+ React component tasks including:
- Complex state management (Redux Toolkit)
- Advanced animations (Framer Motion)
- Performance optimization (React.memo, useMemo)

Results: 18/20 perfect on first try, 2/20 needed minor tweaks.
Outperformed GPT-4 Turbo consistently.

**Evidence:**
- Link to test tasks
- Screenshots of results
- Comparison with other models
```

### 3. Add Task Categories

Found a category we're missing?

**Proposal format:**
```json
{
  "name": "mobile-app-development",
  "description": "React Native, Flutter, or native mobile development",
  "keywords": ["react-native", "flutter", "swift", "kotlin", "mobile"],
  "complexity_indicators": {
    "1": "Simple UI component",
    "2": "Screen with navigation",
    "3": "Feature with state management",
    "4": "Native module integration",
    "5": "Complex offline sync, background processing"
  },
  "example_tasks": [
    "Create a login screen (complexity=2)",
    "Build a camera integration (complexity=4)"
  ],
  "benchmarks": [
    "Mobile-specific eval datasets",
    "App Store submission success rate"
  ]
}
```

### 4. Report Issues

Found a bug or unexpected routing behavior?

**Issue template:**
```markdown
**Description:**
Brief description of the issue

**Task Details:**
- Description: "Build a REST API"
- Category: api-development
- Complexity: 3

**Expected Routing:**
Should route to GPT-4 Turbo (4★, max=4)

**Actual Routing:**
Routed to Gemini Flash (3★, max=3)

**Registry State:**
```json
{
  "gpt-4-turbo": {
    "enabled": true,
    "capabilities": {
      "api-development": {
        "rating": 4,
        "max_complexity": 4
      }
    }
  }
}
```

**Steps to Reproduce:**
1. Configure registry as shown
2. Run: `python3 scripts/router.py --test`
3. Observe routing

**Environment:**
- OS: macOS 14.2
- Python: 3.11.5
- Claw Conductor version: 1.0.0
```

## 📋 Development Setup

### Prerequisites

- Python 3.7+
- jq (for JSON processing)
- git

### Local Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/claw-conductor.git
cd claw-conductor

# Run setup
./scripts/setup.sh

# Run tests
python3 scripts/router.py --test

# Test capability updates
python3 scripts/update-capability.py --list
```

### Testing Checklist

Before submitting a PR:

- [ ] All existing tests pass
- [ ] New models have complete capability profiles
- [ ] JSON files are properly formatted
- [ ] Documentation updated if needed
- [ ] Examples added for new features
- [ ] Cost information verified with sources

## 🎨 Code Style

### JSON Files

- Use 2-space indentation
- Sort keys alphabetically within sections
- Include comments for data sources (as `_data_sources`)
- Use ISO 8601 dates (`YYYY-MM-DD`)

### Python Scripts

- Follow PEP 8
- Use type hints
- Include docstrings for functions
- Keep functions focused and small

### Bash Scripts

- Use `set -e` for error handling
- Include descriptive comments
- Use meaningful variable names
- Test on macOS and Linux

## 🔄 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-model`)
3. **Commit** your changes (`git commit -m 'Add Claude Opus 4.5 profile'`)
4. **Push** to the branch (`git push origin feature/amazing-model`)
5. **Open** a Pull Request

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New model profile
- [ ] Rating adjustment
- [ ] New task category
- [ ] Bug fix
- [ ] Documentation update
- [ ] New feature

## Testing
- [ ] Tested with `router.py --test`
- [ ] Verified JSON format
- [ ] Checked capability ratings
- [ ] Updated documentation

## Data Sources
- Link to benchmarks
- Real-world testing details
- Cost verification sources

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 📊 Benchmark Data Sources

We accept data from:

### Primary Sources
- **SWE-bench** - Real-world software engineering tasks
- **HumanEval** - Code generation quality
- **MATH** - Mathematical reasoning
- **MBPP** - Python programming problems

### Secondary Sources
- Real-world testing (minimum 20 tasks per category)
- Community feedback and ratings
- Comparative analysis vs. existing models
- Published research papers

### Data Quality Requirements

1. **Reproducible** - Provide test methodology
2. **Recent** - Within last 6 months
3. **Representative** - Covers diverse scenarios
4. **Quantitative** - Include success rates, scores
5. **Comparative** - Show vs. other models

## 🤝 Community Guidelines

- Be respectful and constructive
- Share data and sources
- Focus on objective performance metrics
- Acknowledge limitations and edge cases
- Help others improve their configurations

## 📝 Documentation

When adding features:

1. Update README.md with examples
2. Add to SKILL.md if relevant
3. Include usage examples
4. Document configuration options
5. Update CHANGELOG.md

## 🔍 Review Process

1. **Automated checks** - JSON validation, linting
2. **Maintainer review** - Verify data sources and logic
3. **Community feedback** - 48-hour comment period for major changes
4. **Merge** - After approval and CI pass

## 💡 Ideas for Contribution

Not sure where to start? Try these:

- [ ] Add your favorite model's profile
- [ ] Test and report accuracy for existing profiles
- [ ] Create example workflows
- [ ] Improve error messages
- [ ] Add integration tests
- [ ] Write tutorials or guides
- [ ] Translate documentation
- [ ] Create visualizations for routing decisions

## 📬 Contact

- GitHub Issues: Bug reports and feature requests
- Discussions: General questions and ideas
- Email: [your-email] for sensitive topics

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Claw Conductor better for everyone!** 🎼
