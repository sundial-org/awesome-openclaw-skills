---
name: gcloud
description: Manage Google Cloud Platform resources via gcloud CLI. Use for Compute Engine VMs, Cloud Run services, Firebase Hosting, Cloud Storage, and project management. Covers deployment, monitoring, logs, and SSH access.
---

# Google Cloud Platform Skill

Manage GCP resources using `gcloud`, `gsutil`, and `firebase` CLIs.

## Installation

### gcloud CLI (one-time setup)

```bash
# Download and extract
cd ~ && curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xzf google-cloud-cli-linux-x86_64.tar.gz

# Install (adds to PATH via .bashrc)
./google-cloud-sdk/install.sh --quiet --path-update true

# Reload shell or source
source ~/.bashrc

# Authenticate
gcloud auth login
```

### Firebase CLI

```bash
npm install -g firebase-tools
firebase login
```

## Quick Reference

### Authentication & Config

```bash
# List authenticated accounts
gcloud auth list

# Switch active account
gcloud config set account EMAIL

# List projects
gcloud projects list

# Set default project
gcloud config set project PROJECT_ID

# View current config
gcloud config list
```

---

## Compute Engine (VMs)

### List Instances

```bash
# All instances across projects
gcloud compute instances list --project PROJECT_ID

# With specific fields
gcloud compute instances list --project PROJECT_ID \
  --format="table(name,zone,status,networkInterfaces[0].accessConfigs[0].natIP)"
```

### Start/Stop/Restart

```bash
gcloud compute instances start INSTANCE_NAME --zone ZONE --project PROJECT_ID
gcloud compute instances stop INSTANCE_NAME --zone ZONE --project PROJECT_ID
gcloud compute instances reset INSTANCE_NAME --zone ZONE --project PROJECT_ID
```

### SSH Access

```bash
# Interactive SSH
gcloud compute ssh INSTANCE_NAME --zone ZONE --project PROJECT_ID

# Run command remotely
gcloud compute ssh INSTANCE_NAME --zone ZONE --project PROJECT_ID --command "uptime"

# With tunneling (e.g., for local port forwarding)
gcloud compute ssh INSTANCE_NAME --zone ZONE --project PROJECT_ID -- -L 8080:localhost:8080
```

### View Logs

```bash
# Serial port output (boot logs)
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone ZONE --project PROJECT_ID

# Tail logs via SSH
gcloud compute ssh INSTANCE_NAME --zone ZONE --project PROJECT_ID --command "journalctl -f"
```

---

## Cloud Run

### List Services

```bash
# List all services in a region
gcloud run services list --region REGION --project PROJECT_ID

# All regions
gcloud run services list --project PROJECT_ID
```

### Deploy

```bash
# Deploy from source (builds container automatically)
gcloud run deploy SERVICE_NAME \
  --source . \
  --region REGION \
  --project PROJECT_ID \
  --allow-unauthenticated

# Deploy existing container image
gcloud run deploy SERVICE_NAME \
  --image gcr.io/PROJECT_ID/IMAGE:TAG \
  --region REGION \
  --project PROJECT_ID
```

### View Service Details

```bash
gcloud run services describe SERVICE_NAME --region REGION --project PROJECT_ID
```

### View Logs

```bash
# Stream logs
gcloud run services logs read SERVICE_NAME --region REGION --project PROJECT_ID --limit 50

# Or use Cloud Logging
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE_NAME" \
  --project PROJECT_ID --limit 20 --format="table(timestamp,textPayload)"
```

### Update Environment Variables

```bash
gcloud run services update SERVICE_NAME \
  --region REGION \
  --project PROJECT_ID \
  --set-env-vars "KEY1=value1,KEY2=value2"
```

### Traffic Management

```bash
# Route 100% traffic to latest
gcloud run services update-traffic SERVICE_NAME --to-latest --region REGION --project PROJECT_ID

# Split traffic (canary)
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION1=90,REVISION2=10 \
  --region REGION --project PROJECT_ID
```

---

