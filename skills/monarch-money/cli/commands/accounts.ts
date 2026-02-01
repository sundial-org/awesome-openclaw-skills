import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { getClient } from '../client';
import { printTable, printJSON, printError, formatCurrency, truncate } from '../utils/output';

export const accountsCommand = new Command('accounts')
  .alias('acc')
  .description('Account management');

accountsCommand
  .command('list')
  .description('List all accounts')
  .option('--type <type>', 'Filter by account type')
  .option('--hidden', 'Include hidden accounts')
  .option('--json', 'Output as JSON')
  .action(async (options) => {
    const spinner = ora('Fetching accounts...').start();
    
    try {
      const client = await getClient();
      let accounts = await client.accounts.getAll({ includeHidden: options.hidden });
      
      spinner.stop();

      // Filter by type if specified
      if (options.type) {
        const typeLower = options.type.toLowerCase();
        accounts = accounts.filter((a: any) => 
          a.type?.display?.toLowerCase().includes(typeLower) ||
          a.subtype?.display?.toLowerCase().includes(typeLower)
        );
      }

      if (options.json) {
        printJSON(accounts);
        return;
      }

      if (accounts.length === 0) {
        console.log(chalk.yellow('No accounts found'));
        return;
      }

      console.log(chalk.bold(`\n${accounts.length} account(s):\n`));

      // Calculate total balance
      const totalBalance = accounts.reduce((sum: number, a: any) => 
        sum + (a.currentBalance || 0), 0
      );

      printTable(
        ['ID', 'Name', 'Type', 'Balance', 'Institution'],
        accounts.map((a: any) => [
          a.id,
          truncate(a.displayName || 'Unknown', 30),
          a.type?.display || a.subtype?.display || '-',
          formatCurrency(a.currentBalance || 0),
          truncate(a.institution?.name || '-', 20),
        ])
      );

      console.log(chalk.bold(`\nTotal Balance: ${formatCurrency(totalBalance)}`));
    } catch (error) {
      spinner.fail('Failed to fetch accounts');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

accountsCommand
  .command('get <id>')
  .description('Get account details')
  .option('--json', 'Output as JSON')
  .action(async (id, options) => {
    const spinner = ora('Fetching account...').start();
    
    try {
      const client = await getClient();
      const account = await client.accounts.getById(id);
      
      spinner.stop();

      if (!account) {
        printError(`Account ${id} not found`);
        process.exit(1);
      }

      if (options.json) {
        printJSON(account);
        return;
      }

      console.log(chalk.bold('\nAccount Details:\n'));
      console.log(`  ${chalk.cyan('ID:')}           ${account.id}`);
      console.log(`  ${chalk.cyan('Name:')}         ${account.displayName}`);
      console.log(`  ${chalk.cyan('Type:')}         ${(account as any).type?.display || '-'}`);
      console.log(`  ${chalk.cyan('Subtype:')}      ${(account as any).subtype?.display || '-'}`);
      console.log(`  ${chalk.cyan('Balance:')}      ${formatCurrency(account.currentBalance || 0)}`);
      console.log(`  ${chalk.cyan('Institution:')} ${(account as any).institution?.name || '-'}`);
      if ((account as any).lastSyncedAt) {
        console.log(`  ${chalk.cyan('Last Synced:')} ${new Date((account as any).lastSyncedAt).toLocaleString()}`);
      }
    } catch (error) {
      spinner.fail('Fetch failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });
