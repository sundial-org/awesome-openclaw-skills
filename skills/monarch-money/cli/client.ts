import { MonarchClient } from '../lib';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// Use the same session directory as monarchmoney library
const SESSION_DIR = join(homedir(), '.mm');
const CLI_CONFIG_FILE = join(SESSION_DIR, 'cli-config.json');

// The correct API base URL (not the default api.monarchmoney.com)
const MONARCH_API_URL = 'https://api.monarch.com';

export interface CliConfig {
  email?: string;
}

function ensureSessionDir(): void {
  if (!existsSync(SESSION_DIR)) {
    mkdirSync(SESSION_DIR, { recursive: true, mode: 0o700 });
  }
}

export function saveCliConfig(config: CliConfig): void {
  ensureSessionDir();
  writeFileSync(CLI_CONFIG_FILE, JSON.stringify(config, null, 2), { mode: 0o600 });
}

export function loadCliConfig(): CliConfig | null {
  if (!existsSync(CLI_CONFIG_FILE)) {
    return null;
  }
  try {
    return JSON.parse(readFileSync(CLI_CONFIG_FILE, 'utf-8'));
  } catch {
    return null;
  }
}

export function clearCliConfig(): void {
  if (existsSync(CLI_CONFIG_FILE)) {
    writeFileSync(CLI_CONFIG_FILE, '{}');
  }
}

export async function getClient(): Promise<MonarchClient> {
  const client = new MonarchClient({ baseURL: MONARCH_API_URL, enablePersistentCache: false });

  // Load saved session from ~/.mm/session.json
  const loaded = client.loadSession();
  if (!loaded) {
    throw new Error('Not logged in. Run: monarch auth login');
  }
  
  return client;
}

export async function loginWithCredentials(email: string, password: string, mfaSecret?: string): Promise<MonarchClient> {
  const client = new MonarchClient({ baseURL: MONARCH_API_URL, enablePersistentCache: false });

  await client.login({ email, password, mfaSecretKey: mfaSecret, useSavedSession: true, saveSession: true });
  
  // Save the email for status display
  saveCliConfig({ email });

  return client;
}
