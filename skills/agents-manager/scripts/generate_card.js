const fs = require('fs');
const path = require('path');

// Mock data loader
const REGISTRY_PATH = path.join(__dirname, '../references/agent-registry.md');

function generateCard(agentId) {
    const content = fs.readFileSync(REGISTRY_PATH, 'utf8');

    // Find agent section
    const sectionStart = content.split(`### ${agentId} `)[1];
    if (!sectionStart) {
        console.error(`Agent ${agentId} not found`);
        process.exit(1);
    }

    // Parse minimal details for card
    // In real implementation, this would parse the 'agent_card' YAML block
    // For now, we construct a mock card based on available info

    const card = {
        id: agentId,
        name: agentId === 'main' ? 'Clawdia' : agentId,
        type: 'agent',
        capabilities: ['general', 'Orchestration'], // Placeholder
        routing: {
            reports_to: 'Ilkerkaan',
            can_assign_to: ['sub-agents']
        },
        generated_at: new Date().toISOString()
    };

    return card;
}

const args = process.argv.slice(2);
if (args.length === 0) {
    console.log('Usage: node generate_card.js <agent_id>');
    process.exit(0);
}

const card = generateCard(args[0]);
console.log(JSON.stringify(card, null, 2));
