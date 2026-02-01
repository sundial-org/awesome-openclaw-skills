import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { readFileSync, existsSync } from 'fs';
import { getClient } from '../client';
import { 
  printTable, 
  printJSON, 
  printSuccess, 
  printError, 
  printWarning,
  formatCurrency 
} from '../utils/output';

interface SplitItem {
  description: string;
  amount: number;
  category: string;  // Category name or ID
  notes?: string;
}

export const receiptsCommand = new Command('receipts')
  .description('Receipt splitting and management');

receiptsCommand
  .command('split <transactionId>')
  .description('Split a transaction by receipt items')
  .option('-f, --file <path>', 'JSON file with split items')
  .option('-i, --items <json>', 'Inline JSON array of split items')
  .option('--dry-run', 'Preview without making changes')
  .option('--json', 'Output as JSON')
  .action(async (transactionId, options) => {
    try {
      // Parse split items
      let items: SplitItem[];
      
      if (options.file) {
        if (!existsSync(options.file)) {
          printError(`File not found: ${options.file}`);
          process.exit(1);
        }
        items = JSON.parse(readFileSync(options.file, 'utf-8'));
      } else if (options.items) {
        items = JSON.parse(options.items);
      } else {
        printError('Provide --file or --items with split data');
        console.log('\nExample JSON format:');
        console.log(JSON.stringify([
          { description: 'Groceries', amount: 25.99, category: 'Groceries' },
          { description: 'Cleaning supplies', amount: 12.50, category: 'Home' },
        ], null, 2));
        process.exit(1);
      }

      if (!Array.isArray(items) || items.length === 0) {
        printError('Items must be a non-empty array');
        process.exit(1);
      }

      const totalSplit = items.reduce((sum, item) => sum + item.amount, 0);

      console.log(chalk.bold('\nSplit Preview:\n'));
      printTable(
        ['Item', 'Amount', 'Category', 'Notes'],
        items.map(item => [
          item.description,
          formatCurrency(-item.amount),
          item.category,
          item.notes || '-',
        ])
      );
      console.log(chalk.bold(`\nTotal: ${formatCurrency(-totalSplit)}`));

      if (options.dryRun) {
        printWarning('Dry run - no changes made');
        return;
      }

      const spinner = ora('Applying split...').start();

      const client = await getClient();

      // First, get the original transaction
      const originalTx = await client.transactions.getTransactionDetails(transactionId);

      if (!originalTx) {
        spinner.fail('Transaction not found');
        process.exit(1);
      }

      // Verify amounts match (with small tolerance for rounding)
      const originalAmount = Math.abs(originalTx.amount);
      if (Math.abs(totalSplit - originalAmount) > 0.02) {
        spinner.warn(
          `Split total (${formatCurrency(-totalSplit)}) differs from original (${formatCurrency(originalTx.amount)})`
        );
      }

      // Get categories to resolve names to IDs
      const categories = await client.categories.getCategories();
      
      const categoryMap = new Map<string, string>();
      categories.forEach((c: any) => {
        categoryMap.set(c.name.toLowerCase(), c.id);
        categoryMap.set(c.id, c.id);
      });

      // Build splits array for the API
      const splits = items.map(item => {
        const categoryId = categoryMap.get(item.category.toLowerCase()) || 
                          categoryMap.get(item.category);
        
        if (!categoryId) {
          throw new Error(`Category "${item.category}" not found`);
        }

        return {
          merchantName: item.description,
          amount: item.amount,
          categoryId,
          notes: item.notes,
          hideFromReports: false,
        };
      });

      // Use the transaction splits API
      await client.transactions.updateTransactionSplits(transactionId, splits);

      spinner.stop();

      if (options.json) {
        printJSON({ success: true, transactionId, splits: items });
        return;
      }

      printSuccess(`Split transaction ${transactionId} into ${items.length} parts`);
    } catch (error) {
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

receiptsCommand
  .command('template')
  .description('Print a template for split items')
  .action(() => {
    const template = [
      {
        description: 'Item 1 description',
        amount: 10.99,
        category: 'Groceries',
        notes: 'Optional notes',
      },
      {
        description: 'Item 2 description',
        amount: 5.50,
        category: 'Home',
      },
    ];
    
    console.log(chalk.bold('\nSplit items template:\n'));
    console.log(JSON.stringify(template, null, 2));
    console.log(chalk.dim('\nSave as JSON file and use with: monarch receipts split <txId> -f items.json'));
  });
