# assets/dotenv-template.example
# Copy to .env (do not commit). Replace values via secret manager or deploy-time injection.

ENVIRONMENT=dev
APP_NAME=

# n8n
N8N_ENCRYPTION_KEY=
N8N_BASIC_AUTH_ACTIVE=false

# Google OAuth (example)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=

# Logging/Audit
AUDIT_LOG_SINK=sheet|db|file
