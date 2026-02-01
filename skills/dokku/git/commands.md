# Git / deploy commands

Git repository and deployment. Deploy via `git push` or from a Docker image.

## git:from-image

Initialize or update an app repository from a Docker image.

```bash
dokku git:from-image <app> <docker-image>
dokku git:from-image --force <app> <docker-image>
```

Example:

```bash
dokku git:from-image node-js-app my-registry/node-js-getting-started:latest
```

## git:set

Set or clear git properties for an app (e.g. deploy branch).

```bash
dokku git:set <app> deploy-branch <branch>
dokku git:set <app> deploy-branch    # clear
```

## git:sync

Clone or fetch an app from a remote git repository.

```bash
dokku git:sync <app> <remote-url>
```

## git:initialize

Manually initialize git repository for an app (normally created on first push).

```bash
dokku git:initialize <app>
```

## Deploy via git push

From your local machine:

```bash
git remote add dokku dokku@<host>:<app-name>
git push dokku <branch>:master
# or if deploy-branch is set to main:
git push dokku main
```

Remote username must be `dokku`. Use `ssh://dokku@<host>:<app-name>` if your tool needs a full URL.

## Changing deploy branch

On Dokku host:

```bash
dokku git:set <app> deploy-branch main
```

Then push: `git push dokku main`.
