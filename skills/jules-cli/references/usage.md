# Jules CLI Usage Reference

## Repository Format

**Important:** Always use your GitHub username/org, not your local system username.

- **Correct:** `octocat/Hello-World`
- **Incorrect:** `localuser/Hello-World`

Verify available repos and see the correct format:
```bash
jules remote list --repo
```

---

## Automation Wrapper

### `jules_submit.py`
A helper script provided by this skill to automate the full Jules workflow.

**Usage:**
```bash
./scripts/jules_submit.py [flags] "task description"
```

**Flags:**
- `--repo <repo>`: Specify the repository (e.g., `octocat/Hello-World`). **Must be GitHub username format.**
- `--no-wait`: Don't wait for the session to complete (default: wait).

**Examples:**
```bash
# Submit and wait for completion
./scripts/jules_submit.py --repo octocat/Hello-World "Fix login bug"

# Fire-and-forget (don't wait)
./scripts/jules_submit.py --repo octocat/Hello-World --no-wait "Research task"
```

---

## Native Jules Commands

### `jules remote new`
Assigns a new session to Jules in a remote VM.

**Usage:**
```bash
jules remote new --repo octocat/Hello-World --session "Task description"
```

**Flags:**
- `--repo <repo>`: Specify the repository in `GITHUB_USERNAME/REPO` format. Defaults to current directory.
- `--session <task>`: The task description (required).
- `--parallel <num>`: Number of parallel sessions (1-5).

---

### `jules remote list`
Lists remote sessions or repositories.

**Usage:**
```bash
# List your active sessions
jules remote list --session

# List available repos (pre-flight check)
jules remote list --repo
```

---

### `jules remote pull`
Pulls the result of a remote session.

**Usage:**
```bash
jules remote pull --session <SESSION_ID> --apply
```

**Flags:**
- `--session <id>`: The session ID (required).
- `--apply`: Apply the patch to the local repository.

---

### `jules teleport`
Clones repository and applies session changes (or applies to existing repo).

**Usage:**
```bash
jules teleport <session_id>
```

---

## Error Reference

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "repo doesn't exist" | Wrong username format | Use GitHub username: `octocat/repo` not `localuser/repo` |
| "repository not found" | Repo not accessible | Run `jules remote list --repo` to verify |
| "Login Related" | Missing credentials | Run `jules login` or check `~/.jules/cache/oauth_creds.json` |
| TTY errors | Terminal interaction issues | Use `< /dev/null` suffix or the wrapper scripts |
