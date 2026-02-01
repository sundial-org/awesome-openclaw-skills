---
name: request-approval
description: Use Preloop's request_approval tool to get human approval before risky operations like deletions, production changes, or external modifications
compatibility: Requires Preloop MCP server configured and accessible
metadata:
  author: preloop
  version: "1.0"
---

# Request Approval Skill

Use Preloop's `request_approval` MCP tool to get human approval before executing risky operations. Preloop will notify the user (via Slack, email, mobile apps, etc.) and wait for their response.

## Setup

Preloop must be configured as an MCP server. See [references/SETUP.md](references/SETUP.md) for configuration details.

## When to Request Approval

### ALWAYS Request Approval For:
- Deleting anything (files, directories, database records, cloud resources)
- Production changes (deployments, config changes, environment variables)
- Database operations (schema changes, migrations, bulk deletions/updates)
- External modifications (creating/merging PRs, posting to APIs, sending emails)
- Security changes (permissions, access controls, API keys)
- Financial operations (purchases, charges, refunds)
- System modifications (installing packages, changing system settings, CI/CD changes)

### Usually Request Approval For:
- Creating pull requests or issues (unless explicitly requested)
- Pushing commits to main/master branches
- Modifying critical files (package.json, requirements.txt, docker-compose.yml, etc.)
- Running commands that modify system state
- Making bulk changes (affecting many files/records)

### DON'T Request Approval For:
- Reading files or data
- Searching or querying
- Creating feature branches
- Running tests (in isolated environments)
- Making commits to feature branches

## How to Use

Call the `request_approval` tool BEFORE executing the risky operation.

### Parameters

**Required:**
- `operation` (string): Clear, specific description of what you'll do
  - ✅ Good: "Delete the logs/2024-01/ directory containing 1,234 log files (2.3GB)"
  - ❌ Bad: "Delete some logs"

- `context` (string): Additional details about what will be affected
  - ✅ Good: "This directory contains archived application logs from January 2024. The logs have been backed up to S3. Deleting will free up 2.3GB."
  - ❌ Bad: "Old logs"

- `reasoning` (string): Why this operation is necessary
  - ✅ Good: "Disk usage is at 92% capacity. These logs are archived in S3 and no longer needed locally."
  - ❌ Bad: "Need more space"

**Optional:**
- `caller` (string): Auto-populated by Preloop
- `approval_policy` (string): Specific approval policy name (uses account default if omitted)

### Response

The tool returns a string:
- **Approved**: Success message → proceed with the operation
- **Denied**: "Approval denied" or "Approval denied: {reason}" → STOP, don't execute
- **Error**: Error message → check configuration or try again

## Quick Example

**Task**: User asks to delete old cache files

**Your workflow**:
1. Check what exists: 3,421 cache files, 1.8GB, from last week
2. Call `request_approval`:
   - operation: "Delete the temp-cache/ directory"
   - context: "Contains 3,421 cache files totaling 1.8GB from batch jobs that ran last week. All jobs completed successfully."
   - reasoning: "Cache is no longer needed and is consuming disk space. Results are in the database."
3. Wait for response
4. If "denied" in response → tell user it's cancelled, ask for alternatives
5. If approved → proceed with deletion

See [references/EXAMPLES.md](references/EXAMPLES.md) for more examples.

## Decision Framework

When unsure:

1. **Can this be undone easily?** NO → Request approval
2. **Could this cause harm or data loss?** YES → Request approval
3. **Is this modifying production or external systems?** YES → Request approval
4. **Would a human want to review this first?** YES → Request approval
5. **Am I uncertain about the safety?** YES → Request approval

**Golden Rule**: When in doubt, request approval. Better to ask unnecessarily than to cause harm.

## If Approval is Denied

1. **Stop immediately** - do NOT proceed
2. **Check for comments** - denial may include reasoning
3. **Inform the user** - explain why it was cancelled
4. **Look for alternatives** - can you accomplish the goal differently?
5. **Don't retry** - don't ask again unless circumstances change

## Best Practices

**DO:**
- ✅ Request approval BEFORE executing
- ✅ Be specific and detailed
- ✅ Include numbers (file count, size, affected records)
- ✅ Explain the impact
- ✅ Respect denials

**DON'T:**
- ❌ Execute first, then ask
- ❌ Be vague
- ❌ Bundle multiple operations
- ❌ Proceed if denied
- ❌ Skip approval because you think it's "probably fine"

## Additional Resources

- [references/SETUP.md](references/SETUP.md) - Configuration and MCP server setup
- [references/EXAMPLES.md](references/EXAMPLES.md) - Detailed examples and workflows
- [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) - Common errors and solutions

---

**Remember**: Safety first! Trust is earned by being cautious and respectful of the user's systems and data.
