# Promptify

Optimize your prompts. One command, stackable modifiers.

Works in **Claude Code** and **molt.bot**.

## Install

**Claude Code:**
```bash
claude plugin install promptify@tolibear
```

**Molt.bot:**
```bash
npx molthub install promptify
```

## Usage

```
/promptify [+modifiers] your prompt here
```

## Modifiers

| Modifier | Effect |
|----------|--------|
| `+ask` | Ask clarifying questions first |
| `+deep` | Explore codebase for context |
| `+web` | Search web for best practices |

Stack them:

```
/promptify +ask+deep+web Build a payment system
```

## Smart Auto-Detection (v3)

Skip modifiers - promptify auto-detects what's needed:

| Your Prompt | Auto-Triggers |
|-------------|---------------|
| "Add auth to our API" | Codebase research |
| "Help me with this thing" | Clarifying questions |
| "Best practices for React hooks" | Web search |
| "Write a landing page" | Direct optimization |

## Example

**Before:**
```
Build a payment system
```

**After:**
```
You are a senior backend engineer with Stripe integration experience.

<task>
1. Analyze payment requirements (one-time vs recurring, currencies, refunds)
2. Design the data model (customers, payments, subscriptions)
3. Implement Stripe integration with proper error handling
4. Add webhook handlers for payment events
5. Include idempotency keys for safe retries
</task>

<constraints>
- Use Stripe API v2024-01
- Handle card failures gracefully with user-friendly messages
- Log all payment events for debugging
- Never store raw card numbers
</constraints>

<output>
Working implementation with:
- Payment service class
- Webhook controller
- Database migrations
- Test coverage for happy path and failure cases
</output>
```

## What It Does

- Analyzes images you include
- Uses conversation context
- Detects prompt type (coding, writing, analysis, creative, data)
- Converts output requests to process-oriented prompts
- Removes anti-patterns (filler, excessive politeness)
- Enforces Role, Task, Constraints, Output
- Copies to clipboard

## Changelog

**v3.0.0** - Rewritten for Claude 4.x. 65% shorter (163→57 lines). Progressive disclosure. Contract-first design.

## License

MIT
