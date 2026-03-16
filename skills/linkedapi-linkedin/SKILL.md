---
name: linkedin
description: General-purpose LinkedIn automation – fetch profiles, search people and companies, send messages, manage connections, create posts, and more. Use when the user wants to interact with LinkedIn.
---

# LinkedIn Skill

You have access to `linkedin` – a CLI tool for LinkedIn automation. Use it to fetch profiles, search people and companies, send messages, manage connections, create posts, react, comment, and more.

Each command sends a request to Linked API, which runs a real cloud browser to perform the action on LinkedIn. Operations are **not instant** – expect 30 seconds to several minutes depending on complexity.

If `linkedin` is not available, install it:

```bash
npm install -g @linkedapi/linkedin-cli
```

## Authentication

If a command fails with exit code 2 (authentication error), ask the user to set up their account:

1. Go to [app.linkedapi.io](https://app.linkedapi.io) and sign up or log in
2. Connect their LinkedIn account
3. Copy the **Linked API Token** and **Identification Token** from the dashboard

Once the user provides the tokens, run:

```bash
linkedin setup --linked-api-token=TOKEN --identification-token=TOKEN
```

## Global Flags

Always use `--json` and `-q` for machine-readable output:

```bash
linkedin <command> --json -q
```

| Flag | Description |
|------|-------------|
| `--json` | Structured JSON output |
| `--quiet` / `-q` | Suppress stderr progress messages |
| `--fields name,url,...` | Select specific fields in output |
| `--no-color` | Disable colors |
| `--account "Name"` | Use a specific account for this command |

## Commands

### Fetch a Person Profile

```bash
linkedin person fetch <url> [flags] --json -q
```

Optional flags: `--experience`, `--education`, `--skills`, `--languages`, `--posts`, `--comments`, `--reactions`.

### Search People

```bash
linkedin person search [flags] --json -q
```

Flags: `--term`, `--limit`, `--first-name`, `--last-name`, `--position`, `--locations`, `--industries`, `--current-companies`, `--previous-companies`, `--schools`.

### Fetch a Company

```bash
linkedin company fetch <url> [flags] --json -q
```

Optional flags: `--employees`, `--dms`, `--posts`.

### Search Companies

```bash
linkedin company search [flags] --json -q
```

Flags: `--term`, `--limit`, `--sizes`, `--locations`, `--industries`.

### Send a Message

```bash
linkedin message send <person-url> '<text>' --json -q
```

### Get Conversation

```bash
linkedin message get <person-url> [--since TIMESTAMP] --json -q
```

### Connection Management

```bash
linkedin connection status <url> --json -q
linkedin connection send <url> [--note 'text'] --json -q
linkedin connection list [flags] --json -q
linkedin connection pending --json -q
linkedin connection withdraw <url> --json -q
linkedin connection remove <url> --json -q
```

### Posts

```bash
linkedin post fetch <url> [--comments] [--reactions] --json -q
linkedin post create '<text>' [--attachments "url:type:name"] --json -q
linkedin post react <url> --type <like|love|support|celebrate|insightful|funny> --json -q
linkedin post comment <url> '<text>' --json -q
```

### Statistics

```bash
linkedin stats ssi --json -q
linkedin stats performance --json -q
linkedin stats usage --start <ISO> --end <ISO> --json -q
```

### Sales Navigator

```bash
linkedin navigator person fetch <hashed-url> --json -q
linkedin navigator person search [flags] --json -q
linkedin navigator company fetch <hashed-url> [--employees] [--dms] --json -q
linkedin navigator company search [flags] --json -q
linkedin navigator message send <person-url> '<text>' --subject '<subject>' --json -q
linkedin navigator message get <person-url> --json -q
```

### Custom Workflows

```bash
linkedin workflow run --file workflow.json --json -q
linkedin workflow status <id> --json -q
```

## Important Behavior

- **Sequential execution.** All operations for an account run one at a time.
- **Not instant.** A real browser navigates LinkedIn – expect 30 seconds to several minutes.
- **Timestamps in UTC.** All dates and times are in UTC.
- **Single quotes for text arguments.** Use single quotes around message text.
