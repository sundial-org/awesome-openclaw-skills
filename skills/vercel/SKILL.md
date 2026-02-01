---
name: vercel
description: Deploy applications and manage projects with complete CLI reference. Commands for deployments, projects, domains, environment variables, and live documentation access.
metadata: {"clawdbot":{"emoji":"▲","requires":{"bins":["vercel","curl"]}}}
---

# Vercel

Complete Vercel CLI reference and documentation access.

## When to Use
- Deploying applications to Vercel
- Managing projects, domains, and environment variables
- Running local development server
- Viewing deployment logs and status
- Looking up Vercel documentation

---

## Documentation

Fetch any Vercel docs page as markdown:

```bash
curl -s "https://vercel.com/docs/<path>" -H 'accept: text/markdown'
```

**Get the full sitemap to discover all available pages:**
```bash
curl -s "https://vercel.com/docs/sitemap.md" -H 'accept: text/markdown'
```

---

## CLI Commands

### Deployment

#### `vercel` / `vercel deploy [path]`
Deploy the current directory or specified path.

**Options:**
- `--prod` - Deploy to production
- `-e KEY=VALUE` - Set runtime environment variables
- `-b KEY=VALUE` - Set build-time environment variables
- `--prebuilt` - Deploy prebuilt output (use with `vercel build`)
- `--force` - Force new deployment even if unchanged
- `--no-wait` - Don't wait for deployment to finish
- `-y, --yes` - Skip prompts, use defaults

**Examples:**
```bash
vercel                          # deploy current directory
vercel --prod                   # deploy to production
vercel /path/to/project         # deploy specific path
vercel -e NODE_ENV=production   # with env var
vercel build && vercel --prebuilt  # prebuilt deploy
```

#### `vercel build`
Build the project locally into `./vercel/output`.

```bash
vercel build
```

#### `vercel dev [dir]`
Start local development server.

**Options:**
- `-l, --listen <URI>` - Port/address (default: 0.0.0.0:3000)

**Examples:**
```bash
vercel dev                  # start on port 3000
vercel dev --listen 8080    # start on port 8080
```

---

### Project Management

#### `vercel link [path]`
Link local directory to a Vercel project.

**Options:**
- `-p, --project <NAME>` - Specify project name
- `-y, --yes` - Skip prompts

**Examples:**
```bash
vercel link
vercel link --yes
vercel link -p my-project
```

#### `vercel projects`
Manage projects.

```bash
vercel projects list              # list all projects
vercel projects add <name>        # create new project
vercel projects inspect [name]    # show project details
vercel projects remove <name>     # delete project
```

#### `vercel pull [path]`
Pull project settings and env vars from cloud.

```bash
vercel pull
```

---

### Environment Variables

#### `vercel env`
Manage environment variables.

```bash
vercel env list [environment]                    # list env vars
vercel env add <name> [environment]              # add env var
vercel env remove <name> [environment]           # remove env var
vercel env pull [filename]                       # pull to .env.local
```

**Environments:** `development`, `preview`, `production`

**Examples:**
```bash
vercel env list production
vercel env add DATABASE_URL production
vercel env pull .env.local
```

---

### Domains & Aliases

#### `vercel domains`
Manage domain names.

```bash
vercel domains list                          # list domains
vercel domains add <domain> <project>        # add domain
vercel domains inspect <domain>              # show domain info
vercel domains remove <domain>               # remove domain
vercel domains buy <domain>                  # purchase domain
vercel domains transfer-in <domain>          # transfer domain to Vercel
```

#### `vercel alias`
Manage deployment aliases.

```bash
vercel alias list                                    # list aliases
vercel alias set <deployment> <alias>                # create alias
vercel alias remove <alias>                          # remove alias
```

**Examples:**
```bash
vercel alias set my-app-abc123.vercel.app my-app.vercel.app
vercel alias set my-app-abc123.vercel.app custom-domain.com
```

---

### Deployments

#### `vercel ls [app]` / `vercel list`
List deployments.

```bash
vercel ls
vercel ls my-project
```

#### `vercel inspect [id]`
Display deployment information.

```bash
vercel inspect <deployment-url-or-id>
```

#### `vercel logs <url|id>`
View runtime logs for a deployment.

**Options:**
- `-j, --json` - Output as JSON (compatible with jq)

**Examples:**
```bash
vercel logs my-app.vercel.app
vercel logs <deployment-id> --json
vercel logs <deployment-id> --json | jq 'select(.level == "error")'
```

#### `vercel promote <url|id>`
Promote deployment to production.

```bash
vercel promote <deployment-url-or-id>
```

#### `vercel rollback [url|id]`
Rollback to previous deployment.

```bash
vercel rollback
vercel rollback <deployment-url-or-id>
```

#### `vercel redeploy [url|id]`
Rebuild and deploy a previous deployment.

```bash
vercel redeploy <deployment-url-or-id>
```

#### `vercel rm <id>` / `vercel remove`
Remove a deployment.

```bash
vercel rm <deployment-url-or-id>
```

---

### Authentication & Teams

```bash
vercel login [email]      # log in or create account
vercel logout             # log out
vercel whoami             # show current user
vercel switch [scope]     # switch between scopes/teams
vercel teams              # manage teams
```

---

### Other Commands

```bash
vercel open               # open project in dashboard
vercel init [example]     # initialize from example
vercel install [name]     # install marketplace integration
vercel integration        # manage integrations
vercel certs              # manage SSL certificates
vercel dns                # manage DNS records
vercel bisect             # binary search for bug-introducing deployment
```

---

## Global Options

Available on all commands:

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help |
| `-v, --version` | Show version |
| `-d, --debug` | Debug mode |
| `-t, --token <TOKEN>` | Auth token |
| `-S, --scope` | Set scope/team |
| `--cwd <DIR>` | Working directory |
| `-A, --local-config <FILE>` | Path to vercel.json |
| `--no-color` | Disable colors |

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy | `vercel` or `vercel --prod` |
| Dev server | `vercel dev` |
| Link project | `vercel link` |
| List deployments | `vercel ls` |
| View logs | `vercel logs <url>` |
| Add env var | `vercel env add <name> <env>` |
| Pull env vars | `vercel env pull` |
| Rollback | `vercel rollback` |
| Add domain | `vercel domains add <domain> <project>` |
| Get docs | `curl -s "https://vercel.com/docs/<path>" -H 'accept: text/markdown'` |
| Docs sitemap | `curl -s "https://vercel.com/docs/sitemap.md" -H 'accept: text/markdown'` |
