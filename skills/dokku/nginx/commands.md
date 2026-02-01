# Nginx commands

All `dokku nginx:*` subcommands. Apply when using the default nginx proxy plugin.

## nginx:build-config

Rebuild nginx configuration for an app (or all apps).

```bash
dokku nginx:build-config <app>
dokku nginx:build-config --global
```

## nginx:show-config

Display current nginx config for an app.

```bash
dokku nginx:show-config <app>
```

## nginx:set

Set nginx property for an app (e.g. bind-address-ipv4, bind-address-ipv6, hsts, hsts-max-age).

```bash
dokku nginx:set <app> <key> <value>
dokku nginx:set <app> <key>    # clear
```

## nginx:validate-config

Validate nginx configuration for an app.

```bash
dokku nginx:validate-config <app>
```

## nginx:access-logs

View nginx access logs. Use `-t` to follow.

```bash
dokku nginx:access-logs <app>
dokku nginx:access-logs -t <app>
```

## nginx:error-logs

View nginx error logs. Use `-t` to follow.

```bash
dokku nginx:error-logs <app>
dokku nginx:error-logs -t <app>
```
