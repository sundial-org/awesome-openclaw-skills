# Upgrading Dokku

How to upgrade Dokku. **Always check migration guides** for each version between your current and target version. Reference: [dokku.com/docs/getting-started/upgrading](https://dokku.com/docs/getting-started/upgrading).

## Migration guides

Before upgrading, read the migration guides for every version you are jumping over:

- [Upgrading to 0.35](https://dokku.com/docs/appendices/0.35.0-migration-guide/)
- [Upgrading to 0.34](https://dokku.com/docs/appendices/0.34.0-migration-guide/)
- [Upgrading to 0.33](https://dokku.com/docs/appendices/0.33.0-migration-guide/)
- [Upgrading to 0.32](https://dokku.com/docs/appendices/0.32.0-migration-guide/)
- [Upgrading to 0.31](https://dokku.com/docs/appendices/0.31.0-migration-guide/)
- [Upgrading to 0.30](https://dokku.com/docs/appendices/0.30.0-migration-guide/)
- [Upgrading to 0.29](https://dokku.com/docs/appendices/0.29.0-migration-guide/)
- … and older versions: [dokku.com/docs/appendices](https://dokku.com/docs/appendices/)

Check current version: `dokku version`. If your version is **pre-0.3.0**, a fresh install on a new server is recommended instead of upgrading.

## Before upgrading

If you will update Docker or the herokuish package at the same time, stop all apps before upgrading and rebuild after.

**0.22.0 and newer:**

```bash
dokku ps:stop --all
```

**0.11.4–0.21.4:**

```bash
dokku ps:stopall
```

**0.8.1–0.11.3:**

```bash
dokku --quiet apps:list | xargs -L1 dokku ps:stop
```

**Older than 0.8.1:**

```bash
dokku --quiet apps | xargs -L1 dokku ps:stop
```

If only the `dokku` package is being upgraded (no Docker/herokuish change), stopping is optional.

## Upgrade methods

### Using dokku-update (recommended)

`dokku-update` automates many upgrade steps. It does **not** support upgrading to a specific version; use apt for that.

```bash
# Install (if not already)
sudo apt-get update
sudo apt-get install dokku-update

# Run upgrade
sudo dokku-update
```

### Using apt

If Dokku was installed via `bootstrap.sh` or `apt-get install dokku`:

```bash
sudo apt-get update
sudo apt-get --no-install-recommends install dokku herokuish sshcommand plugn gliderlabs-sigil dokku-update dokku-event-listener

# Or upgrade everything:
sudo apt-get upgrade
```

To upgrade to a **specific version** (version without `v` prefix):

```bash
sudo apt-get install dokku=0.37.5
```

### From source

Only if you originally installed from source:

```bash
cd ~/dokku
git pull --tags origin master
sudo DOKKU_BRANCH=master make install
```

## After upgrading

Rebuild apps to pick up new buildpacks and runtime changes:

```bash
dokku ps:rebuild --all
```

If apps were deployed via tags/tar, rebuild each app individually: `dokku ps:rebuild <app>`.

## Security updates

- Follow [@dokku](https://twitter.com/dokku) for security-related updates.
- Enable unattended upgrades for the OS (Debian/Ubuntu) and keep Docker updated per [Docker documentation](https://docs.docker.com/).
