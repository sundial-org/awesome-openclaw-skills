/**
 * Unit tests for ResponseFormatter utility
 */

import { ResponseFormatter } from '../client/ResponseFormatter';

describe('ResponseFormatter', () => {
  const mockAccounts = [
    {
      id: '1',
      displayName: 'Chase Checking',
      currentBalance: 5234.56,
      type: { name: 'checking', display: 'Checking' },
      institution: { name: 'Chase' },
      isHidden: false,
      includeInNetWorth: true,
      updatedAt: '2024-01-01T12:00:00Z'
    },
    {
      id: '2',
      displayName: 'Savings Account',
      currentBalance: 15678.90,
      type: { name: 'savings', display: 'Savings' },
      institution: { name: 'Wells Fargo' },
      isHidden: false,
      includeInNetWorth: true,
      updatedAt: '2024-01-01T12:00:00Z'
    },
    {
      id: '3',
      displayName: 'Hidden Account',
      currentBalance: 1000.00,
      type: { name: 'checking', display: 'Checking' },
      institution: { name: 'Bank' },
      isHidden: true,
      includeInNetWorth: false,
      updatedAt: '2024-01-01T12:00:00Z'
    }
  ];

  const mockTransactions = [
    {
      id: '1',
      amount: -45.67,
      date: '2024-01-15',
      merchant: { name: 'Amazon' },
      category: { name: 'Shopping' },
      account: { displayName: 'Chase Checking', mask: '1234' }
    },
    {
      id: '2',
      amount: -12.34,
      date: '2024-01-14',
      merchant: { name: 'Starbucks' },
      category: { name: 'Dining' },
      account: { displayName: 'Chase Checking', mask: '1234' }
    },
    {
      id: '3',
      amount: 1000.00,
      date: '2024-01-13',
      merchant: { name: 'Employer' },
      category: { name: 'Income' },
      account: { displayName: 'Chase Checking', mask: '1234' }
    }
  ];

  describe('Account Formatting', () => {
    test('ultra-light format is very compact', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'ultra-light');

      expect(result).toContain('💰');
      expect(result).toContain('3 accounts');
      expect(result).toContain('$21,913'); // Total balance
      expect(result.length).toBeLessThan(100); // Very compact
    });

    test('light format shows account details', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'light');

      expect(result).toContain('Chase Checking');
      expect(result).toContain('Savings Account');
      expect(result).toContain('$5,234');
      expect(result).toContain('$15,678');
      expect(result).toContain('Total: $21,913');
      expect(result.length).toBeLessThan(500);
    });

    test('standard format returns JSON string', () => {
      const result = ResponseFormatter.formatAccounts(mockAccounts, 'standard');

      expect(typeof result).toBe('string');
      expect(() => JSON.parse(result)).not.toThrow();

      const parsed = JSON.parse(result);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(3);
      expect(parsed[0]).toHaveProperty('displayName', 'Chase Checking');
    });

    test('handles empty accounts array', () => {
      const result = ResponseFormatter.formatAccounts([], 'ultra-light');
      expect(result).toContain('0 accounts');
      expect(result).toContain('$0');
    });

    test('handles accounts with missing data', () => {
      const incompleteAccounts = [
        { id: '1', displayName: 'Test Account' } // Missing balance, type, etc.
      ];

      const result = ResponseFormatter.formatAccounts(incompleteAccounts, 'ultra-light');
      expect(result).toContain('1 accounts');
      expect(result).toContain('$0'); // Should handle missing balance
    });

    test('handles hidden accounts in light format', () => {
      const accountsWithHidden = [
        ...mockAccounts,
        { ...mockAccounts[0], isHidden: true, displayName: 'Hidden Account' }
      ];

      const result = ResponseFormatter.formatAccounts(accountsWithHidden, 'light');
      expect(result).toContain('(hidden)');
    });
  });

  describe('Transaction Formatting', () => {
    test('ultra-light format is very compact', () => {
      const result = ResponseFormatter.formatTransactions(mockTransactions, 'ultra-light');

      expect(result).toContain('💳');
      expect(result).toContain('3 transactions');
      expect(result).toContain('Volume: $1,058'); // Total absolute amounts
      expect(result.length).toBeLessThan(100);
    });

    test('light format shows transaction details', () => {
      const result = ResponseFormatter.formatTransactions(mockTransactions, 'light');

      expect(result).toMatch(/1\/1[3-5]\/2024 - Amazon/);
      expect(result).toMatch(/1\/1[3-5]\/2024 - Starbucks/);
      expect(result).toContain('$45');
      expect(result).toContain('$12');
      expect(result).toContain('Shopping');
      expect(result).toContain('Dining');
    });

    test('standard format returns JSON string', () => {
      const result = ResponseFormatter.formatTransactions(mockTransactions, 'standard');

      expect(typeof result).toBe('string');
      expect(() => JSON.parse(result)).not.toThrow();

      const parsed = JSON.parse(result);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(3);
    });

    test('includes smart query context when provided', () => {
      const query = 'last 3 Amazon charges';
      const result = ResponseFormatter.formatTransactions(mockTransactions, 'light', query);

      expect(result).toContain('🧠 **Smart Query**');
      expect(result).toContain(query);
    });

    test('handles empty transactions array', () => {
      const result = ResponseFormatter.formatTransactions([], 'ultra-light');
      expect(result).toBe('');
    });

    test('handles transactions with missing data', () => {
      const incompleteTransactions = [
        { id: '1', amount: -50 } // Missing merchant, category, etc.
      ];

      const result = ResponseFormatter.formatTransactions(incompleteTransactions, 'light');
      expect(result).toContain('Unknown merchant');
      expect(result).toContain('Uncategorized');
    });
  });

  describe('Quick Stats Formatting', () => {
    test('formats quick stats correctly', () => {
      const accountsForStats = [
        { currentBalance: 1000, includeInNetWorth: true },
        { currentBalance: 500, includeInNetWorth: true },
        { currentBalance: 200, includeInNetWorth: false } // Excluded from net worth
      ];

      const recentTransactions = [
        { amount: -100, date: '2024-01-15' },
        { amount: -50, date: '2024-01-14' },
        { amount: 200, date: '2024-01-13' } // Income
      ];

      const result = ResponseFormatter.formatQuickStats(accountsForStats, recentTransactions);

      expect(result).toContain('💰 $1,500'); // Only accounts included in net worth
      expect(result).toContain('3 accounts'); // Total accounts shown
      expect(result).toMatch(/⬆️|⬇️/); // Should have trend indicator
      expect(result.length).toBeLessThan(150); // Ultra-compact
    });

    test('handles accounts without recent transactions', () => {
      const accountsForStats = [
        { currentBalance: 1000, includeInNetWorth: true },
        { currentBalance: 500, includeInNetWorth: true }
      ];

      const result = ResponseFormatter.formatQuickStats(accountsForStats);

      expect(result).toContain('💰 $1,500');
      expect(result).toContain('2 accounts');
    });
  });

  describe('Spending Summary Formatting', () => {
    const transactionsForSpending = [
      { amount: -150, category: { name: 'Dining' } },
      { amount: -100, category: { name: 'Dining' } },
      { amount: -80, category: { name: 'Gas' } },
      { amount: -70, category: { name: 'Shopping' } },
      { amount: 500, category: { name: 'Income' } } // Should be excluded (income)
    ];

    test('aggregates spending by category correctly', () => {
      const result = ResponseFormatter.formatSpendingSummary(transactionsForSpending, 3);

      expect(result).toContain('🍽️ $250'); // Dining total
      expect(result).toContain('⛽ $80'); // Gas
      expect(result).toContain('🛍️ $70'); // Shopping
      expect(result).toContain('(top 3 this month)');
      expect(result.length).toBeLessThan(100);
    });

    test('handles no expenses', () => {
      const incomeOnly = [
        { amount: 1000, category: { name: 'Salary' } }
      ];

      const result = ResponseFormatter.formatSpendingSummary(incomeOnly, 5);
      expect(result).toBe('💸 No expenses found');
    });

    test('handles uncategorized transactions', () => {
      const uncategorized = [
        { amount: -50, category: null },
        { amount: -30 } // No category property
      ];

      const result = ResponseFormatter.formatSpendingSummary(uncategorized, 5);
      expect(result).toContain('💸 $80'); // Should sum uncategorized
      expect(result).toMatch(/💸 \$80.*\(top \d+ this month\)/);
    });
  });

  describe('Category Icon Mapping', () => {
    test('maps common categories to appropriate icons', () => {
      const testCategories = [
        { category: 'Dining', expected: '🍽️' },
        { category: 'Gas', expected: '⛽' },
        { category: 'Shopping', expected: '🛍️' },
        { category: 'Travel', expected: '✈️' },
        { category: 'Unknown Category', expected: '💸' }
      ];

      testCategories.forEach(({ category, expected }) => {
        const transactions = [{ amount: -100, category: { name: category } }];
        const result = ResponseFormatter.formatSpendingSummary(transactions, 1);
        expect(result).toContain(expected);
      });
    });
  });

  describe('Performance Characteristics', () => {
    test('different verbosity levels produce different response sizes', () => {
      const manyAccounts = Array(10).fill(null).map((_, i) => ({
        id: String(i),
        displayName: `Account ${i}`,
        currentBalance: 1000 + i * 100,
        type: { name: 'checking', display: 'Checking' },
        institution: { name: 'Bank' },
        isHidden: false,
        includeInNetWorth: true,
        updatedAt: '2024-01-01T12:00:00Z'
      }));

      const ultraLight = ResponseFormatter.formatAccounts(manyAccounts, 'ultra-light');
      const light = ResponseFormatter.formatAccounts(manyAccounts, 'light');
      const standard = ResponseFormatter.formatAccounts(manyAccounts, 'standard');

      expect(ultraLight.length).toBeLessThan(light.length);
      expect(light.length).toBeLessThan(standard.length);

      // Ultra-light should be under 100 chars even with many accounts
      expect(ultraLight.length).toBeLessThan(100);
    });

    test('formatters should be fast with large datasets', () => {
      const largeAccountSet = Array(1000).fill(null).map((_, i) => ({
        id: String(i),
        displayName: `Account ${i}`,
        currentBalance: Math.random() * 10000,
        type: { name: 'checking' },
        includeInNetWorth: true
      }));

      const start = Date.now();
      const result = ResponseFormatter.formatAccounts(largeAccountSet, 'ultra-light');
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(100); // Should complete in under 100ms
      expect(result.length).toBeLessThan(200); // Should remain compact even with large dataset
    });
  });
});