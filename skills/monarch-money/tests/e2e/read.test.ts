/**
 * Read Operations E2E Tests
 *
 * Tests read-only operations against Monarch Money API.
 * These tests are READ-ONLY and safe for automated execution.
 */

import { MonarchClient } from '../../lib';

const MONARCH_API_URL = 'https://api.monarch.com';

describe('Read Operations', () => {
  let client: MonarchClient;

  beforeAll(async () => {
    client = new MonarchClient({
      baseURL: MONARCH_API_URL,
      enablePersistentCache: false
    });

    await client.login({
      email: process.env.MONARCH_EMAIL!,
      password: process.env.MONARCH_PASSWORD!,
      mfaSecretKey: process.env.MONARCH_MFA_SECRET,
      useSavedSession: true,
      saveSession: true
    });
  }, 30000);

  afterAll(async () => {
    try {
      await client.close();
    } catch {
      // Ignore close errors
    }
  });

  describe('Transactions', () => {
    it('should list transactions', async () => {
      const result = await client.transactions.getTransactions({
        limit: 5
      });

      expect(result).toBeDefined();
      expect(result.transactions).toBeDefined();
      expect(Array.isArray(result.transactions)).toBe(true);
    }, 30000);

    it('should list transactions with date filter', async () => {
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const result = await client.transactions.getTransactions({
        limit: 10,
        startDate,
        endDate
      });

      expect(result.transactions).toBeDefined();
      // All transactions should be within date range
      for (const tx of result.transactions) {
        expect(new Date(tx.date).getTime()).toBeGreaterThanOrEqual(
          new Date(startDate).getTime()
        );
        expect(new Date(tx.date).getTime()).toBeLessThanOrEqual(
          new Date(endDate).getTime() + 24 * 60 * 60 * 1000
        );
      }
    }, 30000);

    it('should handle transaction with verbosity levels', async () => {
      const ultraLight = await client.transactions.getTransactions({
        limit: 3,
        verbosity: 'ultra-light'
      });

      const light = await client.transactions.getTransactions({
        limit: 3,
        verbosity: 'light'
      });

      expect(ultraLight.transactions).toBeDefined();
      expect(light.transactions).toBeDefined();
    }, 30000);
  });

  describe('Categories', () => {
    it('should list categories', async () => {
      const categories = await client.categories.getCategories();

      expect(categories).toBeDefined();
      expect(Array.isArray(categories)).toBe(true);
      expect(categories.length).toBeGreaterThan(0);
    }, 30000);

    it('should have expected category properties', async () => {
      const categories = await client.categories.getCategories();

      const category = categories[0];
      expect(category).toHaveProperty('id');
      expect(category).toHaveProperty('name');
    }, 30000);
  });

  describe('Accounts', () => {
    it('should list accounts', async () => {
      const accounts = await client.accounts.getAll();

      expect(accounts).toBeDefined();
      expect(Array.isArray(accounts)).toBe(true);
      expect(accounts.length).toBeGreaterThan(0);
    }, 30000);

    it('should have expected account properties', async () => {
      const accounts = await client.accounts.getAll();

      const account = accounts[0];
      expect(account).toHaveProperty('id');
      expect(account).toHaveProperty('displayName');
    }, 30000);

    it('should support verbosity levels', async () => {
      const ultraLight = await client.accounts.getAll({
        verbosity: 'ultra-light'
      });

      const light = await client.accounts.getAll({
        verbosity: 'light'
      });

      expect(ultraLight).toBeDefined();
      expect(light).toBeDefined();
    }, 30000);
  });
});