## Firebase Hosting

### List Projects

```bash
firebase projects:list
```

### Deploy

```bash
# Deploy everything (hosting + functions + rules)
firebase deploy --project PROJECT_ID

# Hosting only
firebase deploy --only hosting --project PROJECT_ID

# Specific site (multi-site setup)
firebase deploy --only hosting:SITE_NAME --project PROJECT_ID
```

### Preview Channels

```bash
# Create preview channel
firebase hosting:channel:deploy CHANNEL_NAME --project PROJECT_ID

# List channels
firebase hosting:channel:list --project PROJECT_ID

# Delete channel
firebase hosting:channel:delete CHANNEL_NAME --project PROJECT_ID
```

### Rollback

```bash
# List recent deploys
firebase hosting:releases:list --project PROJECT_ID

# Rollback to specific version
firebase hosting:rollback --project PROJECT_ID
```

---

## Cloud Storage (gsutil)

```bash
# List buckets
gsutil ls

# List contents
gsutil ls gs://BUCKET_NAME/

# Copy file
gsutil cp LOCAL_FILE gs://BUCKET_NAME/path/
gsutil cp gs://BUCKET_NAME/path/file LOCAL_PATH

# Sync directory
gsutil -m rsync -r LOCAL_DIR gs://BUCKET_NAME/path/

# Make public
gsutil iam ch allUsers:objectViewer gs://BUCKET_NAME
```

---

## Logs & Monitoring

### Cloud Logging

```bash
# Read recent logs
gcloud logging read "resource.type=gce_instance" --project PROJECT_ID --limit 20

# Filter by severity
gcloud logging read "severity>=ERROR" --project PROJECT_ID --limit 20

# Specific resource
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=my-service" \
  --project PROJECT_ID --limit 20
```

### Monitoring Metrics

```bash
# List available metrics
gcloud monitoring metrics list --project PROJECT_ID | head -50

# Describe metric
gcloud monitoring metrics-scopes describe projects/PROJECT_ID
```

---

## Billing & Cost Monitoring

### View Current Costs

```bash
# List billing accounts
gcloud billing accounts list

# Get billing account linked to project
gcloud billing projects describe PROJECT_ID

# View cost breakdown (requires billing export to BigQuery or use console)
# Quick estimate via APIs enabled:
gcloud services list --enabled --project PROJECT_ID
```

### Set Budget Alerts

```bash
# Create budget (via gcloud beta)
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget" \
  --budget-amount=50EUR \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100

# List budgets
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Describe budget
gcloud billing budgets describe BUDGET_ID --billing-account=BILLING_ACCOUNT_ID
```

### Cost-Saving Tips

```bash
# Stop unused VMs (saves $$$)
gcloud compute instances stop INSTANCE_NAME --zone ZONE --project PROJECT_ID

# Schedule auto-start/stop (use Cloud Scheduler + Cloud Functions or cron)

# Check for idle resources
gcloud recommender recommendations list \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.compute.instance.IdleResourceRecommender
```

---

## Secret Manager

### Create & Manage Secrets

```bash
# Enable API
gcloud services enable secretmanager.googleapis.com --project PROJECT_ID

# Create a secret
echo -n "my-secret-value" | gcloud secrets create SECRET_NAME \
  --data-file=- \
  --project PROJECT_ID

# Or from file
gcloud secrets create SECRET_NAME --data-file=./secret.txt --project PROJECT_ID
```

### Access Secrets

```bash
# Get latest version
gcloud secrets versions access latest --secret=SECRET_NAME --project PROJECT_ID

# Get specific version
gcloud secrets versions access 1 --secret=SECRET_NAME --project PROJECT_ID

# List all secrets
gcloud secrets list --project PROJECT_ID

# List versions of a secret
gcloud secrets versions list SECRET_NAME --project PROJECT_ID
```

### Update Secrets

```bash
# Add new version
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=- --project PROJECT_ID

# Disable old version
gcloud secrets versions disable VERSION_ID --secret=SECRET_NAME --project PROJECT_ID

# Delete version (permanent!)
gcloud secrets versions destroy VERSION_ID --secret=SECRET_NAME --project PROJECT_ID
```

