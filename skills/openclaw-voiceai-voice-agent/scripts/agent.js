#!/usr/bin/env node
/**
 * Voice.ai Agents CLI
 * 
 * Command-line interface for managing Voice.ai conversational AI agents.
 * 
 * Usage:
 *   node agent.js <command> [options]
 * 
 * Commands:
 *   create   - Create a new agent
 *   list     - List all agents
 *   get      - Get agent details
 *   update   - Update an agent
 *   deploy   - Deploy an agent
 *   pause    - Pause an agent
 *   delete   - Delete an agent
 * 
 * @author Nick Gill (https://github.com/gizmoGremlin)
 */

const VoiceAIAgents = require('../voice-ai-agents-sdk');
const fs = require('fs');

// Parse command line arguments
function parseArgs(args) {
  const result = { _: [] };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        result[key] = next;
        i++;
      } else {
        result[key] = true;
      }
    } else {
      result._.push(args[i]);
    }
  }
  return result;
}

// Print help
function printHelp() {
  console.log(`
Voice.ai Agents CLI

Usage: node agent.js <command> [options]

Commands:
  create    Create a new agent
  list      List all agents
  get       Get agent details
  update    Update an agent
  deploy    Deploy an agent for calls
  pause     Pause an agent
  delete    Delete an agent

Options:
  --id <agent_id>       Agent ID (for get/update/deploy/pause/delete)
  --name <name>         Agent name (for create/update)
  --prompt <text>       System prompt (for create/update)
  --greeting <text>     Initial greeting (for create/update)
  --voice-id <id>       Voice ID for TTS
  --language <code>     Language code (en, es, fr, etc.)
  --kb-id <id>          Knowledge base ID
  --help                Show this help

Environment:
  VOICE_AI_API_KEY      Your Voice.ai API key (required)

Examples:
  # Create a new agent
  node agent.js create --name "Support Bot" --prompt "You help customers"

  # List all agents
  node agent.js list

  # Deploy an agent
  node agent.js deploy --id abc123

  # Update an agent's prompt
  node agent.js update --id abc123 --prompt "New system prompt"
`);
}

// Main CLI function
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  if (args.help || !command) {
    printHelp();
    process.exit(command ? 0 : 1);
  }

  // Check for API key
  const apiKey = process.env.VOICE_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: VOICE_AI_API_KEY environment variable is required');
    console.error('Get your API key at: https://voice.ai/app/dashboard/developers');
    process.exit(1);
  }

  const client = new VoiceAIAgents(apiKey);

  try {
    switch (command) {
      case 'create': {
        if (!args.name) {
          console.error('Error: --name is required for create');
          process.exit(1);
        }
        
        const config = VoiceAIAgents.createConfig({
          prompt: args.prompt || 'You are a helpful assistant.',
          greeting: args.greeting || 'Hello! How can I help you today?',
          voice_id: args['voice-id'],
          language: args.language || 'en'
        });

        const agent = await client.createAgent({
          name: args.name,
          config: config,
          kb_id: args['kb-id'] ? parseInt(args['kb-id']) : undefined
        });

        console.log('✅ Agent created successfully!\n');
        console.log(`ID:     ${agent.agent_id}`);
        console.log(`Name:   ${agent.name}`);
        console.log(`Status: ${agent.status}`);
        break;
      }

      case 'list': {
        const agents = await client.listAgents();
        
        if (!agents || agents.length === 0) {
          console.log('No agents found.');
          break;
        }

        console.log('Your agents:\n');
        console.log('ID                                    Name                 Status');
        console.log('─'.repeat(70));
        
        for (const agent of agents) {
          const id = agent.agent_id.padEnd(36);
          const name = (agent.name || 'Unnamed').slice(0, 20).padEnd(20);
          const status = agent.status || 'unknown';
          console.log(`${id}  ${name} ${status}`);
        }
        break;
      }

      case 'get': {
        if (!args.id) {
          console.error('Error: --id is required');
          process.exit(1);
        }

        const agent = await client.getAgent(args.id);
        console.log(JSON.stringify(agent, null, 2));
        break;
      }

      case 'update': {
        if (!args.id) {
          console.error('Error: --id is required');
          process.exit(1);
        }

        const updates = {};
        if (args.name) updates.name = args.name;
        if (args.prompt || args.greeting || args['voice-id'] || args.language) {
          updates.config = {};
          if (args.prompt) updates.config.prompt = args.prompt;
          if (args.greeting) updates.config.greeting = args.greeting;
          if (args['voice-id'] || args.language) {
            updates.config.tts_params = {};
            if (args['voice-id']) updates.config.tts_params.voice_id = args['voice-id'];
            if (args.language) updates.config.tts_params.language = args.language;
          }
        }

        const agent = await client.updateAgent(args.id, updates);
        console.log('✅ Agent updated successfully!');
        console.log(`Name:   ${agent.name}`);
        console.log(`Status: ${agent.status}`);
        break;
      }

      case 'deploy': {
        if (!args.id) {
          console.error('Error: --id is required');
          process.exit(1);
        }

        const result = await client.deployAgent(args.id);
        console.log('🚀 Agent deployed successfully!\n');
        console.log(`Message: ${result.message}`);
        if (result.sip_status) {
          console.log(`SIP Status: ${result.sip_status}`);
        }
        break;
      }

      case 'pause': {
        if (!args.id) {
          console.error('Error: --id is required');
          process.exit(1);
        }

        const agent = await client.pauseAgent(args.id);
        console.log('⏸️  Agent paused successfully!');
        console.log(`Status: ${agent.status}`);
        break;
      }

      case 'delete': {
        if (!args.id) {
          console.error('Error: --id is required');
          process.exit(1);
        }

        await client.deleteAgent(args.id);
        console.log('🗑️  Agent deleted successfully!');
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        printHelp();
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    if (error.details) {
      console.error('Details:', JSON.stringify(error.details, null, 2));
    }
    process.exit(1);
  }
}

main();
