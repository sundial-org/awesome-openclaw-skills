# Cleaning up Dokku and containers

How to free disk space and remove unused apps, containers, and images. Reference: Docker [Prune unused objects](https://docs.docker.com/engine/reference/commandline/system_prune/), Dokku discussions.

## Removing an app

To remove a single app and its add-ons:

```bash
dokku apps:destroy <app>
# Prompts for app name; use --force to skip:
dokku --force apps:destroy <app>
```

This unlinks services and removes app config; linked services (e.g. Postgres) keep their data unless removed separately.

## Docker prune (containers and images)

Run on the Dokku host. These affect **all** Docker objects, not just Dokku apps; use with care.

### System prune (containers, networks, dangling images, build cache)

```bash
sudo docker system prune
sudo docker system prune -f   # skip confirmation
```

### Remove unused images (including non-dangling)

```bash
sudo docker system prune -a
sudo docker system prune -a -f
```

### Include anonymous volumes

```bash
sudo docker system prune -a --volumes -f
```

### Prune by type

```bash
sudo docker container prune -f   # stopped containers
sudo docker image prune -f      # dangling images only
sudo docker image prune -a -f   # all unused images
sudo docker volume prune -f     # unused volumes
sudo docker builder prune -f    # build cache
```

Filter by age, e.g. older than 24 hours:

```bash
sudo docker image prune -a --filter "until=24h" -f
```

## Dokku automatic builder prune

As of Dokku **0.35.0**, the platform runs `docker builder prune` once daily at **4:05am** server time to remove build cache. No manual command needed for routine build-cache cleanup.

## Optional: dokku-nuke plugin

For **aggressive** cleanup (e.g. wipe everything): the community plugin [dokku-nuke](https://github.com/dokku-community/dokku-nuke) stops all running containers and deletes all containers and images. Use only when you intend to remove all apps and images from the host.

```bash
sudo dokku plugin:install https://github.com/dokku-community/dokku-nuke.git
# Then run per plugin docs (destructive).
```

Prefer `dokku apps:destroy` and `docker system prune` for normal cleanup.
