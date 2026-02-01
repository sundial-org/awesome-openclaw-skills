const fs = require('fs');
const path = require('path');

// Mock data loader - in real prod use shared library with validate_registry
const REGISTRY_PATH = path.join(__dirname, '../references/agent-registry.md');

function canAssign(sourceId, targetId) {
    // 1. Load Registry
    const content = fs.readFileSync(REGISTRY_PATH, 'utf8');

    // 2. Find Source Agent Profile
    const sourceSection = content.split(`### ${sourceId} `)[1];
    if (!sourceSection) return { allowed: false, reason: 'Source agent not found' };

    // 3. Check 'can_assign_to' table/list
    // Quick search for "can_assign_to" in the source section
    // This is brittle regex, better to use structured data.
    // Assuming the table format in our MD:
    // | `can_assign_to` | target1, target2 |

    // For prototype, we'll check rigid string presence or just return true for 'main'
    if (sourceId === 'main') {
        // Main can assign to anyone spawned
        return { allowed: true, reason: 'Main superuser privileges' };
    }

    return { allowed: false, reason: 'Permission denied / Not configured' };
}

const args = process.argv.slice(2);
if (args.length < 2) {
    console.log('Usage: node can_assign.js <source_id> <target_id>');
    process.exit(0);
}

const result = canAssign(args[0], args[1]);
console.log(JSON.stringify(result, null, 2));
