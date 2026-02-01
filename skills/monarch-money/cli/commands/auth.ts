import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { MonarchClient } from '../../lib';
import { saveCliConfig, clearCliConfig, loadCliConfig } from '../client';
import { printSuccess, printError, printInfo } from '../utils/output';

const MONARCH_API_URL = 'https://api.monarch.com';

export const authCommand = new Command('auth')
  .description('Authentication commands');

authCommand
  .command('login')
  .description('Login to Monarch Money')
  .option('-e, --email <email>', 'Email address')
  .option('-p, --password <password>', 'Password')
  .option('--mfa-secret <secret>', 'MFA secret (optional)')
  .action(async (options) => {
    const spinner = ora('Logging in...').start();
    
    try {
      const email = options.email || process.env.MONARCH_EMAIL;
      const password = options.password || process.env.MONARCH_PASSWORD;
      const mfaSecret = options.mfaSecret || process.env.MONARCH_MFA_SECRET;
      
      if (!email || !password) {
        spinner.fail('Email and password required');
        console.log('\nUsage:');
        console.log('  monarch auth login -e <email> -p <password>');
        console.log('\nOr set environment variables:');
        console.log('  MONARCH_EMAIL=your@email.com');
        console.log('  MONARCH_PASSWORD=yourpassword');
        process.exit(1);
      }

      const client = new MonarchClient({ baseURL: MONARCH_API_URL, enablePersistentCache: false });

      await client.login({ email, password, mfaSecretKey: mfaSecret, useSavedSession: true, saveSession: true });
      
      // Save email for status display
      saveCliConfig({ email });

      spinner.succeed(`Logged in as ${chalk.cyan(email)}`);
    } catch (error) {
      spinner.fail('Login failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

authCommand
  .command('logout')
  .description('Logout and clear session')
  .action(() => {
    const client = new MonarchClient({ baseURL: MONARCH_API_URL, enablePersistentCache: false });
    client.deleteSession();
    clearCliConfig();
    printSuccess('Logged out successfully');
  });

authCommand
  .command('status')
  .description('Check authentication status')
  .action(async () => {
    const spinner = ora('Checking session...').start();
    
    try {
      const client = new MonarchClient({ baseURL: MONARCH_API_URL, enablePersistentCache: false });
      const loaded = client.loadSession();
      
      if (!loaded) {
        spinner.fail('Not logged in');
        printInfo('Run: monarch auth login');
        return;
      }
      
      // Try a simple API call to verify session
      await client.accounts.getAll();
      
      const config = loadCliConfig();
      const email = config?.email || 'unknown';
      
      spinner.succeed(`Logged in as ${chalk.cyan(email)}`);
    } catch {
      spinner.fail('Session expired or invalid');
      printInfo('Run: monarch auth login');
    }
  });
