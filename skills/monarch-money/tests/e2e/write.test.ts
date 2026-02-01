/**
 * Write Operations E2E Tests
 *
 * Tests write operations against Monarch Money API.
 * These tests REQUIRE --allow-writes flag and are MANUAL ONLY.
 *
 * WARNING: These tests create/modify real data in the Monarch Money account.
 * Only run manually with explicit confirmation.
 */

import { MonarchClient } from '../../lib';

const MONARCH_API_URL = 'https://api.monarch.com';
const ALLOW_WRITES = process.env.ALLOW_WRITE_TESTS === '1';

describe('Write Operations (Manual Only)', () => {
  let client: MonarchClient;

  beforeAll(async () => {
    if (!ALLOW_WRITES) {
      console.log('='.repeat(60));
      console.log('SKIPPING WRITE TESTS');
      console.log('Set ALLOW_WRITE_TESTS=1 to enable');
      console.log('WARNING: These tests modify real data!');
      console.log('='.repeat(60));
      return;
    }

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
    if (client) {
      try {
        await client.close();
      } catch {
        // Ignore close errors
      }
    }
  });

  describe('Transaction Updates', () => {
    it('should update transaction notes', async () => {
      if (!ALLOW_WRITES) {
        console.log('Skipping write test - ALLOW_WRITE_TESTS not set');
        return;
      }

      // Get a recent transaction to update
      const result = await client.transactions.getTransactions({
        limit: 1
      });

      if (result.transactions.length === 0) {
        console.log('No transactions to test with');
        return;
      }

      const tx = result.transactions[0];
      const originalNotes = tx.notes || '';
      const testNotes = `E2E Test - ${new Date().toISOString()}`;

      // Update notes
      await client.transactions.updateTransaction(tx.id, {
        notes: testNotes
      });

      // Restore original notes
      await client.transactions.updateTransaction(tx.id, {
        notes: originalNotes
      });

      console.log(`Successfully updated and restored transaction ${tx.id}`);
    }, 60000);
  });

  describe('Category Updates', () => {
    it('should update transaction category', async () => {
      if (!ALLOW_WRITES) {
        console.log('Skipping write test - ALLOW_WRITE_TESTS not set');
        return;
      }

      // Get a transaction and categories
      const [txResult, categories] = await Promise.all([
        client.transactions.getTransactions({ limit: 1 }),
        client.categories.getCategories()
      ]);

      if (txResult.transactions.length === 0) {
        console.log('No transactions to test with');
        return;
      }

      if (categories.length < 2) {
        console.log('Not enough categories to test with');
        return;
      }

      const tx = txResult.transactions[0];
      const originalCategoryId = tx.category?.id;

      // Find a different category
      const newCategory = categories.find((c) => c.id !== originalCategoryId);

      if (!newCategory) {
        console.log('Could not find alternate category');
        return;
      }

      // Update category
      await client.transactions.updateTransaction(tx.id, {
        categoryId: newCategory.id
      });

      // Restore original category
      if (originalCategoryId) {
        await client.transactions.updateTransaction(tx.id, {
          categoryId: originalCategoryId
        });
      }

      console.log(`Successfully updated and restored category for ${tx.id}`);
    }, 60000);
  });
});
