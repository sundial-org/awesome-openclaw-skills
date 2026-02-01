#!/bin/bash
# Setup a Neon database for an org with standard schema
# Usage: ./setup-org-db.sh <org-name>

set -e

ORG_NAME="${1:-my-org}"
PROJECT_NAME="${ORG_NAME}-db"

echo "🐘 Creating Neon project: $PROJECT_NAME"

# Create project and capture output
PROJECT_JSON=$(neonctl projects create --name "$PROJECT_NAME" -o json)
PROJECT_ID=$(echo "$PROJECT_JSON" | jq -r '.project.id')

echo "✅ Project created: $PROJECT_ID"

# Get connection string
CONN_STRING=$(neonctl connection-string --project-id "$PROJECT_ID" --pooled)

echo "📊 Setting up standard tables..."

# Create standard org tables
psql "$CONN_STRING" <<EOF
-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    location VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    status VARCHAR(50) DEFAULT 'identified',
    priority VARCHAR(20) DEFAULT 'medium',
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    assigned_to VARCHAR(100),
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_date DATE DEFAULT CURRENT_DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Activity log
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(category);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_metrics_name_date ON metrics(metric_name, metric_date);
CREATE INDEX IF NOT EXISTS idx_activity_entity ON activity_log(entity_type, entity_id);

EOF

echo "✅ Database setup complete!"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Connection: $CONN_STRING"
echo ""
echo "Save these to your org config!"
