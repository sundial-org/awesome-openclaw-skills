import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { getClient } from '../client';
import { printTable, printJSON, printError } from '../utils/output';

export const categoriesCommand = new Command('categories')
  .alias('cat')
  .description('Category management');

categoriesCommand
  .command('list')
  .description('List all categories')
  .option('-g, --group <name>', 'Filter by group name')
  .option('--json', 'Output as JSON')
  .action(async (options) => {
    const spinner = ora('Fetching categories...').start();
    
    try {
      const client = await getClient();
      let categories = await client.categories.getCategories();
      
      spinner.stop();

      // Filter by group if specified
      if (options.group) {
        const groupLower = options.group.toLowerCase();
        categories = categories.filter((c: any) => 
          c.group?.name?.toLowerCase().includes(groupLower)
        );
      }

      if (options.json) {
        printJSON(categories);
        return;
      }

      if (categories.length === 0) {
        console.log(chalk.yellow('No categories found'));
        return;
      }

      console.log(chalk.bold(`\n${categories.length} categories:\n`));

      // Group categories by their group
      const grouped: Record<string, any[]> = {};
      categories.forEach((cat: any) => {
        const groupName = cat.group?.name || 'Ungrouped';
        if (!grouped[groupName]) grouped[groupName] = [];
        grouped[groupName].push(cat);
      });

      for (const [groupName, cats] of Object.entries(grouped)) {
        console.log(chalk.cyan.bold(`\n${groupName}:`));
        printTable(
          ['ID', 'Name', 'Icon'],
          cats.map((c: any) => [
            c.id,
            c.name,
            c.icon || '-',
          ])
        );
      }
    } catch (error) {
      spinner.fail('Failed to fetch categories');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

categoriesCommand
  .command('search <query>')
  .description('Search categories by name')
  .option('--json', 'Output as JSON')
  .action(async (query, options) => {
    const spinner = ora('Searching categories...').start();
    
    try {
      const client = await getClient();
      const allCategories = await client.categories.getCategories();
      
      spinner.stop();

      const queryLower = query.toLowerCase();
      const categories = allCategories.filter((c: any) =>
        c.name?.toLowerCase().includes(queryLower) ||
        c.group?.name?.toLowerCase().includes(queryLower)
      );

      if (options.json) {
        printJSON(categories);
        return;
      }

      if (categories.length === 0) {
        console.log(chalk.yellow(`No categories matching "${query}"`));
        return;
      }

      console.log(chalk.bold(`\nFound ${categories.length} category(ies):\n`));

      printTable(
        ['ID', 'Name', 'Group'],
        categories.map((c: any) => [
          c.id,
          c.name,
          c.group?.name || '-',
        ])
      );
    } catch (error) {
      spinner.fail('Search failed');
      printError(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });
