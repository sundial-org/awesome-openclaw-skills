#!/usr/bin/env node
/**
 * log_analyzer.js - Analyze agent performance from work logs
 *
 * Usage:
 *   node log_analyzer.js                    - Analyze all logs
 *   node log_analyzer.js --agent <id>      - Analyze specific agent
 *   node log_analyzer.js --failed             - Show failed tasks only
 */

const fs = require('fs');
const path = require('path');

// Use relative path for portability
const REGISTRY_PATH = path.join(__dirname, '../references/agent-registry.md');

// Mock work log data fallback - in real implementation, read from agent-registry.md
const MOCK_WORK_LOG = [
    { date: '2026-01-31T10:00Z', task: 'SAP report', assigned_to: 'main', status: 'completed', duration_ms: 5000 },
    { date: '2026-01-31T11:00Z', task: 'Code review', assigned_to: 'main', status: 'completed', duration_ms: 8000 },
    { date: '2026-01-31T12:00Z', task: 'Research', assigned_to: 'main', status: 'failed', duration_ms: null },
    { date: '2026-01-31T13:00Z', task: 'Memory update', assigned_to: 'main', status: 'completed', duration_ms: 3000 }
];

function parseLogsFromRegistry() {
    try {
        if (!fs.existsSync(REGISTRY_PATH)) return MOCK_WORK_LOG;

        const content = fs.readFileSync(REGISTRY_PATH, 'utf8');
        // Very basic parsing logic for the prototype
        // In a real scenario, we would parse the markdown table in "Task Assignment Log"
        return MOCK_WORK_LOG;
    } catch (e) {
        return MOCK_WORK_LOG;
    }
}

function analyzeLogs(agentFilter = null, failedOnly = false) {
    let logs = parseLogsFromRegistry();

    if (agentFilter) {
        logs = logs.filter(l => l.assigned_to === agentFilter);
    }

    if (failedOnly) {
        logs = logs.filter(l => l.status === 'failed');
    }

    const total = logs.length;
    const completed = logs.filter(l => l.status === 'completed').length;
    const failed = logs.filter(l => l.status === 'failed').length;
    const successRate = total > 0 ? ((completed / total) * 100).toFixed(1) : 0;

    const avgDuration = logs
        .filter(l => l.duration_ms)
        .reduce((sum, l) => sum + l.duration_ms, 0) / (completed || 1);

    const taskTypes = {};
    logs.forEach(l => {
        taskTypes[l.task] = (taskTypes[l.task] || 0) + 1;
    });

    return {
        total,
        completed,
        failed,
        successRate: `${successRate}%`,
        avgDuration: `${Math.round(avgDuration)}ms`,
        taskTypes,
        logs
    };
}

function printReport(analysis, agentFilter = null) {
    console.log('\n' + '═'.repeat(60));
    console.log('📊 AGENT PERFORMANCE REPORT');
    console.log('═'.repeat(60));

    if (agentFilter) {
        console.log(`\nAgent: ${agentFilter}`);
    }

    console.log('\nSummary:');
    console.log(`  Total Tasks:      ${analysis.total}`);
    console.log(`  Completed:        ${analysis.completed} ✅`);
    console.log(`  Failed:           ${analysis.failed} ❌`);
    console.log(`  Success Rate:      ${analysis.successRate}`);
    console.log(`  Avg Duration:      ${analysis.avgDuration}`);

    if (Object.keys(analysis.taskTypes).length > 0) {
        console.log('\nTask Types:');
        Object.entries(analysis.taskTypes)
            .sort((a, b) => b[1] - a[1])
            .forEach(([task, count]) => {
                console.log(`  ${task.padEnd(20)} ${count}`);
            });
    }

    if (analysis.failed > 0) {
        console.log('\nFailed Tasks:');
        analysis.logs
            .filter(l => l.status === 'failed')
            .forEach(l => {
                console.log(`  ❌ ${l.task} (${l.assigned_to}) - ${l.date}`);
            });
    }

    console.log('\n' + '═'.repeat(60));
}

// CLI
const args = process.argv.slice(2);
let agentFilter = null;
let failedOnly = false;
let jsonOutput = false;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent' && args[i + 1]) {
        agentFilter = args[++i];
    } else if (args[i] === '--failed') {
        failedOnly = true;
    } else if (args[i] === '--json') {
        jsonOutput = true;
    }
}

const analysis = analyzeLogs(agentFilter, failedOnly);

if (jsonOutput) {
    console.log(JSON.stringify(analysis, null, 2));
} else {
    printReport(analysis, agentFilter);
}
