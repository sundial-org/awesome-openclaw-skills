# Niri IPC quick reference

Use `niri msg` (recommended) or talk to the IPC socket directly.

## Prefer `niri msg --json`

- `niri msg --help` lists commands.
- Use `--json` for scripts; human-readable output is not stable.

Common commands:

- `niri msg --json version`
- `niri msg --json outputs`
- `niri msg --json workspaces`
- `niri msg --json windows`
- `niri msg --json focused-window`
- `niri msg --json action focus-workspace 2`

## Programmatic socket access

- Socket path: `$NIRI_SOCKET`
- Protocol: newline-delimited JSON.
- Write one JSON `Request` per line; read one JSON `Reply` per line.

Debug with socat:

```sh
socat STDIO "$NIRI_SOCKET"
"FocusedWindow"
# => {"Ok":{"FocusedWindow":{...}}}
```

To see how `niri msg` formats more complex requests:

```sh
socat STDIO UNIX-LISTEN:temp.sock
# in another terminal:
env NIRI_SOCKET=./temp.sock niri msg action focus-workspace 2
# socat shows:
# {"Action":{"FocusWorkspace":{"reference":{"Index":2}}}}
```

For the full schema/types, see the upstream niri-ipc crate docs:
https://yalter.github.io/niri/niri_ipc/
