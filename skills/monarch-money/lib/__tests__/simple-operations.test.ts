/**
 * Simple unit tests for operations and ResponseFormatter
 */

import {
  GET_ACCOUNTS_ULTRA_LIGHT,
  GET_ACCOUNTS_LIGHT,
  GET_ACCOUNTS,
  getQueryForVerbosity
} from '../client/graphql/operations';
import { ResponseFormatter } from '../client/ResponseFormatter';

describe('Operations and ResponseFormatter', () => {
  describe('Query Selection', () => {
    test('getQueryForVerbosity works for accounts', () => {
      expect(getQueryForVerbosity('accounts', 'ultra-light')).toBe(GET_ACCOUNTS_ULTRA_LIGHT);
      expect(getQueryForVerbosity('accounts', 'light')).toBe(GET_ACCOUNTS_LIGHT);
      expect(getQueryForVerbosity('accounts', 'standard')).toBe(GET_ACCOUNTS);
    });

    test('queries have expected content', () => {
      expect(GET_ACCOUNTS_ULTRA_LIGHT).toContain('displayName');
      expect(GET_ACCOUNTS_LIGHT).toContain('institution');
      expect(GET_ACCOUNTS).toContain('credential');
    });
  });

  describe('ResponseFormatter', () => {
    const mockAccounts = [
      {
        id: '1',
        displayName: 'Test Account',
        currentBalance: 1000,
        type: { name: 'checking' },
        includeInNetWorth: true
      }
    ];

    test('formatAccounts ultra-light is compact', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'ultra-light');
      expect(result).toContain('💰');
      expect(result).toContain('1 accounts');
      expect(result.length).toBeLessThan(100);
    });

    test('formatAccounts light shows details', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'light');
      expect(result).toContain('Test Account');
      expect(result).toContain('$1,000');
    });

    test('formatAccounts standard returns JSON', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'standard');
      expect(() => JSON.parse(result)).not.toThrow();
    });
  });
});