#!/usr/bin/env npx tsx
import { x402Client, wrapFetchWithPayment } from '@x402/fetch';
import { registerExactEvmScheme } from '@x402/evm/exact/client';
import { privateKeyToAccount } from 'viem/accounts';

const PRIVATE_KEY = process.env.SKILLZ_PRIVATE_KEY as `0x${string}`;
const API_URL = process.env.SKILLZ_API_URL || 'https://api.skillz.market';

interface Skill {
  slug: string;
  name: string;
  endpoint: string;
  price: string;
  description?: string;
  isActive?: boolean;
}

async function listSkills(verified?: boolean): Promise<Skill[]> {
  const params = new URLSearchParams();
  if (verified) params.set('verified', 'true');
  const query = params.toString();
  const url = `${API_URL}/skills${query ? `?${query}` : ''}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to list skills: ${res.statusText}`);
  }
  return res.json();
}

async function search(query: string) {
  const res = await fetch(`${API_URL}/skills?q=${encodeURIComponent(query)}`);
  if (!res.ok) {
    console.error(`Search failed: ${res.statusText}`);
    process.exit(1);
  }
  const skills = await res.json();
  console.log(JSON.stringify(skills, null, 2));
}

async function info(slug: string) {
  const res = await fetch(`${API_URL}/skills/${slug}`);
  if (!res.ok) {
    console.error(`Skill "${slug}" not found`);
    process.exit(1);
  }
  const skill = await res.json();
  console.log(JSON.stringify(skill, null, 2));
}

async function call(slug: string, input: string) {
  if (!PRIVATE_KEY) {
    console.error('Error: SKILLZ_PRIVATE_KEY not set');
    process.exit(1);
  }

  // Look up skill from API
  const skillRes = await fetch(`${API_URL}/skills/${slug}`);
  if (!skillRes.ok) {
    console.error(`Skill "${slug}" not found`);
    process.exit(1);
  }
  const skill: Skill = await skillRes.json();

  if (skill.isActive === false) {
    console.error(`Skill "${slug}" is not active`);
    process.exit(1);
  }

  console.error(`Calling ${skill.name} @ ${skill.endpoint} ($${skill.price} USDC)`);

  // Set up payment client
  const account = privateKeyToAccount(PRIVATE_KEY);
  const client = new x402Client();
  registerExactEvmScheme(client, { signer: account });
  const paymentFetch = wrapFetchWithPayment(fetch, client);

  try {
    const response = await paymentFetch(skill.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: input,
    });

    if (!response.ok) {
      console.error(`Skill call failed: ${response.statusText}`);
      process.exit(1);
    }

    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

async function direct(url: string, input: string) {
  if (!PRIVATE_KEY) {
    console.error('Error: SKILLZ_PRIVATE_KEY not set');
    process.exit(1);
  }

  console.error(`Calling endpoint: ${url}`);

  // Set up payment client
  const account = privateKeyToAccount(PRIVATE_KEY);
  const client = new x402Client();
  registerExactEvmScheme(client, { signer: account });
  const paymentFetch = wrapFetchWithPayment(fetch, client);

  try {
    const response = await paymentFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: input,
    });

    if (!response.ok) {
      console.error(`Call failed: ${response.statusText}`);
      process.exit(1);
    }

    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// Main dispatch
const command = process.argv[2];
const args = process.argv.slice(3);

switch (command) {
  case 'list':
    const verified = args.includes('--verified');
    listSkills(verified)
      .then((skills) => console.log(JSON.stringify(skills, null, 2)))
      .catch((err) => {
        console.error(err.message);
        process.exit(1);
      });
    break;
  case 'search':
    if (!args[0]) {
      console.error('Usage: search <query>');
      process.exit(1);
    }
    search(args[0]);
    break;
  case 'info':
    if (!args[0]) {
      console.error('Usage: info <slug>');
      process.exit(1);
    }
    info(args[0]);
    break;
  case 'call':
    if (!args[0] || !args[1]) {
      console.error('Usage: call <slug> <json_input>');
      process.exit(1);
    }
    call(args[0], args[1]);
    break;
  case 'direct':
    if (!args[0] || !args[1]) {
      console.error('Usage: direct <url> <json_input>');
      process.exit(1);
    }
    direct(args[0], args[1]);
    break;
  default:
    console.error('Usage: skillz-cli.ts <list|search|info|call|direct> [args]');
    process.exit(1);
}
