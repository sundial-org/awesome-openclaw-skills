#!/usr/bin/env node
/**
 * FieldFix CLI - Query your equipment fleet from the command line
 * 
 * Usage:
 *   fieldfix machines              List all machines
 *   fieldfix machine <id>          Get machine details
 *   fieldfix expenses <id>         Get machine expenses
 *   fieldfix service <id>          Get service history
 *   fieldfix alerts                Get fleet alerts
 *   fieldfix log-service <id>      Log a service entry (Industry)
 *   fieldfix log-expense <id>      Log an expense (Industry)
 *   fieldfix update-hours <id>     Update hour meter (Industry)
 * 
 * Environment:
 *   FIELDFIX_API_KEY - Your FieldFix API key (required)
 */

const BASE_URL = 'https://app.fieldfix.ai/api/v1';

async function request(path, options = {}) {
  const apiKey = process.env.FIELDFIX_API_KEY;
  if (!apiKey) {
    console.error('Error: FIELDFIX_API_KEY environment variable not set');
    console.error('Get your API key at https://app.fieldfix.ai/settings/api');
    process.exit(1);
  }

  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await response.json();
  
  if (!response.ok) {
    console.error(`Error: ${data.error?.message || response.statusText}`);
    process.exit(1);
  }

  return data;
}

async function main() {
  const [,, command, ...args] = process.argv;

  if (!command) {
    console.log(`
FieldFix CLI - Query your equipment fleet

Commands:
  machines              List all machines
  machine <id>          Get machine details  
  expenses <id>         Get machine expenses
  service <id>          Get service history
  alerts                Get fleet alerts

Write commands (Industry plan):
  log-service <id> <type> <cost> [notes]
  log-expense <id> <category> <amount> [description]
  update-hours <id> <hours>

Environment:
  FIELDFIX_API_KEY      Your API key (required)
`);
    process.exit(0);
  }

  let result;

  switch (command) {
    case 'machines':
      result = await request('/machines');
      break;

    case 'machine':
      if (!args[0]) {
        console.error('Usage: fieldfix machine <id>');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}`);
      break;

    case 'expenses':
      if (!args[0]) {
        console.error('Usage: fieldfix expenses <machine-id>');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}/expenses`);
      break;

    case 'service':
      if (!args[0]) {
        console.error('Usage: fieldfix service <machine-id>');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}/service`);
      break;

    case 'alerts':
      result = await request('/alerts');
      break;

    case 'log-service':
      if (args.length < 3) {
        console.error('Usage: fieldfix log-service <machine-id> <type> <cost> [notes]');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}/service`, {
        method: 'POST',
        body: JSON.stringify({
          type: args[1],
          cost: parseFloat(args[2]),
          notes: args.slice(3).join(' ') || undefined,
        }),
      });
      break;

    case 'log-expense':
      if (args.length < 3) {
        console.error('Usage: fieldfix log-expense <machine-id> <category> <amount> [description]');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}/expenses`, {
        method: 'POST',
        body: JSON.stringify({
          category: args[1],
          amount: parseFloat(args[2]),
          description: args.slice(3).join(' ') || undefined,
        }),
      });
      break;

    case 'update-hours':
      if (args.length < 2) {
        console.error('Usage: fieldfix update-hours <machine-id> <hours>');
        process.exit(1);
      }
      result = await request(`/machines/${args[0]}/hours`, {
        method: 'POST',
        body: JSON.stringify({
          hours: parseFloat(args[1]),
        }),
      });
      break;

    default:
      console.error(`Unknown command: ${command}`);
      console.error('Run "fieldfix" for usage');
      process.exit(1);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
