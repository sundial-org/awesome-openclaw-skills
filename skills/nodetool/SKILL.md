---
name: nodetool
description: Visual AI workflow builder - ComfyUI meets n8n for LLM agents, RAG pipelines, and multimodal data flows. Local-first, open source (AGPL-3.0).
---

# NodeTool

Visual AI workflow builder combining ComfyUI's node-based flexibility with n8n's automation power. Build LLM agents, RAG pipelines, and multimodal data flows on your local machine.

## Quick Start

```bash
# See system info
nodetool info

# List workflows
nodetool workflows list

# Run a workflow interactively
nodetool run <workflow_id>

# Start of chat interface
nodetool chat

# Start of web server
nodetool serve
```

## Installation

### Linux / macOS

Quick one-line installation:

```bash
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash
```

With custom directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash --prefix ~/.nodetool
```

**Non-interactive mode (automatic, no prompts):**

Both scripts support silent installation:

```bash
# Linux/macOS - use -y
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash -y

# Windows - use -Yes
irm https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.ps1 | iex; .\install.ps1 -Yes
```

**What happens with non-interactive mode:**
- All confirmation prompts are skipped automatically
- Installation proceeds without requiring user input
- Perfect for CI/CD pipelines or automated setups

### Windows

Quick one-line installation:

```powershell
irm https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.ps1 | iex
```

With custom directory:

```powershell
.\install.ps1 -Prefix "C:\nodetool"
```

Non-interactive mode:

```powershell
.\install.ps1 -Yes
```

## Core Commands

### Workflows

Manage and execute NodeTool workflows:

```bash
# List all workflows (user + example)
nodetool workflows list

# Get details for a specific workflow
nodetool workflows get <workflow_id>

# Run workflow by ID
nodetool run <workflow_id>

# Run workflow from file
nodetool run workflow.json

# Run with JSONL output (for automation)
nodetool run <workflow_id> --jsonl
```

### Run Options

Execute workflows in different modes:

```bash
# Interactive mode (default) - pretty output
nodetool run workflow_abc123

# JSONL mode - streaming JSON for subprocess use
nodetool run workflow_abc123 --jsonl

# Stdin mode - pipe RunJobRequest JSON
echo '{"workflow_id":"abc","user_id":"1","auth_token":"token","params":{}}' | nodetool run --stdin --jsonl

# With custom user ID
nodetool run workflow_abc123 --user-id "custom_user_id"

# With auth token
nodetool run workflow_abc123 --auth-token "my_auth_token"
```

### Assets

Manage workflow assets (nodes, models, files):

```bash
# List all assets
nodetool assets list

# Get asset details
nodetool assets get <asset_id>
```

### Packages

Manage NodeTool packages (export workflows, generate docs):

```bash
# List packages
nodetool package list

# Generate documentation
nodetool package docs

# Generate node documentation
nodetool package node-docs

# Generate workflow documentation (Jekyll)
nodetool package workflow-docs

# Scan directory for nodes and create package
nodetool package scan

# Initialize new package project
nodetool package init
```

### Jobs

Manage background job executions:

```bash
# List jobs for a user
nodetool jobs list

# Get job details
nodetool jobs get <job_id>

# Get job logs
nodetool jobs logs <job_id>

# Start background job for workflow
nodetool jobs start <workflow_id>
```

### Deployment

Deploy NodeTool to cloud platforms (RunPod, GCP, Docker):

```bash
# Initialize deployment.yaml
nodetool deploy init

# List deployments
nodetool deploy list

# Add new deployment
nodetool deploy add

# Apply deployment configuration
nodetool deploy apply

# Check deployment status
nodetool deploy status <deployment_name>

# View deployment logs
nodetool deploy logs <deployment_name>

# Destroy deployment
nodetool deploy destroy <deployment_name>

# Manage collections on deployed instance
nodetool deploy collections

# Manage database on deployed instance
nodetool deploy database

# Manage workflows on deployed instance
nodetool deploy workflows

# See what changes will be made
nodetool deploy plan
```

### Model Management

Discover and manage AI models (HuggingFace, Ollama):

```bash
# List cached HuggingFace models by type
nodetool model list-hf <hf_type>

# List all HuggingFace cache entries
nodetool model list-hf-all

# List supported HF types
nodetool model hf-types

# Inspect HuggingFace cache
nodetool model hf-cache

