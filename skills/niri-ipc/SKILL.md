---
name: niri-ipc
description: Control the Niri Wayland compositor on Linux via its IPC (`niri msg --json` / $NIRI_SOCKET). Use when you need to query Niri state (outputs/workspaces/windows/focused window) or perform actions (focus/move/close windows, switch workspaces, spawn commands, reload config) from an OpenClaw agent running on a Niri session.
---

# Niri IPC

Use Niri IPC through the `niri msg` CLI (preferred) or by writing JSON requests to `$NIRI_SOCKET`.

This skill assumes:
- You are on Linux with Niri running.
- `$NIRI_SOCKET` is set (usually true inside the Niri session).

## Quick start (recommended)

Use the bundled helper script (wrapper around `niri msg --json`):

```bash
./skills/niri-ipc/scripts/niri.py version
./skills/niri-ipc/scripts/niri.py outputs
./skills/niri-ipc/scripts/niri.py workspaces
./skills/niri-ipc/scripts/niri.py windows
./skills/niri-ipc/scripts/niri.py focused-window
```

## Deeper control

### 1) High-level helpers (window matching)

Use `scripts/niri_ctl.py` when you want to refer to windows by **title/app_id substring** instead of ids:

```bash
# List windows (optionally filtered)
./skills/niri-ipc/scripts/niri_ctl.py list-windows --query firefox

# Focus a window by substring match
./skills/niri-ipc/scripts/niri_ctl.py focus firefox

# Close a matched window (focus then close)
./skills/niri-ipc/scripts/niri_ctl.py close firefox

# Move a matched window to a workspace (by index or by name)
./skills/niri-ipc/scripts/niri_ctl.py move-to-workspace firefox 3
./skills/niri-ipc/scripts/niri_ctl.py move-to-workspace firefox web

# Focus a workspace by index or name
./skills/niri-ipc/scripts/niri_ctl.py focus-workspace 2
./skills/niri-ipc/scripts/niri_ctl.py focus-workspace web
```

### 2) Full IPC access (raw socket)

Use `scripts/niri_socket.py` to talk to `$NIRI_SOCKET` directly (newline-delimited JSON):

```bash
# Send a simple request (JSON string)
./skills/niri-ipc/scripts/niri_socket.py raw '"FocusedWindow"'

# Batch requests: one JSON request per line on stdin
printf '%s\n' '"FocusedWindow"' '"Workspaces"' | ./skills/niri-ipc/scripts/niri_socket.py stdin

# Event stream (prints JSON events until interrupted)
./skills/niri-ipc/scripts/niri_socket.py event-stream
```

### Actions

Pass through Niri actions:

```bash
# Focus workspace by index
./skills/niri-ipc/scripts/niri.py action focus-workspace 2

# Move focused window to workspace
./skills/niri-ipc/scripts/niri.py action move-window-to-workspace 3

# Focus a window by id
./skills/niri-ipc/scripts/niri.py action focus-window 123

# Close focused window
./skills/niri-ipc/scripts/niri.py action close-window

# Reload niri config
./skills/niri-ipc/scripts/niri.py action load-config-file

# Spawn (no shell)
./skills/niri-ipc/scripts/niri.py action spawn -- alacritty

# Spawn through shell
./skills/niri-ipc/scripts/niri.py action spawn-sh -- 'notify-send hello'
```

### Output configuration

Use `niri msg output ...` via the wrapper:

```bash
./skills/niri-ipc/scripts/niri.py output --help
```

## Working directly with `niri msg`

If you don’t want the helper script, call Niri directly:

```bash
niri msg --json windows
niri msg --json action focus-workspace 2
```

Tip: if `niri msg` parsing errors happen after upgrades, restart the compositor (new `niri msg` against old compositor is a common mismatch).

## Event stream

For status bars/daemons: Niri can stream events.

```bash
# Raw JSON event lines (runs until interrupted)
./skills/niri-ipc/scripts/niri.py event-stream

# Just a few lines for a quick test
./skills/niri-ipc/scripts/niri.py event-stream --lines 5
```

## Troubleshooting

- If commands fail with “NIRI_SOCKET is not set”: run inside your Niri session, or export the socket path.
- If you need the socket protocol details, read: `./skills/niri-ipc/references/ipc.md`.
- If your goal is complex automation (pick the right window by title/app_id, etc.), first query `windows`, then act by window id.
