# Request Approval Skill

This skill teaches AI agents to use Preloop's `request_approval` MCP tool for safe operation with human oversight.

## Structure

```
request-approval/
├── SKILL.md                    # Main skill file (agents load this first)
├── README.md                   # This file
└── references/
    ├── SETUP.md               # Configuration and MCP server setup
    ├── EXAMPLES.md            # Detailed examples and workflows
    └── TROUBLESHOOTING.md     # Common errors and solutions
```

## Progressive Disclosure

This skill follows the progressive disclosure pattern:

1. **SKILL.md** (~150 lines): Core instructions loaded when skill is activated
   - When to request approval
   - How to use the tool
   - Quick example
   - Decision framework

2. **references/** (loaded on-demand): Detailed documentation
   - SETUP.md: Configuration instructions
   - EXAMPLES.md: 8+ detailed examples
   - TROUBLESHOOTING.md: Error resolution

Agents load SKILL.md initially, then reference additional files only when needed.

## Installation

### For Users

Copy this directory to your agent's skills folder:

**Claude Desktop / Claude Code:**
```bash
cp -r request-approval ~/.claude/skills/
```

**Cline:**
```bash
cp -r request-approval ~/.cline/skills/
```

**Other agents:**
Check your agent's documentation for the skills directory location.

### For Distribution

This skill can be:
- Bundled with Preloop installations
- Distributed via package managers
- Shared as a git repository
- Included in agent presets

## Configuration

Before using this skill:

1. Configure Preloop as an MCP server (see [references/SETUP.md](references/SETUP.md))
2. Create an approval policy in Preloop
3. Set the policy as default
4. Restart your agent

## Usage

Once installed and configured, agents will automatically:
- Identify risky operations that need approval
- Call the `request_approval` tool before executing
- Wait for human approval/denial
- Proceed only if approved

## Validation

This skill follows the [Agent Skills specification](https://agentskills.io/specification).

Validate with:
```bash
npm install -g @agentskills/cli
agentskills validate request-approval/
```

## License

See the main Preloop repository for license information.

## Support

- Documentation: https://docs.preloop.ai
- Community: https://community.preloop.ai
- GitHub: https://github.com/preloop/preloop
