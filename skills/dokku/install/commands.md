# Installing Dokku

How to install Dokku on a server. Reference: [dokku.com/docs/getting-started/installation](https://dokku.com/docs/getting-started/installation).

## System requirements

- **OS:** Ubuntu 22.04/24.04 or Debian 11+ x64
- **Arch:** AMD64 (x86_64) or arm64 (armv8)
- **Memory:** Minimum 1GB for Docker scheduler (or add swap). K3s scheduler: 2GB per node.
- **Domain:** Optional but recommended (A record or wildcard to server IP).

## Bootstrap install (recommended)

Install the latest stable version (replace `v0.37.5` with desired tag from [releases](https://github.com/dokku/dokku/releases)):

```bash
wget -NP . https://dokku.com/install/v0.37.5/bootstrap.sh
sudo DOKKU_TAG=v0.37.5 bash bootstrap.sh
```

Installation takes about 5–10 minutes. Then configure SSH and domain.

## Post-install setup

### Add SSH key

```bash
cat ~/.ssh/authorized_keys | sudo dokku ssh-keys:add admin
```

### Set global domain

```bash
# Use a domain with A record pointing at your server
dokku domains:set-global dokku.me

# Or use server IP
dokku domains:set-global 10.0.0.2

# Or use sslip.io for subdomain support (e.g. 10.0.0.2.sslip.io)
dokku domains:set-global 10.0.0.2.sslip.io
```

## Alternative installation methods

- **Debian package (manual):** Step-by-step with debconf. See [dokku.com/docs/getting-started/install/debian](https://dokku.com/docs/getting-started/install/debian).
- **Advanced installation:** From source, unattended install, provider-specific (DigitalOcean, DreamHost, Azure). See [dokku.com/docs/getting-started/advanced-installation](https://dokku.com/docs/getting-started/advanced-installation).
- **Docker scheduler vs K3s:** Bootstrap defaults to Docker; K3s is an option for multi-node. See docs for your target setup.

## Verify

```bash
dokku version
dokku apps:list
```
