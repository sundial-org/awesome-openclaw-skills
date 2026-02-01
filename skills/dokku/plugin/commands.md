# Plugin commands

All `dokku plugin:*` subcommands. Manage Dokku plugins (install, update, list).

## plugin:list

List active plugins and versions.

```bash
dokku plugin:list
```

## plugin:install

Download and install a plugin. Usually requires root/sudo.

```bash
sudo dokku plugin:install <url>
# Example:
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git
```

## plugin:update

Update named plugin(s) to latest. Omit name to update all.

```bash
dokku plugin:update [<plugin> ...]
```

## plugin:uninstall

Uninstall a plugin.

```bash
sudo dokku plugin:uninstall <plugin>
```

## plugin:enable

Enable a previously disabled plugin.

```bash
dokku plugin:enable <plugin>
```

## plugin:disable

Disable a plugin (keeps installed, stops it from running).

```bash
dokku plugin:disable <plugin>
```

## plugin:trigger

Trigger an arbitrary plugin hook (advanced; for plugin development or scripting).

```bash
dokku plugin:trigger <trigger> [args...]
```
