---
name: portainer
description: Control Docker containers and stacks via Portainer API. List containers, start/stop/restart, view logs, and redeploy stacks from git.
metadata: {"clawdbot":{"emoji":"🐳","requires":{"bins":["curl","jq"],"env":["PORTAINER_API_KEY"]},"primaryEnv":"PORTAINER_API_KEY"}}
---

# 🐳 Portainer Skill

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🐳  P O R T A I N E R   C O N T R O L   C L I  🐳      ║
    ║                                                           ║
    ║       Manage Docker containers via Portainer API          ║
    ║            Start, stop, deploy, redeploy                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
```

> *"Docker containers? I'll handle them from my lily pad."* 🐸

---

## 📖 What Does This Skill Do?

The **Portainer Skill** gives you control over your Docker infrastructure through Portainer's REST API. Manage containers, stacks, and deployments without touching the web UI.

**Features:**
- 📊 **Status** — Check Portainer server status
- 🖥️ **Endpoints** — List all Docker environments
- 📦 **Containers** — List, start, stop, restart containers
- 📚 **Stacks** — List and manage Docker Compose stacks
- 🔄 **Redeploy** — Pull from git and redeploy stacks
- 📜 **Logs** — View container logs

---

## ⚙️ Requirements

| What | Details |
|------|---------|
| **Portainer** | Version 2.x with API access |
| **Tools** | `curl`, `jq` |
| **Auth** | API Access Token |

### Setup

1. **Get API Token from Portainer:**
   - Log into Portainer web UI
   - Click username → My Account
   - Scroll to "Access tokens" → Add access token
   - Copy the token (you won't see it again!)

2. **Configure credentials:**
   ```bash
   # Add to ~/.clawdbot/.env
   PORTAINER_URL=https://your-portainer-server:9443
   PORTAINER_API_KEY=ptr_your_token_here
   ```

3. **Ready!** 🚀

---

## 🛠️ Commands

### `status` — Check Portainer Server

```bash
./portainer.sh status
```

**Output:**
```
Portainer v2.27.3
```

---

### `endpoints` — List Environments

```bash
./portainer.sh endpoints
```

**Output:**
```
3: portainer (local) - ✓ online
4: production (remote) - ✓ online
```

---

### `containers` — List Containers

```bash
# List containers on default endpoint (4)
./portainer.sh containers

# List containers on specific endpoint
./portainer.sh containers 3
```

**Output:**
```
steinbergerraum-web-1    running    Up 2 days
cora-web-1               running    Up 6 weeks
minecraft                running    Up 6 weeks (healthy)
```

---

### `stacks` — List All Stacks

```bash
./portainer.sh stacks
```

**Output:**
```
25: steinbergerraum - ✓ active
33: cora - ✓ active
35: minecraft - ✓ active
4: pulse-website - ✗ inactive
```

---

### `stack-info` — Stack Details

```bash
./portainer.sh stack-info 25
```

**Output:**
```json
{
  "Id": 25,
  "Name": "steinbergerraum",
  "Status": 1,
  "EndpointId": 4,
  "GitConfig": "https://github.com/user/repo",
  "UpdateDate": "2026-01-25T08:44:56Z"
}
```

---

### `redeploy` — Pull & Redeploy Stack 🔄

```bash
./portainer.sh redeploy 25
```

**Output:**
```
✓ Stack 'steinbergerraum' redeployed successfully
```

This will:
1. Pull latest code from git
2. Rebuild containers if needed
3. Restart the stack

---

### `start` / `stop` / `restart` — Container Control

```bash
# Start a container
./portainer.sh start steinbergerraum-web-1

# Stop a container
./portainer.sh stop steinbergerraum-web-1

# Restart a container
./portainer.sh restart steinbergerraum-web-1

# Specify endpoint (default: 4)
./portainer.sh restart steinbergerraum-web-1 4
```

**Output:**
```
✓ Container 'steinbergerraum-web-1' restarted
```

---

### `logs` — View Container Logs

```bash
# Last 100 lines (default)
./portainer.sh logs steinbergerraum-web-1

# Last 50 lines
./portainer.sh logs steinbergerraum-web-1 4 50
```

---

## 🎯 Example Workflows

### 🚀 "Deploy Website Update"
```bash
# After merging PR
./portainer.sh redeploy 25
./portainer.sh logs steinbergerraum-web-1 4 20
```

### 🔧 "Debug Container"
```bash
./portainer.sh containers
./portainer.sh logs cora-web-1
./portainer.sh restart cora-web-1
```

### 📊 "System Overview"
```bash
./portainer.sh status
./portainer.sh endpoints
./portainer.sh containers
./portainer.sh stacks
```

---

## 🔧 Troubleshooting

### ❌ "Authentication required / Repository not found"

**Problem:** Stack redeploy fails with git auth error

**Solution:** The stack needs `repositoryGitCredentialID` parameter. The script handles this automatically by reading from the existing stack config.

---

### ❌ "Container not found"

**Problem:** Container name doesn't match

**Solution:** Use exact name from `./portainer.sh containers`:
- Include the full name: `steinbergerraum-web-1` not `steinbergerraum`
- Names are case-sensitive

---

### ❌ "PORTAINER_URL and PORTAINER_API_KEY must be set"

**Problem:** Credentials not configured

**Solution:**
```bash
# Add to ~/.clawdbot/.env
echo "PORTAINER_URL=https://your-server:9443" >> ~/.clawdbot/.env
echo "PORTAINER_API_KEY=ptr_your_token" >> ~/.clawdbot/.env
```

---

## 🔗 Integration with Clawd

```
"Redeploy the website"
→ ./portainer.sh redeploy 25

"Show me running containers"
→ ./portainer.sh containers

"Restart the Minecraft server"
→ ./portainer.sh restart minecraft

"What stacks do we have?"
→ ./portainer.sh stacks
```

---

## 📜 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-25 | Initial release |

---

## 🐸 Credits

```
  @..@
 (----)
( >__< )   "Containers are just fancy lily pads
 ^^  ^^     for your code to hop around!"
```

**Author:** Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)  
**Powered by:** [Portainer](https://portainer.io/) API  
**Part of:** [Clawdbot](https://clawdhub.com) Skills Collection

---

<div align="center">

**Made with 💚 for the Clawdbot Community**

*Ribbit!* 🐸

</div>
