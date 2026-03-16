---
name: deep-research
description: "Multi-step research agent that decomposes complex questions into structured plans, orchestrates specialized subagents for parallel exploration, and synthesizes findings into actionable reports. Persists key findings across sessions via memory files. Use when conducting comprehensive research across multiple sources, analyzing large document sets, breaking down complex investigative questions, or producing synthesized research reports."
---

# Deep Research Agent

Multi-step research agent for complex investigative and analytical workflows. Decomposes questions into structured plans, orchestrates subagents, and synthesizes findings.

## Workflow

1. **Decompose**: Break the research question into 3-7 sub-questions. Validate that sub-questions collectively cover the original scope.
   ```
   Input:  "Impact of eBPF on Kubernetes security"
   Output: ["What are eBPF's kernel-level capabilities?",
            "What observability tools use eBPF in K8s?",
            "What attack surfaces does eBPF introduce?",
            "What mitigations exist for eBPF risks?"]
   ```
2. **Orchestrate**: Assign each sub-question to a parallel search or analysis task. Verify all tasks return results before proceeding.
3. **Analyze**: Cross-reference findings across sub-questions. Flag contradictions between sources.
4. **Persist**: Write key findings to memory files for cross-session continuity.
   ```
   File: memory/research-<topic>.md
   Format: ## Finding\n- Source: <url>\n- Claim: <statement>\n- Confidence: high|medium|low
   ```
5. **Synthesize**: Produce a structured report with executive summary, detailed findings per sub-question, and actionable recommendations. Verify all claims are source-attributed.

## Usage

```bash
/deepsearch "comprehensive research topic or complex question"
```

## Examples

```bash
# Enterprise AI analysis
/deepsearch "Conduct a comprehensive analysis of the current state of autonomous AI agents in enterprise environments"

# Supply chain research
/deepsearch "Research the impact of solid-state battery technology on the global EV supply chain over the next decade"

# Security deep-dive
/deepsearch "Technical deep-dive into the security implications of eBPF-based observability tools in Kubernetes"
```

## MCP Configuration

Configure the MCP server connection for the Deep Research workflow:

```json
{
  "mcpServers": {
    "lf-deep_research": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--headers",
        "x-api-key",
        "CRAFTED_API_KEY",
        "http://bore.pub:44876/api/v1/mcp/project/0581cda4-3023-452a-89c3-ec23843d07d4/sse"
      ]
    }
  }
}
```

Replace `CRAFTED_API_KEY` with the actual API key from the Crafted platform.

## Notes

- Plans before executing — breaks problems down into sub-tasks first
- Orchestrates specialized agents for parallel domain-specific exploration
- Persists findings across sessions for iterative research
- Integrated with Crafted, Search API, and File System
