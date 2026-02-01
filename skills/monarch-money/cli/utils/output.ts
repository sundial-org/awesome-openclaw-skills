import chalk from 'chalk';
import Table from 'cli-table3';

export interface OutputOptions {
  json?: boolean;
  verbose?: boolean;
}

export function formatCurrency(amount: number): string {
  const formatted = Math.abs(amount).toFixed(2);
  if (amount < 0) {
    return chalk.red(`-$${formatted}`);
  }
  return chalk.green(`$${formatted}`);
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function printTable(
  headers: string[],
  rows: (string | number)[][],
  options?: { head?: string[] }
): void {
  const table = new Table({
    head: options?.head || headers.map(h => chalk.cyan(h)),
    style: { head: [], border: [] },
  });
  
  rows.forEach(row => table.push(row.map(String)));
  console.log(table.toString());
}

export function printJSON(data: unknown): void {
  console.log(JSON.stringify(data, null, 2));
}

export function printSuccess(message: string): void {
  console.log(chalk.green('✓'), message);
}

export function printError(message: string): void {
  console.error(chalk.red('✗'), message);
}

export function printWarning(message: string): void {
  console.log(chalk.yellow('⚠'), message);
}

export function printInfo(message: string): void {
  console.log(chalk.blue('ℹ'), message);
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.substring(0, length - 3) + '...';
}
