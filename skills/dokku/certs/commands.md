# Certs commands

All `dokku certs:*` subcommands. Manage SSL/TLS certificates for apps.

## certs:add

Add a certificate and key for an app. Certificate is associated with the app's domains.

```bash
dokku certs:add <app> <cert.pem> <key.pem>
dokku certs:add <app> < fullchain.pem < privkey.pem
```

## certs:remove

Remove certificate for an app.

```bash
dokku certs:remove <app>
```

## certs:generate

Generate a self-signed certificate for an app (development only).

```bash
dokku certs:generate <app>
dokku certs:generate <app> <domain>
```

## certs:update

Update certificate for an app (e.g. after renewal).

```bash
dokku certs:update <app> <cert.pem> <key.pem>
```

## certs:report

Display cert report for one or all apps.

```bash
dokku certs:report
dokku certs:report <app>
```

## Letsencrypt plugin

For automated SSL, install the optional letsencrypt plugin:

```bash
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku letsencrypt:set --global email your@email.com
dokku domains:set <app> <app>.your.domain.com
dokku letsencrypt:enable <app>
dokku letsencrypt:cron-job --add
```
