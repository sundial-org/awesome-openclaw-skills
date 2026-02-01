/**
 * Authentication E2E Tests
 *
 * Tests authentication flow with Monarch Money API.
 * These tests are READ-ONLY and safe for automated execution.
 */

import { MonarchClient } from '../../lib';

const MONARCH_API_URL = 'https://api.monarch.com';

describe('Authentication', () => {
  let client: MonarchClient;

  beforeEach(() => {
    client = new MonarchClient({
      baseURL: MONARCH_API_URL,
      enablePersistentCache: false
    });
  });

  afterEach(async () => {
    try {
      await client.close();
    } catch {
      // Ignore close errors
    }
  });

  it('should have required environment variables', () => {
    expect(process.env.MONARCH_EMAIL).toBeDefined();
    expect(process.env.MONARCH_PASSWORD).toBeDefined();
    expect(process.env.MONARCH_MFA_SECRET).toBeDefined();
  });

  it('should login with valid credentials', async () => {
    const email = process.env.MONARCH_EMAIL!;
    const password = process.env.MONARCH_PASSWORD!;
    const mfaSecret = process.env.MONARCH_MFA_SECRET;

    await client.login({
      email,
      password,
      mfaSecretKey: mfaSecret,
      useSavedSession: false,
      saveSession: false
    });

    // Verify we can make an API call
    const accounts = await client.accounts.getAll();
    expect(accounts).toBeDefined();
    expect(Array.isArray(accounts)).toBe(true);
  }, 30000);

  it('should load saved session if available', async () => {
    const loaded = client.loadSession();

    if (loaded) {
      // Session exists - verify it works
      const accounts = await client.accounts.getAll();
      expect(accounts).toBeDefined();
    } else {
      // No saved session - this is fine for CI
      console.log('No saved session found (expected in CI)');
    }
  }, 30000);

  it('should handle MFA automatically with secret', async () => {
    const mfaSecret = process.env.MONARCH_MFA_SECRET;

    if (!mfaSecret) {
      console.log('Skipping MFA test - no MFA_SECRET set');
      return;
    }

    const email = process.env.MONARCH_EMAIL!;
    const password = process.env.MONARCH_PASSWORD!;

    // Login should handle MFA automatically
    await client.login({
      email,
      password,
      mfaSecretKey: mfaSecret,
      useSavedSession: false,
      saveSession: false
    });

    // Verify successful auth
    const accounts = await client.accounts.getAll();
    expect(accounts.length).toBeGreaterThan(0);
  }, 30000);
});
