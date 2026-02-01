import { Command } from 'commander';
import { login, logout, status as authStatus, refresh as authRefresh } from './auth/oauth.js';
import { fetchData, fetchAllTypes } from './api/client.js';
import { getWhoopDay, validateISODate, getDaysAgo } from './utils/date.js';
import { handleError, WhoopError, ExitCode } from './utils/errors.js';
import { formatPretty, formatSummary, formatSummaryColor } from './utils/format.js';
import { analyzeTrends, generateInsights, formatTrends, formatInsights } from './utils/analysis.js';
import type { DataType, WhoopData } from './types/whoop.js';

export const program = new Command();

function output(data: WhoopData, pretty: boolean): void {
  console.log(pretty ? formatPretty(data) : JSON.stringify(data, null, 2));
}

program
  .name('whoopskill')
  .description('CLI for fetching WHOOP health data')
  .version('1.1.0');

program
  .command('auth')
  .description('Manage authentication')
  .argument('<action>', 'login, logout, status, or refresh')
  .action(async (action: string) => {
    try {
      switch (action) {
        case 'login':
          await login();
          break;
        case 'logout':
          logout();
          break;
        case 'status':
          authStatus();
          break;
        case 'refresh':
          await authRefresh();
          break;
        default:
          throw new WhoopError(`Unknown auth action: ${action}. Use: login, logout, status, or refresh`, ExitCode.GENERAL_ERROR);
      }
    } catch (error) {
      handleError(error);
    }
  });

function addDataCommand(name: string, description: string, dataType: DataType): void {
  program
    .command(name)
    .description(description)
    .option('-d, --date <date>', 'Date in ISO format (YYYY-MM-DD)')
    .option('-s, --start <date>', 'Start date for range query')
    .option('-e, --end <date>', 'End date for range query')
    .option('-l, --limit <number>', 'Max results per page', '25')
    .option('-a, --all', 'Fetch all pages')
    .option('-p, --pretty', 'Human-readable output')
    .action(async (options) => {
      try {
        const date = options.date || getWhoopDay();
        if (options.date && !validateISODate(options.date)) {
          throw new WhoopError('Invalid date format. Use YYYY-MM-DD', ExitCode.GENERAL_ERROR);
        }

        const result = await fetchData([dataType], date, {
          limit: parseInt(options.limit, 10),
          all: options.all,
        });

        output(result, options.pretty);
      } catch (error) {
        handleError(error);
      }
    });
}

addDataCommand('sleep', 'Get sleep data', 'sleep');
addDataCommand('recovery', 'Get recovery data', 'recovery');
addDataCommand('workout', 'Get workout data', 'workout');
addDataCommand('cycle', 'Get cycle data', 'cycle');
addDataCommand('profile', 'Get profile data', 'profile');
addDataCommand('body', 'Get body measurements', 'body');

program
  .command('summary')
  .description('One-liner health snapshot')
  .option('-d, --date <date>', 'Date in ISO format (YYYY-MM-DD)')
  .option('-c, --color', 'Color-coded output with status indicators')
  .action(async (options) => {
    try {
      const date = options.date || getWhoopDay();
      if (options.date && !validateISODate(options.date)) {
        throw new WhoopError('Invalid date format. Use YYYY-MM-DD', ExitCode.GENERAL_ERROR);
      }

      const result = await fetchData(['recovery', 'sleep', 'cycle', 'workout'], date, { limit: 25 });
      console.log(options.color ? formatSummaryColor(result) : formatSummary(result));
    } catch (error) {
      handleError(error);
    }
  });

program
  .command('trends')
  .description('Show trends over time (7/14/30 days)')
  .option('-n, --days <number>', 'Number of days to analyze', '7')
  .option('--json', 'Output raw JSON instead of formatted text')
  .action(async (options) => {
    try {
      const days = parseInt(options.days, 10);
      if (![7, 14, 30].includes(days)) {
        throw new WhoopError('Days must be 7, 14, or 30', ExitCode.GENERAL_ERROR);
      }

      const endDate = getWhoopDay();
      const startDate = getDaysAgo(days);
      const params = { start: startDate + 'T00:00:00.000Z', end: endDate + 'T23:59:59.999Z', limit: days + 5 };

      const [recovery, sleep, cycle] = await Promise.all([
        import('./api/client.js').then(m => m.getRecovery(params, true)),
        import('./api/client.js').then(m => m.getSleep(params, true)),
        import('./api/client.js').then(m => m.getCycle(params, true)),
      ]);

      const trends = analyzeTrends(recovery, sleep, cycle, days);
      console.log(formatTrends(trends, !options.json));
    } catch (error) {
      handleError(error);
    }
  });

program
  .command('insights')
  .description('AI-style health insights and recommendations')
  .option('-d, --date <date>', 'Date in ISO format (YYYY-MM-DD)')
  .option('--json', 'Output raw JSON instead of formatted text')
  .action(async (options) => {
    try {
      const date = options.date || getWhoopDay();
      if (options.date && !validateISODate(options.date)) {
        throw new WhoopError('Invalid date format. Use YYYY-MM-DD', ExitCode.GENERAL_ERROR);
      }

      const startDate = getDaysAgo(7);
      const params = { start: startDate + 'T00:00:00.000Z', end: date + 'T23:59:59.999Z' };

      const [recovery, sleep, cycle, workout] = await Promise.all([
        import('./api/client.js').then(m => m.getRecovery(params, true)),
        import('./api/client.js').then(m => m.getSleep(params, true)),
        import('./api/client.js').then(m => m.getCycle(params, true)),
        import('./api/client.js').then(m => m.getWorkout({ start: date + 'T00:00:00.000Z', end: date + 'T23:59:59.999Z' }, true)),
      ]);

      const insights = generateInsights(recovery, sleep, cycle, workout);
      console.log(formatInsights(insights, !options.json));
    } catch (error) {
      handleError(error);
    }
  });

program
  .option('-d, --date <date>', 'Date in ISO format (YYYY-MM-DD)')
  .option('-l, --limit <number>', 'Max results per page', '25')
  .option('-a, --all', 'Fetch all pages')
  .option('-p, --pretty', 'Human-readable output')
  .option('--sleep', 'Include sleep data')
  .option('--recovery', 'Include recovery data')
  .option('--workout', 'Include workout data')
  .option('--cycle', 'Include cycle data')
  .option('--profile', 'Include profile data')
  .option('--body', 'Include body measurements')
  .action(async (options) => {
    try {
      const types: DataType[] = [];
      if (options.sleep) types.push('sleep');
      if (options.recovery) types.push('recovery');
      if (options.workout) types.push('workout');
      if (options.cycle) types.push('cycle');
      if (options.profile) types.push('profile');
      if (options.body) types.push('body');

      if (types.length === 0) {
        program.help();
        return;
      }

      const date = options.date || getWhoopDay();
      if (options.date && !validateISODate(options.date)) {
        throw new WhoopError('Invalid date format. Use YYYY-MM-DD', ExitCode.GENERAL_ERROR);
      }

      const result = await fetchData(types, date, {
        limit: parseInt(options.limit, 10),
        all: options.all,
      });

      output(result, options.pretty);
    } catch (error) {
      handleError(error);
    }
  });
