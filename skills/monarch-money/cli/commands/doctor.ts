import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { existsSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import https from 'https';
import { MonarchClient } from '../../lib';
import { printSuccess, printWarning, printError, printInfo } from '../utils/output';

const BASE_URL = 'https://api.monarch.com';
const SESSION_FILE = join(homedir(), '.mm', 'session.json');

export const doctorCommand = new Command('doctor')
  .description('Check CLI setup, environment, and API connectivity')
  .action(async () => {
    const issues: string[] = [];
    const warnings: string[] = [];

    // Node version
    const nodeMajor = parseInt(process.versions.node.split('.')[0] || '0', 10);
    if (nodeMajor < 18) {
      issues.push(`Node.js ${process.versions.node} detected (requires >= 18)`);
    }

    // Env vars
    const email = process.env.MONARCH_EMAIL;
    const password = process.env.MONARCH_PASSWORD;
    const mfaSecret = process.env.MONARCH_MFA_SECRET;

    if (!email) warnings.push('MONARCH_EMAIL not set (needed for login)');
    if (!password) warnings.push('MONARCH_PASSWORD not set (needed for login)');
    if (!mfaSecret) warnings.push('MONARCH_MFA_SECRET not set (only required if MFA enabled)');

    // Session file check
    if (!existsSync(SESSION_FILE)) {
      warnings.push('No session found (~/.mm/session.json). Run: monarch auth login');
    } else {
      try {
        const session = JSON.parse(readFileSync(SESSION_FILE, 'utf-8'));
        if (session?.email) {
          printInfo(`Session file found for ${session.email}`);
        } else {
          printInfo('Session file found');
        }
      } catch {
        warnings.push('Session file exists but could not be parsed');
      }
    }

    // API connectivity
    const apiSpinner = ora('Checking API connectivity...').start();
    try {
      const url = new URL(`${BASE_URL}/graphql`);
      const body = JSON.stringify({ query: '{ __typename }' });
      const status = await new Promise<number>((resolve, reject) => {
        const req = https.request(
          {
            hostname: url.hostname,
            path: url.pathname,
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Content-Length': Buffer.byteLength(body),
            },
            agent: new https.Agent({ keepAlive: false }),
          },
          (res) => {
            res.resume();
            res.on('end', () => resolve(res.statusCode || 0));
          }
        );
        req.on('error', reject);
        req.write(body);
        req.end();
      });

      apiSpinner.stop();
      if (status === 525) {
        issues.push('API endpoint returned 525 (Cloudflare)');
      } else if (status >= 500) {
        issues.push(`API endpoint returned ${status}`);
      } else {
        printInfo(`API reachable (${status})`);
      }
    } catch (err) {
      apiSpinner.fail('API connectivity check failed');
      issues.push(err instanceof Error ? err.message : String(err));
    }

    // Session validation (if present)
    const sessionSpinner = ora('Validating saved session...').start();
    try {
      const client = new MonarchClient({ baseURL: BASE_URL, enablePersistentCache: false });
      const loaded = client.loadSession();
      if (!loaded) {
        sessionSpinner.fail('No valid session loaded');
      } else {
        await client.accounts.getAll();
        sessionSpinner.succeed('Session is valid');
      }
      await client.close();
    } catch {
      sessionSpinner.fail('Session invalid or expired');
    }

    // Summary
    if (issues.length === 0 && warnings.length === 0) {
      printSuccess('Doctor check passed');
      return;
    }

    if (warnings.length > 0) {
      console.log(chalk.yellow('\nWarnings:'));
      warnings.forEach(w => console.log(`  - ${w}`));
    }

    if (issues.length > 0) {
      console.log(chalk.red('\nIssues:'));
      issues.forEach(i => console.log(`  - ${i}`));
      process.exitCode = 1;
    }
  });
