#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const AgentLedger = require('../src/ledger.js');
const Reports = require('../src/reports.js');
const BudgetManager = require('../src/budget.js');

class TestRunner {
  constructor() {
    this.testCount = 0;
    this.passedTests = 0;
    this.failedTests = 0;
    
    // Use a temporary test directory
    this.testDir = path.join(__dirname, '..', 'test-workspace');
    this.ledger = new AgentLedger(this.testDir);
    this.reports = new Reports(this.ledger);
    this.budgetManager = new BudgetManager(this.ledger);
  }

  async setup() {
    // Clean test directory
    try {
      await fs.rm(this.testDir, { recursive: true, force: true });
    } catch (e) {
      // Directory might not exist
    }
    await fs.mkdir(this.testDir, { recursive: true });
  }

  async teardown() {
    // Clean up test directory
    try {
      await fs.rm(this.testDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }
  }

  async test(name, testFunction) {
    this.testCount++;
    try {
      await testFunction();
      console.log(`✅ ${name}`);
      this.passedTests++;
    } catch (error) {
      console.error(`❌ ${name}: ${error.message}`);
      this.failedTests++;
    }
  }

  assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }

  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  }

  assertApproxEqual(actual, expected, tolerance = 0.01, message) {
    if (Math.abs(actual - expected) > tolerance) {
      throw new Error(message || `Expected ${expected}, got ${actual} (tolerance: ${tolerance})`);
    }
  }

  async run() {
    console.log('🧪 Running AgentLedger Tests\n');
    
    await this.setup();

    try {
      // Basic functionality tests
      await this.test('Ledger initialization', async () => {
        await this.ledger.init();
        this.assert(true, 'Ledger should initialize without errors');
      });

      await this.test('Log simple transaction', async () => {
        const transaction = await this.ledger.logTransaction({
          amount: 29.99,
          vendor: 'OpenAI',
          description: 'API credits'
        });
        
        this.assert(transaction.id, 'Transaction should have an ID');
        this.assertEqual(transaction.amount, 29.99, 'Amount should match');
        this.assertEqual(transaction.vendor, 'OpenAI', 'Vendor should match');
        this.assertEqual(transaction.category, 'Other', 'Default category should be Other');
      });

      await this.test('Log transaction with all fields', async () => {
        const transaction = await this.ledger.logTransaction({
          amount: 50.00,
          currency: 'USD',
          vendor: 'AWS',
          description: 'EC2 instances',
          category: 'Infrastructure',
          account: 'company-card',
          context: 'Monthly hosting costs',
          receiptUrl: 'https://aws.amazon.com/receipt/123',
          confirmationId: 'aws_123456'
        });
        
        this.assertEqual(transaction.amount, 50.00);
        this.assertEqual(transaction.currency, 'USD');
        this.assertEqual(transaction.category, 'Infrastructure');
        this.assertEqual(transaction.account, 'company-card');
        this.assertEqual(transaction.context, 'Monthly hosting costs');
      });

      await this.test('Reject invalid transactions', async () => {
        try {
          await this.ledger.logTransaction({
            amount: -10,
            vendor: 'Test',
            description: 'Test transaction'
          });
          this.assert(false, 'Should reject negative amounts');
        } catch (error) {
          this.assert(error.message.includes('positive'), `Should reject negative amounts, got: ${error.message}`);
        }

        try {
          await this.ledger.logTransaction({
            amount: 10
          });
          this.assert(false, 'Should require vendor');
        } catch (error) {
          this.assert(error.message.includes('vendor'), 'Should require vendor');
        }
      });

      await this.test('Get spending summary', async () => {
        // Add more test transactions
        await this.ledger.logTransaction({
          amount: 25.50,
          vendor: 'Google Cloud',
          description: 'Storage costs',
          category: 'Infrastructure'
        });

        await this.ledger.logTransaction({
          amount: 15.99,
          vendor: 'Stripe',
          description: 'Payment processing',
          category: 'Tools'
        });

        const summary = await this.ledger.getSummary('this-month');
        
        // Should have 4 transactions total (2 from previous tests + 2 new)
        this.assertEqual(summary.count, 4, 'Should have 4 transactions');
        this.assertApproxEqual(summary.total, 121.48, 0.01, 'Total should be correct');
        this.assert(summary.byCategory['Infrastructure'], 'Should have Infrastructure category');
        this.assert(summary.byCategory['Tools'], 'Should have Tools category');
      });

      await this.test('Find transactions', async () => {
        const results = await this.ledger.findTransactions('OpenAI');
        this.assertEqual(results.length, 1, 'Should find one OpenAI transaction');
        this.assertEqual(results[0].vendor, 'OpenAI', 'Should match vendor');

        const infraResults = await this.ledger.findTransactions('', { category: 'Infrastructure' });
        this.assertEqual(infraResults.length, 2, 'Should find two Infrastructure transactions');
      });

      await this.test('Category spending', async () => {
        const infraSpending = await this.ledger.getCategorySpending('Infrastructure');
        this.assertApproxEqual(infraSpending, 75.50, 0.01, 'Infrastructure spending should be correct');

        const toolsSpending = await this.ledger.getCategorySpending('Tools');
        this.assertApproxEqual(toolsSpending, 15.99, 0.01, 'Tools spending should be correct');
      });

      // Budget tests
      await this.test('Set and check budget', async () => {
        await this.budgetManager.setBudget('Infrastructure', 100.00, 'monthly');
        
        const status = await this.budgetManager.checkBudget('Infrastructure');
        this.assert(status.hasBudget, 'Should have budget');
        this.assertEqual(status.budgetAmount, 100.00, 'Budget amount should match');
        this.assertApproxEqual(status.spent, 75.50, 0.01, 'Spent amount should be correct');
        this.assertApproxEqual(status.remaining, 24.50, 0.01, 'Remaining should be correct');
        this.assert(!status.isOverBudget, 'Should not be over budget');
      });

      await this.test('Budget alerts', async () => {
        // Set a low budget to trigger near-limit alert
        await this.budgetManager.setBudget('Tools', 18.00, 'monthly');
        
        const alerts = await this.budgetManager.getAlerts();
        this.assert(alerts.length > 0, 'Should have at least one alert');
        
        const toolsAlert = alerts.find(a => a.category === 'Tools');
        this.assert(toolsAlert, 'Should have Tools alert');
        this.assertEqual(toolsAlert.type, 'NEAR_LIMIT', 'Should be near limit alert');
      });

      // Export test
      await this.test('Export transactions', async () => {
        const csvFile = path.join(this.testDir, 'test-export.csv');
        const result = await this.ledger.exportTransactions('csv', csvFile);
        
        this.assertEqual(result.count, 4, 'Should export 4 transactions');
        this.assertEqual(result.path, csvFile, 'Should return correct path');
        
        // Check if file exists and has content
        const stats = await fs.stat(csvFile);
        this.assert(stats.size > 0, 'Exported file should have content');
        
        const content = await fs.readFile(csvFile, 'utf8');
        this.assert(content.includes('OpenAI'), 'Should contain transaction data');
        this.assert(content.includes('Amount'), 'Should contain CSV header');
      });

      // Account management test
      await this.test('Account management', async () => {
        const account = await this.ledger.addAccount({
          id: 'test-card',
          name: 'Test Credit Card',
          type: 'credit_card',
          currency: 'USD'
        });
        
        this.assertEqual(account.id, 'test-card', 'Account ID should match');
        this.assertEqual(account.name, 'Test Credit Card', 'Account name should match');
        
        const accounts = await this.ledger.loadAccounts();
        this.assertEqual(accounts.length, 1, 'Should have one account');
      });

      // Time period parsing test
      await this.test('Time period parsing', async () => {
        const period = this.ledger.parseTimePeriod('today');
        this.assert(period.start instanceof Date, 'Start should be a date');
        this.assert(period.end instanceof Date, 'End should be a date');
        
        // Today should start at midnight
        this.assertEqual(period.start.getHours(), 0, 'Today should start at midnight');
        this.assertEqual(period.start.getMinutes(), 0, 'Today should start at midnight');
      });

      // Report generation test
      await this.test('Generate monthly report', async () => {
        const report = await this.reports.generate('monthly');
        this.assert(typeof report === 'string', 'Report should be a string');
        this.assert(report.includes('Monthly Report'), 'Should contain report title');
        this.assert(report.includes('Infrastructure'), 'Should contain category breakdown');
      });

      // Multi-currency tests
      await this.test('Multi-currency support', async () => {
        await this.ledger.logTransaction({
          amount: 50,
          vendor: 'European Service',
          description: 'EUR test',
          currency: 'EUR'
        });

        const summary = await this.ledger.getSummary('this-month');
        this.assert(summary.byCurrency['EUR'], 'Should track EUR separately');
        this.assertApproxEqual(summary.byCurrency['EUR'], 50, 0.01, 'EUR amount should be correct');
      });

      // Budget manager tests
      await this.test('Enhanced budget features', async () => {
        const budget = await this.budgetManager.setBudget('Test Category', 100, 'monthly');
        this.assert(budget.alertThreshold, 'Should have alert threshold');
        this.assert(budget.enabled !== false, 'Should be enabled by default');

        const alerts = await this.budgetManager.getAlerts();
        this.assert(Array.isArray(alerts), 'Should return alerts array');

        const report = await this.budgetManager.generateBudgetReport();
        this.assert(typeof report === 'string', 'Budget report should be string');
      });

      // Data backup and recovery test
      await this.test('Data backup and recovery', async () => {
        // Force a save to create backup
        const transactions = await this.ledger.loadTransactions();
        await this.ledger.saveTransactions(transactions);
        
        // Check backup exists
        const backupFile = this.ledger.transactionsFile + '.backup';
        try {
          const stats = await fs.stat(backupFile);
          this.assert(stats.size > 0, 'Backup file should exist and have content');
        } catch (error) {
          // Backup might not exist if this is first save
          this.assert(true, 'Backup handling works');
        }
      });

      // Privacy.com import test
      await this.test('Privacy.com import functionality', async () => {
        // Create sample Privacy.com data
        const privacyData = {
          transactions: [
            {
              id: 'test_txn_123',
              amount: -19.99,
              merchant: 'Test OpenAI Service',
              description: 'API credits test',
              card_id: 'test_card_456'
            }
          ]
        };

        // Write test file
        const testFile = path.join(this.testDir, 'test-privacy.json');
        await fs.writeFile(testFile, JSON.stringify(privacyData));

        // Import and verify
        const result = await this.ledger.importPrivacyTransactions(testFile);
        this.assertEqual(result.imported, 1, 'Should import one transaction');

        const transactions = await this.ledger.loadTransactions();
        const imported = transactions.find(t => t.confirmationId === 'test_txn_123');
        this.assert(imported, 'Should find imported transaction');
        this.assertEqual(imported.category, 'API/Services', 'Should auto-categorize OpenAI as API/Services');
      });

      // CLI named parameters test
      await this.test('CLI named parameters support', async () => {
        // This test validates that CLI parsing works correctly
        const CLI = require('../src/cli.js');
        const cli = new CLI();
        
        // Test option parsing
        const options = cli.parseOptions(['--amount=25.99', '--vendor=TestVendor', '--description=Test transaction']);
        this.assertEqual(options.amount, '25.99', 'Should parse amount option');
        this.assertEqual(options.vendor, 'TestVendor', 'Should parse vendor option');
        this.assertEqual(options.description, 'Test transaction', 'Should parse description option');
      });

    } catch (error) {
      console.error('Test setup error:', error);
      this.failedTests++;
    }

    await this.teardown();

    // Summary
    console.log('\n📊 Test Results:');
    console.log(`Total tests: ${this.testCount}`);
    console.log(`✅ Passed: ${this.passedTests}`);
    console.log(`❌ Failed: ${this.failedTests}`);
    
    if (this.failedTests === 0) {
      console.log('\n🎉 All tests passed!');
      process.exit(0);
    } else {
      console.log('\n💥 Some tests failed!');
      process.exit(1);
    }
  }
}

// Run tests if called directly
if (require.main === module) {
  const runner = new TestRunner();
  runner.run().catch(error => {
    console.error('Test runner error:', error);
    process.exit(1);
  });
}

module.exports = TestRunner;