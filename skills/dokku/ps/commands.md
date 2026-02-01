# Process (ps) commands

All `dokku ps:*` subcommands. Manage app containers and scaling.

## ps:scale

Get or set process counts. Multiple process types can be scaled at once.

```bash
dokku ps:scale <app>                    # show current
dokku ps:scale <app> web=1
dokku ps:scale <app> web=1 worker=2
dokku ps:scale --skip-deploy <app> web=1
```

## ps:rebuild

Rebuild an app from source (no new git push).

```bash
dokku ps:rebuild <app>
dokku ps:rebuild --all
dokku ps:rebuild --all --parallel 2
dokku ps:rebuild --all --parallel -1    # use CPU count
```

## ps:restart

Restart an app or a specific process type.

```bash
dokku ps:restart <app>
dokku ps:restart <app> web
dokku ps:restart --all
dokku ps:restart --all --parallel 2
```

## ps:start

Start stopped containers. No-op if already running.

```bash
dokku ps:start <app>
dokku ps:start --all
dokku ps:start --all --parallel 2
```

## ps:stop

Stop all containers for an app. Results in 502 from proxy until started again.

```bash
dokku ps:stop <app>
dokku ps:stop --all
dokku ps:stop --all --parallel 2
```

## ps:restore

Start previously running apps (e.g. after server reboot). Usually triggered by Dokku init; can be run manually.

```bash
dokku ps:restore <app>
dokku ps:restore
```

## ps:set

Set or clear ps properties for an app (e.g. stop-timeout, procfile-path, restart-policy).

```bash
dokku ps:set <app> stop-timeout 60
dokku ps:set <app> stop-timeout        # clear (use default)
dokku ps:set --global stop-timeout 60
dokku ps:set <app> procfile-path .dokku/Procfile
dokku ps:set <app> restart-policy always
dokku ps:set <app> restart-policy on-failure:20
```

Restart policy options: `always`, `no`, `unless-stopped`, `on-failure`, `on-failure:N`.

## ps:inspect

Display sanitized `docker inspect` output for an app's containers (safe for sharing; env vars stripped).

```bash
dokku ps:inspect <app>
```

## ps:report

Display process report for one or all apps. Use flags for single values (e.g. `--deployed`).

```bash
dokku ps:report
dokku ps:report <app>
dokku ps:report <app> --deployed
```
