---
name: rlm
description: Use RLM (Recursive Language Models) for verified code execution, calculations, data analysis, and task decomposition. Executes Python code iteratively until producing verified results - no LLM guessing.
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (npm)"}]}}
---

# RLM - Recursive Language Models

Execute tasks with **verified code execution** via mcporter MCP bridge.

RLM writes and executes Python code iteratively until it produces a verified answer. Unlike direct LLM responses, RLM computations are **100% accurate** for calculations.

## Prerequisites

### 1. Install mcporter (MCP bridge)
```bash
npm install -g mcporter
```

### 2. Install RLM MCP Server

**Option A: Clone and setup (recommended)**
```bash
# Clone RLM project
git clone https://github.com/alexzhang13/rlm.git $HOME/rlm
cd $HOME/rlm
pip install -e .

# Create MCP server directory
mkdir -p $HOME/.claude/mcp-servers/rlm/src

# Download MCP server files
curl -o $HOME/.claude/mcp-servers/rlm/src/server.py \
  https://raw.githubusercontent.com/eesb99/rlm-mcp/main/src/server.py
curl -o $HOME/.claude/mcp-servers/rlm/run_server.sh \
  https://raw.githubusercontent.com/eesb99/rlm-mcp/main/run_server.sh
curl -o $HOME/.claude/mcp-servers/rlm/setup.sh \
  https://raw.githubusercontent.com/eesb99/rlm-mcp/main/setup.sh
curl -o $HOME/.claude/mcp-servers/rlm/requirements.txt \
  https://raw.githubusercontent.com/eesb99/rlm-mcp/main/requirements.txt

# Setup venv and install dependencies
chmod +x $HOME/.claude/mcp-servers/rlm/*.sh
cd $HOME/.claude/mcp-servers/rlm
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

**Option B: Manual setup**
```bash
# Create server directory
mkdir -p $HOME/.claude/mcp-servers/rlm/src

# Create venv and install dependencies
cd $HOME/.claude/mcp-servers/rlm
python3 -m venv venv
venv/bin/pip install mcp litellm

# Create run_server.sh
cat > $HOME/.claude/mcp-servers/rlm/run_server.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$HOME/rlm:$PYTHONPATH"
export RLM_MODEL="${RLM_MODEL:-openrouter/x-ai/grok-code-fast-1}"
export RLM_SUBTASK_MODEL="${RLM_SUBTASK_MODEL:-openrouter/openai/gpt-4o-mini}"
export RLM_MAX_DEPTH="${RLM_MAX_DEPTH:-2}"
export RLM_MAX_ITERATIONS="${RLM_MAX_ITERATIONS:-20}"
exec "$SCRIPT_DIR/venv/bin/python" -m src.server
EOF
chmod +x $HOME/.claude/mcp-servers/rlm/run_server.sh
```

### 3. Configure MCP (for Claude Code)

Add to `~/.mcp.json` (replace `YOUR_HOME` with your actual home path, e.g., `/Users/john` or `/home/john`):
```json
{
  "mcpServers": {
    "rlm": {
      "command": "bash",
      "args": ["YOUR_HOME/.claude/mcp-servers/rlm/run_server.sh"]
    }
  }
}
```

**Get your home path:** `echo $HOME`

### 4. Set API Key

RLM requires an OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### 5. Verify Installation

```bash
# Check mcporter sees RLM
mcporter list | grep rlm

# Test RLM
mcporter call 'rlm.rlm_status()'
```

## Available Tools

| Tool | Use For | Parameters |
|------|---------|------------|
| `rlm_execute` | General tasks, calculations | `task` (required), `context` (optional) |
| `rlm_analyze` | Data analysis | `data`, `question` (both required) |
| `rlm_code` | Generate tested code | `description` (required), `language` (optional, default: python) |
| `rlm_decompose` | Complex multi-step tasks | `complex_task`, `num_subtasks` (default: 5) |
| `rlm_status` | Check system status | (none) |

## Quick Commands

**Simple calculation:**
```bash
mcporter call 'rlm.rlm_execute(task: "calculate 127 * 389")'
```

**First N primes:**
```bash
mcporter call 'rlm.rlm_execute(task: "calculate the first 100 prime numbers")'
```

**Data analysis:**
```bash
mcporter call 'rlm.rlm_analyze(data: "[23, 45, 67, 89, 12, 34]", question: "what is the mean, median, and standard deviation?")'
```

**Generate code:**
```bash
mcporter call 'rlm.rlm_code(description: "function to check if a number is prime")'
```

**Complex task (decomposed):**
```bash
mcporter call 'rlm.rlm_decompose(complex_task: "analyze a $500K portfolio with 60/30/10 allocation, calculate risk metrics and 10-year projection", num_subtasks: 5)'
```

**Check status:**
```bash
mcporter call 'rlm.rlm_status()'
```

## When to Use RLM

**Use RLM for:**
- Mathematical calculations requiring precision
- Statistical analysis (mean, std dev, correlations)
- Financial calculations (compound interest, NPV, IRR)
- Algorithm execution (primes, sorting, searching)
- Data transformations and aggregations
- Code generation with verification

**Don't use RLM for:**
- Simple factual questions (use direct response)
- Creative writing or brainstorming
- Tasks requiring web search or real-time data
- Very simple calculations (2+2)

## How It Works

```
1. You give RLM a task
2. RLM writes Python code to solve it
3. Code executes in sandbox
4. If not complete, RLM iterates
5. Returns verified final answer
```

**Models used:**
- Root: `grok-code-fast-1` (fast code execution)
- Subtasks: `gpt-4o-mini` (cheap sub-queries)

## Configuration

**Environment variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `RLM_MODEL` | `openrouter/x-ai/grok-code-fast-1` | Root execution model |
| `RLM_SUBTASK_MODEL` | `openrouter/openai/gpt-4o-mini` | Subtask model |
| `RLM_MAX_DEPTH` | `2` | Max recursion depth |
| `RLM_MAX_ITERATIONS` | `20` | Max iterations per task |
| `OPENROUTER_API_KEY` | (required) | OpenRouter API key |

**Server location:** `$HOME/.claude/mcp-servers/rlm/`

## Troubleshooting

**"Server offline" or "No module named 'mcp'":**
```bash
# Reinstall dependencies
cd $HOME/.claude/mcp-servers/rlm
python3 -m venv venv
venv/bin/pip install mcp litellm
```

**"mcporter: command not found":**
```bash
npm install -g mcporter
```

**"rlm not in mcporter list":**
- Check `$HOME/.mcp.json` exists and has rlm config
- Verify run_server.sh is executable: `chmod +x $HOME/.claude/mcp-servers/rlm/run_server.sh`

**Slow response:**
- RLM executes real code, typically 10-30 seconds
- Complex tasks with decomposition take longer

## References

- **Paper:** [Recursive Language Models](https://arxiv.org/abs/2512.24601) (Zhang, Kraska, Khattab 2025)
- **RLM Library:** [github.com/alexzhang13/rlm](https://github.com/alexzhang13/rlm)
- **MCP Server:** [github.com/eesb99/rlm-mcp](https://github.com/eesb99/rlm-mcp)
- **MCP SDK:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **mcporter:** [mcporter.dev](http://mcporter.dev)
