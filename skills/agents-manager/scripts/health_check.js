// scripts/health_check.js
// Checks if agents are responsive with detailed status codes

const fs = require('fs');
const path = require('path');

// In a real scenario, this would dynamically list agents.
// For prototype, we check 'main' and any mocked sub-agents.
const AGENTS_TO_CHECK = ['main'];

async function checkHealth(agentId) {
    // Mock health check logic
    // In production: await sessions_send(agentId, "ping")

    // Simulate random latency & status
    const latency = Math.floor(Math.random() * 800);

    let status = 'healthy';
    if (latency > 500) status = 'slow';
    // Simulate 5% chance of offline/error
    if (Math.random() > 0.95) status = 'error';

    return {
        id: agentId,
        status: status,
        latency_ms: latency,
        last_active: new Date().toISOString()
    };
}

function getStatusEmoji(status) {
    switch (status) {
        case 'healthy': return '🟢';
        case 'slow': return '🟡';
        case 'offline': return '🔴';
        case 'error': return '🔴';
        default: return '❓';
    }
}

async function main() {
    console.log('🏥 Agent Health Check');
    console.log('──────────────────────────────────────');
    console.log('Agent                Status     Latency');
    console.log('──────────────────────────────────────');

    for (const agent of AGENTS_TO_CHECK) {
        const result = await checkHealth(agent);
        const emoji = getStatusEmoji(result.status);

        console.log(`${result.id.padEnd(20)} ${emoji} ${result.status.padEnd(8)} ${result.latency_ms}ms`);

        // Auto-recovery hint (simplified)
        if (result.status === 'error' || result.status === 'offline') {
            console.log(`  └─ ⚠️ Action required: Check logs or restart agent.`);
        }
    }
    console.log('──────────────────────────────────────');
}

main();
