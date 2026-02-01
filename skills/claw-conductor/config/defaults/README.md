# Default Model Profiles

This directory contains pre-configured capability profiles for popular AI models, based on extensive benchmark testing and real-world performance data.

## Available Profiles

| Model | Provider | Cost | Best For |
|-------|----------|------|----------|
| **Claude Sonnet 4.5** | Anthropic | $3-15/M tokens | Complex debugging, testing, algorithms |
| **GPT-4 Turbo** | OpenAI | $10-30/M tokens | General-purpose, API development |
| **Gemini 2.0 Flash** | Google | Free tier | Fast generation, huge context (1M) |
| **DeepSeek V3** | OpenRouter | Free | Cost-conscious, strong reasoning |
| **Qwen 2.5 72B** | OpenRouter | Free | Multilingual, math/coding tasks |

## How to Add a Model

### Using Setup Wizard (Recommended)

```bash
./scripts/setup.sh
```

Select "Add new model from defaults" and choose from the list.

### Manual Addition

1. **Copy the default profile:**
   ```bash
   cp config/defaults/claude-sonnet-4.5.json /tmp/claude-temp.json
   ```

2. **Edit user-specific fields:**
   - Update `user_cost` section with your actual pricing
   - Set `enabled: true`
   - Verify `verified_date`

3. **Add to agent registry:**
   - Open `config/agent-registry.json`
   - Add the model to the `agents` object
   - Or use: `python3 scripts/register-model.py --from-default claude-sonnet-4.5`

## Capability Ratings

All ratings are 1-5 stars based on:
- **SWE-bench** (real-world software engineering tasks)
- **HumanEval** (code generation quality)
- **MATH** (mathematical reasoning)
- **Real-world testing** (actual usage patterns)

### Rating Scale

- ⭐ **1 star**: Beginner - basic functionality only
- ⭐⭐ **2 stars**: Simple - straightforward tasks
- ⭐⭐⭐ **3 stars**: Intermediate - moderate complexity
- ⭐⭐⭐⭐ **4 stars**: Advanced - handles most scenarios
- ⭐⭐⭐⭐⭐ **5 stars**: Expert - production-ready, minimal iteration

## Customizing Ratings

Don't agree with our ratings? You can override them:

```bash
python3 scripts/update-capability.py \
  --model claude-sonnet-4.5 \
  --category frontend-development \
  --rating 4 \
  --max-complexity 4 \
  --notes "My experience shows it's advanced but not expert"
```

## Contributing New Profiles

Have a model we don't cover? Submit a PR with:

1. Benchmark data (SWE-bench, HumanEval, etc.)
2. Real-world testing examples
3. Cost information
4. Capability ratings with justification

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## Profile Sources

Ratings derived from:
- Official benchmarks (Anthropic, OpenAI, Google, etc.)
- Independent testing (SWE-bench leaderboard, HumanEval)
- Community feedback and real-world usage
- Comparative analysis document (see `references/model-comparison.md`)

## Notes

- **Cost information** is approximate - always verify current pricing with providers
- **Capability ratings** may vary based on prompt engineering and use case
- **Free tier limits** may apply - check provider documentation
- **Context windows** are maximum - actual usable context may be less

---

*Last updated: 2026-01-31*
