const fs = require('fs');
const path = require('path');
const readline = require('readline');

const REGISTRY_PATH = path.join(__dirname, '../references/agent-registry.md');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const config = {
    id: 'new-agent',
    name: '',
    role: '',
    reports_to: ''
};

console.log('🧙 Agents Manager Setup Wizard');
console.log('──────────────────────────────────────');
console.log('This wizard will help you register a new agent or configure the system.\n');

function askQuestion(query) {
    return new Promise(resolve => rl.question(query, resolve));
}

async function main() {
    config.id = await askQuestion('1. Enter Agent ID (e.g., coder, research): ');
    config.name = await askQuestion('2. Enter Display Name (e.g., Code Master): ');
    config.role = await askQuestion('3. Primary Capability (e.g., Python coding): ');
    config.reports_to = await askQuestion('4. Who does this agent report to? (default: main): ') || 'main';

    console.log('\nCONFIRMATION:');
    console.log(`ID: ${config.id}`);
    console.log(`Name: ${config.name}`);
    console.log(`Role: ${config.role}`);
    console.log(`Reports To: ${config.reports_to}`);

    const confirm = await askQuestion('\nSave this agent? (y/n): ');

    if (confirm.toLowerCase() === 'y') {
        appendAgentToRegistry(config);
        console.log(`\n✅ Agent '${config.id}' registered successfully!`);
        console.log('Run `node scripts/scan_agents.js` to see it.');
    } else {
        console.log('\n❌ Setup cancelled.');
    }

    rl.close();
}

function appendAgentToRegistry(agent) {
    if (!fs.existsSync(REGISTRY_PATH)) {
        console.error('Error: Registry file not found!');
        return;
    }

    let content = fs.readFileSync(REGISTRY_PATH, 'utf8');
    const timestamp = new Date().toISOString().split('T')[0];

    // Append to table (tricky with regex, simpler to just append detailed profile for now)
    // In a robust app, we'd use a Markdown parser.
    // Here we append a simplified profile.

    const newProfile = `\n### ${agent.id} (${agent.name})

**Model:** (auto-detect)
**Capabilities:**
- ${agent.role}

**Routing Configuration:**
| Field | Value |
|-------|-------|
| \`reports_to\` | ${agent.reports_to} |
| \`can_assign_to\` | (none) |

**Health Status:** 🟢 New
*Last updated: ${timestamp}*
\n`;

    fs.appendFileSync(REGISTRY_PATH, newProfile);
}

main();
