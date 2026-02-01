# Network commands

All `dokku network:*` subcommands. Manage network configuration for apps and the host.

## network:report

Display network report for one or all apps. Use flags for single values.

```bash
dokku network:report
dokku network:report <app>
dokku network:report --global
```

## network:set

Set network property for an app (e.g. bind-all-interfaces).

```bash
dokku network:set <app> bind-all-interfaces true
dokku network:set <app> bind-all-interfaces false
```

## network:set-global

Set global network property.

```bash
dokku network:set --global <key> <value>
```

## Common properties

- **bind-all-interfaces** — Bind app to all interfaces (0.0.0.0). Useful when not using a reverse proxy or for custom networking.

## Proxy plugin

Port mapping and proxy behavior are often managed by the proxy plugin (e.g. `dokku proxy:ports-set`, `dokku proxy:enable`). See proxy/nginx docs for request routing.
