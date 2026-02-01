# Domains commands

All `dokku domains:*` subcommands. Manage app and global domain names.

## domains:add

Add domain(s) to an app.

```bash
dokku domains:add <app> <domain> [<domain> ...]
```

## domains:remove

Remove domain(s) from an app.

```bash
dokku domains:remove <app> <domain> [<domain> ...]
```

## domains:set

Set all domains for an app (replaces existing).

```bash
dokku domains:set <app> <domain> [<domain> ...]
```

## domains:clear

Clear all custom domains for an app.

```bash
dokku domains:clear <app>
```

## domains:reset

Delete all app domains and apply global-configured domains to the app.

```bash
dokku domains:reset <app>
```

## domains:enable

Enable VHOST support for an app (or all with `--all`).

```bash
dokku domains:enable <app>
dokku domains:enable --all
```

## domains:disable

Disable VHOST support for an app (or all with `--all`).

```bash
dokku domains:disable <app>
dokku domains:disable --all
```

## domains:set-global

Set global domain name(s) used as default TLD for all apps.

```bash
dokku domains:set-global <domain> [<domain> ...]
# Examples:
dokku domains:set-global dokku.me
dokku domains:set-global 10.0.0.2
dokku domains:set-global 10.0.0.2.sslip.io
```

## domains:add-global

Add global domain name(s).

```bash
dokku domains:add-global <domain> [<domain> ...]
```

## domains:remove-global

Remove global domain name(s).

```bash
dokku domains:remove-global <domain> [<domain> ...]
```

## domains:clear-global

Clear all global domain names.

```bash
dokku domains:clear-global
```

## domains:report

Display domains report for one or all apps. Use flags for single values (e.g. `--domains-app-enabled`).

```bash
dokku domains:report
dokku domains:report <app>
dokku domains:report --global
```
