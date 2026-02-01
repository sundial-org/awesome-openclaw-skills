# Run commands

One-off and background process execution in the app environment.

## run

Run a one-off command in a new container. Waits for completion.

```bash
dokku run <app> <cmd> [args...]
dokku run <app> --env KEY=value <cmd>
dokku run --no-tty <app> <cmd>
dokku run --rm <app> <cmd>   # remove container after run
```

Example:

```bash
dokku run node-js-app bundle exec rake db:migrate
```

## run:detached

Run a command in the background. Returns immediately with container ID.

```bash
dokku run:detached <app> <cmd> [args...]
dokku run --detach <app> <cmd> [args...]
```

Use for long-running tasks (e.g. installs, migrations) so the agent does not block. Optionally pass `--env`, `--no-tty`, `--ttl-seconds` (default 24h).

## Agent-side backgrounding

For long-running deploy or install steps **from the agent**, run the shell command via the exec tool with:

- `background: true` — start in background immediately, or
- Short `yieldMs` — auto-background after a few seconds.

Then use the process tool to poll or read logs as needed.
