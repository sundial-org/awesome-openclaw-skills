# DROPBOOK SKILL KNOWLEDGE BASE

**Generated:** 2026-01-15
**Version:** 1.0.0

## OVERVIEW

This directory contains the `dropbox-skill`, an optimized integration layer enabling AI agents to interact with Dropbook via the Model Context Protocol (MCP).

## STRUCTURE

```
dropbox-skill/
├── SKILL.md                 # Master documentation & configuration
├── SKILL.json               # Machine-readable definition for OpenCode
└── references/              # Legacy or auxiliary docs
    └── mcp-setup.md
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| **Install/Setup** | `SKILL.md` (Setup section) |
| **Tool Definitions** | `SKILL.json` (for programmatic import) |
| **Usage Examples** | `SKILL.md` (CLI & JSON-RPC examples) |
| **Error Handling** | `SKILL.md` (Troubleshooting table) |

## CONVENTIONS

- **Single Source of Truth**: `SKILL.md` is the primary documentation. `SKILL.json` mirrors it for tooling.
- **Telegraphic Style**: Documentation should be concise, using tables and code blocks over prose.
- **JSON-RPC Format**: All MCP tool examples MUST follow the strict JSON-RPC 2.0 structure.

## ANTI-PATTERNS (SKILL SPECIFIC)

- **Do Not Modify `SKILL.json` Manually**: Ensure it stays in sync with `SKILL.md` descriptions.
- **No Hardcoded Tokens**: Instructions MUST use environment variable placeholders (e.g., `"${DROPBOX_APP_KEY}"`), never actual keys.
- **Avoid "Chatty" Protocols**: Use bulk operations where possible; explain rate limits in docs.

## INTEGRATION

To add this skill to an agent:
1. Reference `SKILL.json` in the agent's capability manifest.
2. Point the MCP client configuration to the `dropbook` executable built in the root directory.
