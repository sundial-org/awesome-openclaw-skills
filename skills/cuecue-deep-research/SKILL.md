---
name: cuecue-deep-research
description: Conduct deep financial research using CueCue's AI-powered multi-agent system
version: 1.0.2
author: CueCue Team
keywords:
  - research
  - financial-analysis
  - ai-agents
  - report-generation
  - data-analysis
  - imitation-writing
metadata: {"clawdbot":{"emoji":"🔭","requires":{"env":["CUECUE_API_KEY"]},"primaryEnv": "CUECUE_API_KEY"}}

---

# CueCue Deep Research TypeScript Skill

Execute comprehensive financial research queries using CueCue's multi-agent AI system. This TypeScript implementation provides the same functionality as the Python version with modern async/await patterns and full type safety.

## What This Skill Does

CueCue Deep Research orchestrates multiple AI agents to:

1. **Analyze** your research question and break it down into actionable tasks
2. **Research** using web crawling, financial databases, and knowledge retrieval
3. **Synthesize** findings into a comprehensive markdown report
4. **Generate** a shareable report URL

The skill filters the verbose agent workflow to show only:
- 📋 Task titles (from the supervisor agent)
- 📝 Final research report (from the reporter agent)
- 🔗 Report URL for web viewing

⏱️ **Execution Time**: Depending on the complexity of your research question, the process may take **5-30 minutes**. The system performs comprehensive research including web crawling, data analysis, and report generation. Please be patient and wait for the complete results.

## For AI Assistants

**Important**: When using this skill, you MUST monitor the research progress by checking the command output:

1. **Progress Monitoring**: The research process outputs progress information in real-time. You should check the output **every 5 minutes** to:
   - Verify the research is still running
   - Report task progress to the user (📋 Task updates)
   - Detect any errors or issues
   - Inform the user when report generation begins (📝 Generating Report...)

2. **Progress URL**: The command will output a URL like "Research begin. You can view progress at: https://cuecue.cn/c/..." - this URL is for **human users** to view the web interface, NOT for you to fetch. You should monitor progress through the command's stdout output.

3. **User Communication**: Keep the user informed about:
   - When research begins
   - Each major task that starts
   - When report generation begins
   - When research completes
   - Any errors or timeouts

4. **Timeout Handling**: If the command appears to hang or timeout, inform the user that the research may still be processing on the server, and they can check the web interface URL.

## Prerequisites

- Node.js 18+ or Deno
- CueCue API key (obtain from your CueCue account settings from https://cuecue.cn)
- npm or yarn package manager

## Installation

### As a CLI Tool

```bash
# Install globally
npm install -g cuecue-deep-research@1.0.2

# Or install locally in your project
npm install cuecue-deep-research@1.0.2
```

## Usage

### Command-Line Interface

#### Basic Research

```bash
# Using environment variable (recommended)
export CUECUE_API_KEY="your_api_key"
cuecue-research "Tesla Q3 2024 revenue analysis"

# Or specify API key directly
cuecue-research "Tesla Q3 2024 revenue analysis" --api-key YOUR_API_KEY
```

#### Save Report to File

```bash
cuecue-research "BYD vs Tesla market comparison" --output ~/clawd/cuecue-reports/2026-01-30-14-30-byd-tesla-comparison.md
```

**Note**: The output path should use the format `~/clawd/cuecue-reports/YYYY-MM-DD-HH-MM-descriptive-name.md` where the timestamp represents when the research was initiated. The `~` will be expanded to your home directory.

#### Use a Research Template

```bash
cuecue-research "Analyze CATL competitive advantages" \
  --output ~/clawd/cuecue-reports/2026-01-30-11-20-catl-analysis.md \
  --template-id TEMPLATE_ID
```

#### Continue Existing Conversation

```bash
cuecue-research "Further analyze supply chain risks" \
  --output ~/clawd/cuecue-reports/2026-01-30-15-45-supply-chain-risks.md \
  --conversation-id EXISTING_CONV_ID
```

#### Mimic Writing Style

```bash
cuecue-research "Electric vehicle market analysis" \
  --output ~/clawd/cuecue-reports/2026-01-30-16-00-ev-market-analysis.md \
  --mimic-url https://example.com/sample-article
```

The mimic feature analyzes the writing style, tone, and structure of the provided URL and applies it to the generated research report. This is useful for:
- Matching your organization's reporting style
- Adapting to specific audience preferences
- Maintaining consistency across reports

⚠️ **Note**: The `--mimic-url` and `--template-id` options cannot be used together. Choose one approach:
- Use `--template-id` for predefined research frameworks (goal, search plan, report format)
- Use `--mimic-url` for style mimicking without a template


## Command-Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `query` | ✅ | Research question or topic |
| `--api-key` | ❌ | Your CueCue API key (defaults to `CUECUE_API_KEY` env var) |
| `--base-url` | ❌ | CueCue API base URL (defaults to `CUECUE_BASE_URL` env var or https://cuecue.cn) |
| `--conversation-id` | ❌ | Continue an existing conversation |
| `--template-id` | ❌ | Use a predefined research template (cannot be used with `--mimic-url`) |
| `--mimic-url` | ❌ | URL to mimic the writing style from (cannot be used with `--template-id`) |
| `--output`, `-o` | ❌ | Save report to file (markdown format). Recommended format: `~/clawd/cuecue-reports/clawd/cuecue-reports/YYYY-MM-DD-HH-MM-descriptive-name.md` (e.g., `~/clawd/2026-01-30-12-41-tesla-analysis.md`). The `~` will be expanded to your home directory. |
| `--verbose`, `-v` | ❌ | Enable verbose logging |
| `--help`, `-h` | ❌ | Show help message |

## Output Format

The skill provides real-time streaming output:

```
Starting Deep Research: Tesla Q3 2024 Financial Analysis

Check Progress: https://cuecue.cn/c/12345678-1234-1234-1234-123456789abc

📋 Task: Search for Tesla Q3 2024 financial data

📋 Task: Analyze revenue and profit trends

📝 Generating Report...

# Tesla Q3 2024 Financial Analysis

## Executive Summary
[Report content streams here in real-time...]

✅ Research complete

============================================================
📊 Research Summary
============================================================
Conversation ID: 12345678-1234-1234-1234-123456789abc
Tasks completed: 2
Report URL: https://cuecue.cn/c/12345678-1234-1234-1234-123456789abc
✅ Report saved to: ~/clawd/cuecue-reports/2026-01-30-10-15-tesla-q3-analysis.md
```

## Troubleshooting

### 401 Unauthorized
- Verify your API key is correct
- Check if the API key has expired
- Ensure you have necessary permissions

### Connection Timeout
- Verify the base URL is correct
- Check network connectivity
- Research queries typically take 5-30 minutes depending on complexity - this is normal
- If you see a timeout, the research may still be processing on the server - check the web interface

### Empty Report
- Ensure your research question is clear and specific
- Check server logs for errors
- Try a different query to test connectivity

## Support

For issues or questions:
- [CueCue Website](https://cuecue.cn)
- Email: cue-admin@sensedeal.ai
