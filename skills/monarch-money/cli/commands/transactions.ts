import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { getClient } from '../client';
import { 
  printTable, 
  printJSON, 
  printSuccess, 
  printError,
  formatCurrency, 
  formatDate, 
  truncate 
} from '../utils/output';

export const transactionsCommand = new Command('transactions')
  .alias('tx')
  .description('Transaction management');

transactionsCommand
  .command('search')
  .description('Search transactions')
  .option('-m, --merchant <name>', 'Filter by merchant name')
  .option('-c, --category <name>', 'Filter by category name')
  .option('-a, --account <name>', 'Filter by account name')
  .option('--start <date>', 'Start date (YYYY-MM-DD)')
  .option('--end <date>', 'End date (YYYY-MM-DD)')
  .option('--min <amount>', 'Minimum amount')
  .option('--max <amount>', 'Maximum amount')
  .option('-l, --limit <n>', 'Limit results', '20')
  .option('--json', 'Output as JSON')
  .action(async (options) => {
    const spinner = ora('Searching transactions...').start();
    
    try {
      const client = await getClient();
      
      const searchOptions: any = {
        limit: parseInt(options.limit),
      };
      
      if (options.merchant) {
        searchOptions.search = options.merchant;
      }
      if (options.start) {
        searchOptions.startDate = options.start;
      }
      if (options.end) {
        searchOptions.endDate = options.end;
      }
      if (options.min) {
        searchOptions.absAmountRange = [parseFloat(options.min), undefined];
      }
      if (options.max) {
        const range = searchOptions.absAmountRange || [undefined, undefined];
        searchOptions.absAmountRange = [range[0], parseFloat(options.max)];
      }

      const result = await client.transactions.getTransactions(searchOptions);

      spinner.stop();

      // Filter by category/account if specified (client-side filtering)
      let transactions = result.transactions || [];
      
      if (options.category) {
        const categoryLower = options.category.toLowerCase();
        transactions = transactions.filter((t: any) => 
          t.category?.name?.toLowerCase().includes(categoryLower)
        );
      }
      
      if (options.account) {
        const accountLower = options.account.toLowerCase();
        transactions = transactions.filter((t: any) => 
          t.account?.displayName?.toLowerCase().includes(accountLower)
        );
      }

      if (options.json) {
        printJSON(transactions);
        return;
      }

      if (transactions.length === 0) {
        console.log(chalk.yellow('No transactions found'));
        return;
      }

      console.log(chalk.bold(`\nFound ${transactions.length} transaction(s):\n`));
      
      printTable(
        ['ID', 'Date', 'Merchant', 'Amount', 'Category', 'Account'],
        transactions.map((t: any) => [
          t.id,
          formatDate(t.date),
          truncate(t.merchant?.name || 'Unknown', 25),
          formatCurrency(t.amount),
          truncate(t.category?.name || 'Uncategorized', 20),
          truncate(t.account?.displayName || 'Unknown', 15),
        ])
      );
    } catch (error) {
      spinner.fail('Search failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

transactionsCommand
  .command('get <id>')
  .description('Get transaction details')
  .option('--json', 'Output as JSON')
  .action(async (id, options) => {
    const spinner = ora('Fetching transaction...').start();
    
    try {
      const client = await getClient();
      let transaction: any = null;

      try {
        // Primary: get full transaction details
        transaction = await client.transactions.getTransactionDetails(id);
      } catch {
        // Fallback: page through recent transactions and match by ID
        const pageSize = 100;
        const maxPages = 10; // 1000 transactions
        for (let page = 0; page < maxPages; page++) {
          const result = await client.transactions.getTransactions({
            limit: pageSize,
            offset: page * pageSize,
          });
          transaction = (result.transactions || []).find((t: any) => t.id === id);
          if (transaction || !result.hasMore) break;
        }
      }

      spinner.stop();

      if (!transaction) {
        printError(`Transaction ${id} not found`);
        process.exit(1);
      }

      if (options.json) {
        printJSON(transaction);
        return;
      }

      console.log(chalk.bold('\nTransaction Details:\n'));
      console.log(`  ${chalk.cyan('ID:')}        ${transaction.id}`);
      console.log(`  ${chalk.cyan('Date:')}      ${formatDate(transaction.date)}`);
      console.log(`  ${chalk.cyan('Merchant:')}  ${transaction.merchant?.name || 'Unknown'}`);
      console.log(`  ${chalk.cyan('Amount:')}    ${formatCurrency(transaction.amount)}`);
      console.log(`  ${chalk.cyan('Category:')} ${transaction.category?.name || 'Uncategorized'}`);
      console.log(`  ${chalk.cyan('Account:')}  ${transaction.account?.displayName || 'Unknown'}`);
      if (transaction.notes) {
        console.log(`  ${chalk.cyan('Notes:')}    ${transaction.notes}`);
      }
    } catch (error) {
      spinner.fail('Fetch failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

transactionsCommand
  .command('update <id>')
  .description('Update a transaction')
  .option('-c, --category <id>', 'Set category by ID')
  .option('-n, --notes <text>', 'Set notes')
  .option('--json', 'Output as JSON')
  .action(async (id, options) => {
    const spinner = ora('Updating transaction...').start();
    
    try {
      const client = await getClient();
      
      const updates: any = {};
      
      if (options.category) {
        updates.categoryId = options.category;
      }
      if (options.notes !== undefined) {
        updates.notes = options.notes;
      }

      await client.transactions.updateTransaction(id, updates);

      spinner.succeed(`Transaction ${id} updated`);
      
      if (options.json) {
        printJSON({ success: true, id, updates });
      }
    } catch (error) {
      spinner.fail('Update failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

transactionsCommand
  .command('categorize <transactionId> <categoryId>')
  .description('Set transaction category')
  .action(async (transactionId, categoryId) => {
    const spinner = ora('Setting category...').start();
    
    try {
      const client = await getClient();
      await client.transactions.updateTransaction(transactionId, { categoryId });
      spinner.succeed(`Category set for transaction ${transactionId}`);
    } catch (error) {
      spinner.fail('Failed to set category');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

transactionsCommand
  .command('create')
  .description('Create a manual transaction')
  .requiredOption('-a, --account <id>', 'Account ID')
  .requiredOption('-m, --merchant <name>', 'Merchant name')
  .requiredOption('-A, --amount <number>', 'Amount (e.g., 12.34)')
  .requiredOption('-d, --date <YYYY-MM-DD>', 'Transaction date')
  .option('-c, --category <id>', 'Category ID')
  .option('-n, --notes <text>', 'Notes')
  .option('--json', 'Output as JSON')
  .action(async (options) => {
    const spinner = ora('Creating transaction...').start();

    try {
      const client = await getClient();
      const amount = parseFloat(options.amount);
      if (Number.isNaN(amount)) {
        spinner.fail('Amount must be a number');
        process.exit(1);
      }

      const tx = await client.transactions.createTransaction({
        accountId: options.account,
        merchantName: options.merchant,
        amount,
        date: options.date,
        categoryId: options.category,
        notes: options.notes,
      });

      spinner.succeed(`Transaction created (${tx.id})`);

      if (options.json) {
        printJSON(tx);
      }
    } catch (error) {
      spinner.fail('Create failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

transactionsCommand
  .command('delete <id>')
  .description('Delete a transaction')
  .option('--yes', 'Confirm deletion')
  .option('--json', 'Output as JSON')
  .action(async (id, options) => {
    if (!options.yes) {
      printError('Deletion requires --yes');
      process.exit(1);
    }

    const spinner = ora('Deleting transaction...').start();

    try {
      const client = await getClient();
      const deleted = await client.transactions.deleteTransaction(id);
      if (deleted) {
        spinner.succeed(`Transaction deleted (${id})`);
      } else {
        spinner.fail('Delete failed');
        process.exit(1);
      }

      if (options.json) {
        printJSON({ success: true, id });
      }
    } catch (error) {
      spinner.fail('Delete failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });
