---
name: jules-cli
description: Interact with the Jules CLI to manage asynchronous coding sessions. Use this skill to assign tasks, monitor progress, and pull patches from completed sessions.
---

# Jules CLI Skill

## Quick Start

```bash
# 1. Verify available repos (pre-flight check)
jules remote list --repo

# 2. Submit a task and wait for completion
./scripts/jules_submit.py --repo GITHUB_USERNAME/REPO "Your task description"
```

**Note:** Use your GitHub username/org, not your local system username (e.g., `octocat/Hello-World`, not `$USER/Hello-World`).

---

## Overview

This skill enables the agent to interact with the `jules` CLI. It supports task assignment, session monitoring, and result integration (pulling patches from completed sessions).

## Before You Start

### Verify Repository Access

Before submitting tasks, verify which repositories are available and confirm the correct format:

```bash
# List available repos to verify access and see correct username format
jules remote list --repo
```

**Important:** The `--repo` flag requires your GitHub username or organization name, not your local system username.

- **Correct:** `octocat/Hello-World` (GitHub username)
- **Incorrect:** `localuser/Hello-World` (local system username)

If you're unsure of your GitHub username:
1. Run `jules remote list --repo` to see available repos with correct formatting
2. Or check your GitHub profile at https://github.com/settings/profile

## Core Capabilities

1. **Automated Submission**: Use `jules_submit.py` to handle the session lifecycle (new session → wait → pull → apply).
2. **Task Assignment**: Create new coding sessions with `jules remote new`.
3. **Session Monitoring**: List and parse remote sessions to track progress.
4. **Result Integration**: Pull and apply patches from completed sessions.

## Workflows

### Option 1: Automated Task Submission (Recommended)

**Why this is recommended:**
- **Non-blocking**: The script handles polling automatically, freeing up the terminal
- **TTY-safe**: Automatically handles TTY/input redirection issues common in automation
- **All-in-one**: Creates session, waits for completion, and applies changes locally
- **Error handling**: Built-in retry logic and prerequisite checks

The `jules_submit.py` script handles session creation, waiting for completion, and applying results.

```bash
# Submit task and wait for completion
./scripts/jules_submit.py --repo octocat/Hello-World "Implement unit tests for the login module"

# Submit without waiting (fire-and-forget)
./scripts/jules_submit.py --repo octocat/Hello-World --no-wait "Research API options"
```

**Flags:**
- `--repo <repo>`: Repository in `GITHUB_USERNAME/REPO` format (e.g., `octocat/Hello-World`)
- `--no-wait`: Exit immediately after creating session (don't wait for completion)

### Option 2: Manual Workflow

Use this when you need granular control over each step or want to inspect intermediate results.

```bash
# Step 1: Create session
jules remote new --repo octocat/Hello-World --session "Task description"

# Step 2: Wait for session (check status until terminal state)
./scripts/wait_for_session.sh <SESSION_ID>

# Step 3: Pull and apply changes
jules remote pull --session <SESSION_ID> --apply
```

## Common Error Patterns

### "repo doesn't exist" or "repository not found"
**Cause:** Using local system username instead of GitHub username

**Solution:** 
- Verify with `jules remote list --repo` to see correct format
- Use GitHub username: `octocat/repo` not `localuser/repo`

### "Login Related" Errors
If you see `Trying to make a GET request without a valid client (did you forget to login?)` when running from automation:
1. **Verify HOME**: Ensure the `HOME` environment variable is set to the user's home directory.
2. **Credentials**: Ensure `~/.jules/cache/oauth_creds.json` exists and is valid. Run `jules login` manually if needed.

### TTY Errors
If you see `could not open a new TTY` or `inappropriate ioctl for device`:
1. Use redirected input: `echo "task" | jules ... < /dev/null`.
2. The provided scripts (`jules_submit.py`) handle this automatically.

## Testing & Validation

This skill has been validated with live Jules sessions. Key test scenarios include:
- ✅ Session creation with various repository formats
- ✅ TTY-safe automation in non-interactive environments  
- ✅ HOME environment variable edge cases
- ✅ Session status polling (Completed, Failed, Cancelled states)
- ✅ Patch application workflows

All error patterns documented above were discovered and resolved during live testing with the Jules platform.

## Command Reference

### Essential Commands

#### `jules remote new`
Assigns a new session to Jules in a remote VM.

```bash
jules remote new --repo octocat/Hello-World --session "Task description"
```

**Flags:**
- `--repo <repo>`: Repository in `GITHUB_USERNAME/REPO` format
- `--session <task>`: The task description (required)
- `--parallel <num>`: Number of parallel sessions (1-5)

#### `jules remote list`
Lists remote sessions or repositories.

```bash
# List your active sessions
jules remote list --session

# List available repos (useful for verifying repo format)
jules remote list --repo
```

#### `jules remote pull`
Pulls the result of a remote session and optionally applies it.

```bash
jules remote pull --session <SESSION_ID> --apply
```

**Flags:**
- `--session <id>`: The session ID (required)
- `--apply`: Apply the patch to the local repository

## Resources

### Scripts (in `scripts/`)
- `jules_submit.py`: **Primary tool for automation**. Wraps the entire workflow.
- `parse_sessions.py`: Parses the tabular output of `jules remote list --session` into JSON format.
- `wait_for_session.sh`: Polls a session status until it reaches a terminal state.

### Full Reference
- `references/usage.md`: Comprehensive reference of all `jules` commands, flags, and advanced usage patterns.
