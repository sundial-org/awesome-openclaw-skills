const fs = require('fs');
const path = require('path');

const REGISTRY_PATH = path.join(__dirname, '../references/agent-registry.md');

function generateMermaid() {
    // Read registry roughly
    // In real impl, parse 'reports_to' and 'can_assign_to'

    let mermaid = 'graph TD\n';

    // Hardcoded structure for prototype based on current registry
    mermaid += '    User[Ilkerkaan (Human)]\n';
    mermaid += '    Main[Main (Clawdia)]\n';
    mermaid += '    Sub[Sub-Agents (On-Demand)]\n';

    mermaid += '    Main -->|reports_to| User\n';
    mermaid += '    Main -->|can_assign_to| Sub\n';

    return mermaid;
}

const chart = generateMermaid();
console.log(chart);