# Scan cache for info
nodetool admin scan-cache
```

### Admin

Maintain model caches and clean up:

```bash
# Calculate total cache size
nodetool admin cache-size

# Delete HuggingFace model from cache
nodetool admin delete-hf <model_name>

# Download HuggingFace models with progress
nodetool admin download-hf <model_name>

# Download Ollama models
nodetool admin download-ollama <model_name>
```

### Chat & Server

Interactive chat and web interface:

```bash
# Start CLI chat
nodetool chat

# Start chat server (WebSocket + SSE)
nodetool chat-server

# Start FastAPI backend server
nodetool serve --host 0.0.0.0 --port 8000

# With static assets folder
nodetool serve --static-folder ./static --apps-folder ./apps

# Development mode with auto-reload
nodetool serve --reload

# Production mode
nodetool serve --production
```

### Proxy

Start reverse proxy with HTTPS:

```bash
# Start proxy server
nodetool proxy

# Check proxy status
nodetool proxy-status

# Validate proxy config
nodetool proxy-validate-config

# Run proxy daemon with ACME HTTP + HTTPS
nodetool proxy-daemon
```

### Other Commands

```bash
# View settings and secrets
nodetool settings show

# Generate custom HTML app for workflow
nodetool vibecoding

# Run workflow and export as Python DSL
nodetool dsl-export

# Export workflow as Gradio app
nodetool gradio-export

# Regenerate DSL
nodetool codegen

# Manage database migrations
nodetool migrations

# Synchronize database with remote
nodetool sync
```

## Use Cases

### Workflow Execution

Run a NodeTool workflow and get structured output:

```bash
# Run workflow interactively
nodetool run my_workflow_id

# Run and stream JSONL output
nodetool run my_workflow_id --jsonl | jq -r '.[] | "\(.status) | \(.output)"'
```

### Package Creation

Generate documentation for a custom package:

```bash
# Scan for nodes and create package
nodetool package scan

# Generate complete documentation
nodetool package docs
```

### Deployment

Deploy a NodeTool instance to the cloud:

```bash
# Initialize deployment config
nodetool deploy init

# Add RunPod deployment
nodetool deploy add

# Deploy and start
nodetool deploy apply
```

### Model Management

Check and manage cached AI models:

```bash
# List all available models
nodetool model list-hf-all

# Inspect cache
nodetool model hf-cache
```

## Installation

### Linux / macOS

Quick one-line installation:

```bash
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash
```

With custom directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash --prefix ~/.nodetool
```

**Non-interactive mode (automatic, no prompts):**

Both scripts support silent installation:

```bash
# Linux/macOS - use -y
curl -fsSL https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.sh | bash -y

# Windows - use -Yes
irm https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.ps1 | iex; .\install.ps1 -Yes
```

**What happens with non-interactive mode:**
- All confirmation prompts are skipped automatically
- Installation proceeds without requiring user input
- Perfect for CI/CD pipelines or automated setups

### Windows

Quick one-line installation:

```powershell
irm https://raw.githubusercontent.com/nodetool-ai/nodetool/refs/heads/main/install.ps1 | iex
```

With custom directory:

```powershell
.\install.ps1 -Prefix "C:\nodetool"
```

Non-interactive mode:

```powershell
.\install.ps1 -Yes
```

## What Gets Installed

The installer sets up:
- **micromamba** — Python package manager (conda replacement)
- **NodeTool environment** — Conda env at `~/.nodetool/env`
- **Python packages** — `nodetool-core`, `nodetool-base` from NodeTool registry
- **Wrapper scripts** — `nodetool` CLI available from any terminal

### Environment Setup

After installation, these variables are automatically configured:

```bash
# Conda environment
export MAMBA_ROOT_PREFIX="$HOME/.nodetool/micromamba"
export PATH="$HOME/.nodetool/env/bin:$HOME/.nodetool/env/Library/bin:$PATH"

# Model cache directories
export HF_HOME="$HOME/.nodetool/cache/huggingface"
export OLLAMA_MODELS="$HOME/.nodetool/cache/ollama"
```

## System Info

Check NodeTool environment and installed packages:

```bash
nodetool info
```

Output shows:
- Version
- Python version
- Platform/Architecture
- Installed AI packages (OpenAI, Anthropic, Google, HF, Ollama, fal-client)
- Environment variables
- API key status
