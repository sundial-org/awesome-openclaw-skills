# Storage commands

All `dokku storage:*` subcommands. Manage persistent volumes (bind mounts) for apps.

## storage:list

List storage mounts for an app (or all apps).

```bash
dokku storage:list <app>
dokku storage:list
```

## storage:mount

Mount a host path into the app container. Format: `host_path:container_path`.

```bash
dokku storage:mount <app> /host/path:/app/data
```

Multiple mounts can be added. Changes take effect on next deploy/restart.

## storage:unmount

Remove a storage mount.

```bash
dokku storage:unmount <app> /host/path:/app/data
```

## storage:report

Display storage report for one or all apps.

```bash
dokku storage:report
dokku storage:report <app>
```

## Notes

- Host path must exist on the Dokku server.
- Use for persistent data (e.g. uploads, SQLite, cache). Container filesystem is ephemeral across deploys.
