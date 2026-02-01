/**
 * Unit tests for optimized GraphQL operations
 */

import {
  GET_ACCOUNTS_ULTRA_LIGHT,
  GET_ACCOUNTS_LIGHT,
  GET_ACCOUNTS,
  GET_TRANSACTIONS_ULTRA_LIGHT,
  GET_TRANSACTIONS_LIGHT,
  GET_TRANSACTIONS,
  GET_QUICK_FINANCIAL_OVERVIEW,
  SMART_TRANSACTION_SEARCH,
  getQueryForVerbosity,
  type VerbosityLevel
} from '../client/graphql/operations';

describe('GraphQL Operations', () => {
  describe('Query Structure Validation', () => {
    test('ultra-light accounts query has minimal fields', () => {
      expect(GET_ACCOUNTS_ULTRA_LIGHT).toContain('id');
      expect(GET_ACCOUNTS_ULTRA_LIGHT).toContain('displayName');
      expect(GET_ACCOUNTS_ULTRA_LIGHT).toContain('currentBalance');
      expect(GET_ACCOUNTS_ULTRA_LIGHT).toContain('type');

      // Should NOT contain verbose fields
      expect(GET_ACCOUNTS_ULTRA_LIGHT).not.toContain('credential');
      expect(GET_ACCOUNTS_ULTRA_LIGHT).not.toContain('syncDisabled');
      expect(GET_ACCOUNTS_ULTRA_LIGHT).not.toContain('institution');
    });

    test('light accounts query has moderate fields', () => {
      expect(GET_ACCOUNTS_LIGHT).toContain('id');
      expect(GET_ACCOUNTS_LIGHT).toContain('displayName');
      expect(GET_ACCOUNTS_LIGHT).toContain('currentBalance');
      expect(GET_ACCOUNTS_LIGHT).toContain('institution');
      expect(GET_ACCOUNTS_LIGHT).toContain('updatedAt');

      // Should NOT contain the most verbose fields
      expect(GET_ACCOUNTS_LIGHT).not.toContain('credential');
      expect(GET_ACCOUNTS_LIGHT).not.toContain('syncDisabled');
      expect(GET_ACCOUNTS_LIGHT).not.toContain('transactionsCount');
    });

    test('standard accounts query has all fields', () => {
      expect(GET_ACCOUNTS).toContain('id');
      expect(GET_ACCOUNTS).toContain('displayName');
      expect(GET_ACCOUNTS).toContain('currentBalance');
      expect(GET_ACCOUNTS).toContain('credential');
      expect(GET_ACCOUNTS).toContain('syncDisabled');
      expect(GET_ACCOUNTS).toContain('institution');
      expect(GET_ACCOUNTS).toContain('transactionsCount');
    });

    test('ultra-light transactions query has minimal fields', () => {
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).toContain('id');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).toContain('amount');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).toContain('date');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).toContain('merchant');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).toContain('account');

      // Should NOT contain verbose fields
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).not.toContain('attachments');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).not.toContain('tags');
      expect(GET_TRANSACTIONS_ULTRA_LIGHT).not.toContain('reviewStatus');
    });

    test('smart transaction search has proper variables', () => {
      expect(SMART_TRANSACTION_SEARCH).toContain('$search: String');
      expect(SMART_TRANSACTION_SEARCH).toContain('$limit: Int');
      expect(SMART_TRANSACTION_SEARCH).toContain('$minAmount: Float');
      expect(SMART_TRANSACTION_SEARCH).toContain('$maxAmount: Float');
      expect(SMART_TRANSACTION_SEARCH).toContain('$accountIds: [ID!]');
      expect(SMART_TRANSACTION_SEARCH).toContain('$categoryIds: [ID!]');
    });
  });

  describe('Query Selector Utility', () => {
    test('getQueryForVerbosity returns correct queries for accounts', () => {
      expect(getQueryForVerbosity('accounts', 'ultra-light')).toBe(GET_ACCOUNTS_ULTRA_LIGHT);
      expect(getQueryForVerbosity('accounts', 'light')).toBe(GET_ACCOUNTS_LIGHT);
      expect(getQueryForVerbosity('accounts', 'standard')).toBe(GET_ACCOUNTS);
    });

    test('getQueryForVerbosity returns correct queries for transactions', () => {
      expect(getQueryForVerbosity('transactions', 'ultra-light')).toBe(GET_TRANSACTIONS_ULTRA_LIGHT);
      expect(getQueryForVerbosity('transactions', 'light')).toBe(GET_TRANSACTIONS_LIGHT);
      expect(getQueryForVerbosity('transactions', 'standard')).toBe(GET_TRANSACTIONS);
    });

    test('getQueryForVerbosity throws for unknown query type', () => {
      expect(() => getQueryForVerbosity('unknown' as any, 'standard')).toThrow('Unknown query type: unknown');
    });
  });

  describe('Query Syntax Validation', () => {
    const queries = [
      GET_ACCOUNTS_ULTRA_LIGHT,
      GET_ACCOUNTS_LIGHT,
      GET_ACCOUNTS,
      GET_TRANSACTIONS_ULTRA_LIGHT,
      GET_TRANSACTIONS_LIGHT,
      GET_TRANSACTIONS,
      GET_QUICK_FINANCIAL_OVERVIEW,
      SMART_TRANSACTION_SEARCH
    ];

    test('all queries have valid GraphQL syntax', () => {
      queries.forEach(query => {
        // Basic GraphQL syntax validation
        expect(query).toContain('query ');
        expect(query).toContain('{');
        expect(query).toContain('}');

        // Should not have syntax errors
        expect(query).not.toContain('{{');
        expect(query).not.toContain('}}');

        // Should have balanced braces
        const openBraces = (query.match(/\{/g) || []).length;
        const closeBraces = (query.match(/\}/g) || []).length;
        expect(openBraces).toBe(closeBraces);
      });
    });
  });

  describe('Performance Characteristics', () => {
    test('ultra-light queries are significantly shorter than standard', () => {
      expect(GET_ACCOUNTS_ULTRA_LIGHT.length).toBeLessThan(GET_ACCOUNTS.length * 0.5);
      expect(GET_TRANSACTIONS_ULTRA_LIGHT.length).toBeLessThan(GET_TRANSACTIONS.length * 0.5);
    });

    test('light queries are shorter than standard but longer than ultra-light', () => {
      expect(GET_ACCOUNTS_LIGHT.length).toBeLessThan(GET_ACCOUNTS.length);
      expect(GET_ACCOUNTS_LIGHT.length).toBeGreaterThan(GET_ACCOUNTS_ULTRA_LIGHT.length);

      expect(GET_TRANSACTIONS_LIGHT.length).toBeLessThan(GET_TRANSACTIONS.length);
      expect(GET_TRANSACTIONS_LIGHT.length).toBeGreaterThan(GET_TRANSACTIONS_ULTRA_LIGHT.length);
    });
  });
});

describe('VerbosityLevel Type', () => {
  test('accepts valid verbosity levels', () => {
    const validLevels: VerbosityLevel[] = ['ultra-light', 'light', 'standard'];

    validLevels.forEach(level => {
      expect(typeof level).toBe('string');
      expect(['ultra-light', 'light', 'standard']).toContain(level);
    });
  });
});