### Use in Cloud Run

```bash
# Deploy with secret as env var
gcloud run deploy SERVICE_NAME \
  --image IMAGE \
  --region REGION \
  --project PROJECT_ID \
  --set-secrets="ENV_VAR_NAME=SECRET_NAME:latest"

# Mount as file
gcloud run deploy SERVICE_NAME \
  --image IMAGE \
  --region REGION \
  --project PROJECT_ID \
  --set-secrets="/path/to/secret=SECRET_NAME:latest"
```

---

## Artifact Registry (Container Images)

### Setup

```bash
# Enable API
gcloud services enable artifactregistry.googleapis.com --project PROJECT_ID

# Create Docker repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --project PROJECT_ID \
  --description="Docker images"
```

### Configure Docker Auth

```bash
# Configure Docker to use gcloud credentials
gcloud auth configure-docker REGION-docker.pkg.dev
```

### Build & Push Images

```bash
# Build with Cloud Build (no local Docker needed)
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE:TAG

# Or with local Docker
docker build -t REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE:TAG .
docker push REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE:TAG
```

### List & Manage Images

```bash
# List images
gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME

# List tags for an image
gcloud artifacts docker tags list REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE

# Delete image
gcloud artifacts docker images delete REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE:TAG
```

---

## Cloud SQL (Databases)

### Create Instance

```bash
# Enable API
gcloud services enable sqladmin.googleapis.com --project PROJECT_ID

# Create PostgreSQL instance
gcloud sql instances create INSTANCE_NAME \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=REGION \
  --project PROJECT_ID

# Create MySQL instance
gcloud sql instances create INSTANCE_NAME \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=REGION \
  --project PROJECT_ID
```

### Manage Databases & Users

```bash
# Create database
gcloud sql databases create DB_NAME --instance=INSTANCE_NAME --project PROJECT_ID

# List databases
gcloud sql databases list --instance=INSTANCE_NAME --project PROJECT_ID

# Create user
gcloud sql users create USERNAME \
  --instance=INSTANCE_NAME \
  --password=PASSWORD \
  --project PROJECT_ID

# List users
gcloud sql users list --instance=INSTANCE_NAME --project PROJECT_ID
```

### Connect

```bash
# Connect via Cloud SQL Proxy (recommended)
# First, download proxy: https://cloud.google.com/sql/docs/mysql/sql-proxy

# Direct connection (requires public IP & authorized networks)
gcloud sql connect INSTANCE_NAME --user=USERNAME --project PROJECT_ID

# Get connection info
gcloud sql instances describe INSTANCE_NAME --project PROJECT_ID \
  --format="value(connectionName)"
```

### Backups

```bash
# Create on-demand backup
gcloud sql backups create --instance=INSTANCE_NAME --project PROJECT_ID

# List backups
gcloud sql backups list --instance=INSTANCE_NAME --project PROJECT_ID

# Restore from backup
gcloud sql backups restore BACKUP_ID --restore-instance=INSTANCE_NAME --project PROJECT_ID
```

### Connect from Cloud Run

```bash
# Deploy with Cloud SQL connection
gcloud run deploy SERVICE_NAME \
  --image IMAGE \
  --region REGION \
  --project PROJECT_ID \
  --add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME \
  --set-env-vars="DB_HOST=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
```

---

## Troubleshooting

### "API not enabled"
```bash
# Enable an API
gcloud services enable run.googleapis.com --project PROJECT_ID
gcloud services enable compute.googleapis.com --project PROJECT_ID
```

### "Permission denied"
```bash
# Check IAM roles
gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" \
  --format="table(bindings.role)" --filter="bindings.members:EMAIL"
```

### "Not authenticated"
```bash
gcloud auth login
gcloud auth application-default login  # For ADC (used by libraries)
```

### Refresh credentials
```bash
gcloud auth login --force
```
