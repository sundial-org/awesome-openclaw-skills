import { Command } from 'commander';
import { spawn } from 'child_process';
import { join } from 'path';

export const testCommand = new Command('test')
  .description('Run E2E tests')
  .option('--auth', 'Run only auth tests')
  .option('--read', 'Run only read tests')
  .option('--write', 'Run only write tests (requires --allow-writes)')
  .option('--allow-writes', 'Enable write tests (modifies real data!)')
  .option('--all', 'Run all tests including write tests')
  .action(async (options) => {
    const env = { ...process.env };

    if (options.allowWrites || options.all) {
      env.ALLOW_WRITE_TESTS = '1';
      console.log('WARNING: Write tests enabled - will modify real data!\n');
    }

    // Determine which tests to run
    let testPattern = 'tests/e2e';

    if (options.auth) {
      testPattern = 'tests/e2e/auth.test.ts';
    } else if (options.read) {
      testPattern = 'tests/e2e/read.test.ts';
    } else if (options.write) {
      testPattern = 'tests/e2e/write.test.ts';
      if (!options.allowWrites) {
        console.log(
          'Note: Write tests will be skipped without --allow-writes\n'
        );
      }
    }

    // Run jest
    const jestArgs = [
      '--runInBand',
      '--testPathPattern',
      testPattern,
      '--passWithNoTests'
    ];

    console.log(`Running tests: ${testPattern}\n`);

    const jest = spawn('npx', ['jest', ...jestArgs], {
      cwd: join(__dirname, '../..'),
      env,
      stdio: 'inherit'
    });

    jest.on('close', (code) => {
      process.exit(code || 0);
    });
  });
