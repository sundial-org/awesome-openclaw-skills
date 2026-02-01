/** @type {import('jest').Config} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/lib', '<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverageFrom: ['lib/**/*.ts', '!lib/**/*.d.ts', '!lib/**/__tests__/**'],
  coverageDirectory: 'coverage',
  verbose: true,
  testTimeout: 30000,
  // E2E tests need longer timeout and run in band
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/lib/**/*.test.ts'],
      testTimeout: 10000
    },
    {
      displayName: 'e2e',
      testMatch: ['<rootDir>/tests/e2e/**/*.test.ts'],
      testTimeout: 60000,
      // Run E2E tests serially to avoid rate limits
      maxWorkers: 1
    }
  ]
};
