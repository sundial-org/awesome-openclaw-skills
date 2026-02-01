#!/bin/bash
# Initialize Council SQLite Database

DB_PATH="$HOME/.clawdbot/council.db"

# Create database and tables
sqlite3 "$DB_PATH" << SQL
CREATE TABLE IF NOT EXISTS council_members (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    system_message TEXT NOT NULL,
    expertise TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS council_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    member_ids TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    completed_at INTEGER
);

-- Insert default council members
INSERT OR IGNORE INTO council_members (id, name, role, system_message, expertise) VALUES
('architect', 'System Architect', 'Technical Design', 'You are a System Architect. Analyze technical systems, data flow, and infrastructure. Provide clear architectural recommendations.', 'System design, scalability, integration patterns'),
('analyst', 'Technical Analyst', 'Research & Analysis', 'You are a Technical Analyst. Perform deep research, validate concepts, and provide data-driven insights.', 'Research, validation, feasibility analysis'),
('security', 'Security Officer', 'Security & Compliance', 'You are a Security Officer. Identify risks, assess compliance, and recommend security best practices.', 'Security audits, risk assessment, compliance'),
('designer', 'UX Designer', 'User Experience', 'You are a UX Designer. Focus on usability, accessibility, and user-centric design principles.', 'UX/UI design, accessibility, user flows'),
('strategist', 'Business Strategist', 'Strategic Value', 'You are a Business Strategist. Assess ROI, strategic value, and business impact of technical decisions.', 'Strategy, ROI analysis, business value');

SQL

echo "✅ Council database initialized at $DB_PATH"
sqlite3 "$DB_PATH" "SELECT COUNT(*) || ' members registered' FROM council_members"
