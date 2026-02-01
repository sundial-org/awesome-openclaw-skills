---
name: test-specialist
description: This skill should be used when writing test cases, fixing bugs, analyzing code for potential issues, or improving test coverage for JavaScript/TypeScript applications. Use this for unit tests, integration tests, end-to-end tests, debugging runtime errors, logic bugs, performance issues, security vulnerabilities, and systematic code analysis.
---

# Test Specialist

## Overview

Apply systematic testing methodologies and debugging techniques to JavaScript/TypeScript applications. This skill provides comprehensive testing strategies, bug analysis frameworks, and automated tools for identifying coverage gaps and untested code.

## Core Capabilities

### 1. Writing Test Cases

Write comprehensive tests covering unit, integration, and end-to-end scenarios.

#### Unit Testing Approach

Structure tests using the AAA pattern (Arrange-Act-Assert):

```typescript
describe('ExpenseCalculator', () => {
  describe('calculateTotal', () => {
    test('sums expense amounts correctly', () => {
      // Arrange
      const expenses = [
        { amount: 100, category: 'food' },
        { amount: 50, category: 'transport' },
        { amount: 25, category: 'entertainment' }
      ];

      // Act
      const total = calculateTotal(expenses);

      // Assert
      expect(total).toBe(175);
    });

    test('handles empty expense list', () => {
      expect(calculateTotal([])).toBe(0);
    });

    test('handles negative amounts', () => {
      const expenses = [
        { amount: 100, category: 'food' },
        { amount: -50, category: 'refund' }
      ];
      expect(calculateTotal(expenses)).toBe(50);
    });
  });
});
```

**Key principles:**
- Test one behavior per test
- Cover happy path, edge cases, and error conditions
- Use descriptive test names that explain the scenario
- Keep tests independent and isolated

#### Integration Testing Approach

Test how components work together, including database, API, and service interactions:

```typescript
describe('ExpenseAPI Integration', () => {
  beforeAll(async () => {
    await database.connect(TEST_DB_URL);
  });

  afterAll(async () => {
    await database.disconnect();
  });

  beforeEach(async () => {
    await database.clear();
    await seedTestData();
  });

  test('POST /expenses creates expense and updates total', async () => {
    const response = await request(app)
      .post('/api/expenses')
      .send({
        amount: 50,
        category: 'food',
        description: 'Lunch'
      })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(Number),
      amount: 50,
      category: 'food'
    });

    // Verify database state
    const total = await getTotalExpenses();
    expect(total).toBe(50);
  });
});
```

#### End-to-End Testing Approach

Test complete user workflows using tools like Playwright or Cypress:

```typescript
test('user can track expense from start to finish', async ({ page }) => {
  // Navigate to app
  await page.goto('/');

  // Add new expense
  await page.click('[data-testid="add-expense-btn"]');
  await page.fill('[data-testid="amount"]', '50.00');
  await page.selectOption('[data-testid="category"]', 'food');
  await page.fill('[data-testid="description"]', 'Lunch');
  await page.click('[data-testid="submit"]');

  // Verify expense appears in list
  await expect(page.locator('[data-testid="expense-item"]')).toContainText('Lunch');
  await expect(page.locator('[data-testid="total"]')).toContainText('$50.00');
});
```

### 2. Systematic Bug Analysis

Apply structured debugging methodology to identify and fix issues.

#### Five-Step Analysis Process

1. **Reproduction**: Reliably reproduce the bug
   - Document exact steps to trigger
   - Identify required environment/state
   - Note expected vs actual behavior

2. **Isolation**: Narrow down the problem
   - Binary search through code path
   - Create minimal reproduction case
   - Remove unrelated dependencies

3. **Root Cause Analysis**: Determine underlying cause
   - Trace execution flow
   - Check assumptions and preconditions
   - Review recent changes (git blame)

4. **Fix Implementation**: Implement solution
   - Write failing test first (TDD)
   - Implement the fix
   - Verify test passes

5. **Validation**: Ensure completeness
   - Run full test suite
   - Test edge cases
   - Verify no regressions

#### Common Bug Patterns

**Race Conditions:**
```typescript
// Test concurrent operations
test('handles concurrent updates correctly', async () => {
  const promises = Array.from({ length: 100 }, () =>
    incrementExpenseCount()
  );

  await Promise.all(promises);
  expect(getExpenseCount()).toBe(100);
});
```

**Null/Undefined Errors:**
```typescript
// Test null safety
test.each([null, undefined, '', 0, false])
  ('handles invalid input: %p', (input) => {
    expect(() => processExpense(input)).toThrow('Invalid expense');
  });
```

**Off-by-One Errors:**
```typescript
// Test boundaries explicitly
describe('pagination', () => {
  test('handles empty list', () => {
    expect(paginate([], 1, 10)).toEqual([]);
  });

  test('handles single item', () => {
    expect(paginate([item], 1, 10)).toEqual([item]);
  });

  test('handles last page with partial items', () => {
    const items = Array.from({ length: 25 }, (_, i) => i);
    expect(paginate(items, 3, 10)).toHaveLength(5);
  });
});
```

### 3. Identifying Potential Issues

Proactively identify issues before they become bugs.

#### Security Vulnerabilities

Test for common security issues:

```typescript
describe('security', () => {
  test('prevents SQL injection', async () => {
    const malicious = "'; DROP TABLE expenses; --";
    await expect(
      searchExpenses(malicious)
    ).resolves.not.toThrow();
  });

  test('sanitizes XSS in descriptions', () => {
    const xss = '<script>alert("xss")</script>';
    const expense = createExpense({ description: xss });
    expect(expense.description).not.toContain('<script>');
  });

  test('requires authentication for expense operations', async () => {
    await request(app)
      .post('/api/expenses')
      .send({ amount: 50 })
      .expect(401);
  });
});
```

#### Performance Issues

Test for performance problems:

```typescript
test('processes large expense list efficiently', () => {
  const largeList = Array.from({ length: 10000 }, (_, i) => ({
    amount: i,
    category: 'test'
  }));

  const start = performance.now();
  const total = calculateTotal(largeList);
  const duration = performance.now() - start;

  expect(duration).toBeLessThan(100); // Should complete in <100ms
  expect(total).toBe(49995000);
});
```

#### Logic Errors

Use parameterized tests to catch edge cases:

```typescript
test.each([
  // [input, expected, description]
  [[10, 20, 30], 60, 'normal positive values'],
  [[0, 0, 0], 0, 'all zeros'],
  [[-10, 20, -5], 5, 'mixed positive and negative'],
  [[0.1, 0.2], 0.3, 'decimal precision'],
  [[Number.MAX_SAFE_INTEGER], Number.MAX_SAFE_INTEGER, 'large numbers'],
])('calculateTotal(%p) = %p (%s)', (amounts, expected, description) => {
  const expenses = amounts.map(amount => ({ amount, category: 'test' }));
  expect(calculateTotal(expenses)).toBeCloseTo(expected);
});
```

### 4. Test Coverage Analysis

Use automated tools to identify gaps in test coverage.

#### Finding Untested Code

Run the provided script to identify source files without tests:

```bash
python3 scripts/find_untested_code.py src
```

The script will:
- Scan source directory for all code files
- Identify which files lack corresponding test files
- Categorize untested files by type (components, services, utils, etc.)
- Prioritize files that need testing most

**Interpretation:**
- **API/Services**: High priority - test business logic and data operations
- **Models**: High priority - test data validation and transformations
- **Hooks**: Medium priority - test stateful behavior
- **Components**: Medium priority - test complex UI logic
- **Utils**: Low priority - test as needed for complex functions

#### Analyzing Coverage Reports

Run the coverage analysis script after generating coverage:

```bash
# Generate coverage (using Jest example)
npm test -- --coverage

# Analyze coverage gaps
python3 scripts/analyze_coverage.py coverage/coverage-final.json
```

The script identifies:
- Files below coverage threshold (default 80%)
- Statement, branch, and function coverage percentages
- Priority files to improve

**Coverage targets:**
- Critical paths: 90%+ coverage
- Business logic: 85%+ coverage
- UI components: 75%+ coverage
- Utilities: 70%+ coverage

### 5. Test Maintenance and Quality

Ensure tests remain valuable and maintainable.

#### Test Code Quality Principles

**DRY (Don't Repeat Yourself):**
```typescript
// Extract common setup
function createTestExpense(overrides = {}) {
  return {
    amount: 50,
    category: 'food',
    description: 'Test expense',
    date: new Date('2024-01-01'),
    ...overrides
  };
}

test('filters by category', () => {
  const expenses = [
    createTestExpense({ category: 'food' }),
    createTestExpense({ category: 'transport' }),
  ];
  // ...
});
```

**Clear test data:**
```typescript
// Bad: Magic numbers
expect(calculateDiscount(100, 0.15)).toBe(85);

// Good: Named constants
const ORIGINAL_PRICE = 100;
const DISCOUNT_RATE = 0.15;
const EXPECTED_PRICE = 85;
expect(calculateDiscount(ORIGINAL_PRICE, DISCOUNT_RATE)).toBe(EXPECTED_PRICE);
```

**Avoid test interdependence:**
```typescript
// Bad: Tests depend on execution order
let sharedState;
test('test 1', () => {
  sharedState = { value: 1 };
});
test('test 2', () => {
  expect(sharedState.value).toBe(1); // Depends on test 1
});

// Good: Independent tests
test('test 1', () => {
  const state = { value: 1 };
  expect(state.value).toBe(1);
});
test('test 2', () => {
  const state = { value: 1 };
  expect(state.value).toBe(1);
});
```

## Workflow Decision Tree

Follow this decision tree to determine the testing approach:

1. **Adding new functionality?**
   - Yes → Write tests first (TDD)
     - Write failing test
     - Implement feature
     - Verify test passes
     - Refactor
   - No → Go to step 2

2. **Fixing a bug?**
   - Yes → Apply bug analysis process
     - Reproduce the bug
     - Write failing test demonstrating bug
     - Fix the implementation
     - Verify test passes
   - No → Go to step 3

3. **Improving test coverage?**
   - Yes → Use coverage tools
     - Run `find_untested_code.py` to identify gaps
     - Run `analyze_coverage.py` on coverage reports
     - Prioritize critical paths
     - Write tests for untested code
   - No → Go to step 4

4. **Analyzing code quality?**
   - Yes → Systematic review
     - Check for security vulnerabilities
     - Test edge cases and error handling
     - Verify performance characteristics
     - Review error handling

## Testing Frameworks and Tools

### Recommended Stack

**Unit/Integration Testing:**
- Jest or Vitest for test runner
- Testing Library for React components
- Supertest for API testing
- MSW (Mock Service Worker) for API mocking

**E2E Testing:**
- Playwright or Cypress
- Page Object Model pattern

**Coverage:**
- Istanbul (built into Jest/Vitest)
- Coverage reports in JSON format

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ExpenseCalculator.test.ts

# Run in watch mode
npm test -- --watch

# Run E2E tests
npm run test:e2e
```

## Reference Documentation

For detailed patterns and techniques, refer to:

- `references/testing_patterns.md` - Comprehensive testing patterns, best practices, and code examples
- `references/bug_analysis.md` - In-depth bug analysis framework, common bug patterns, and debugging techniques

These references contain extensive examples and advanced techniques. Load them when:
- Dealing with complex testing scenarios
- Need specific pattern implementations
- Debugging unusual issues
- Seeking best practices for specific situations

## Scripts

### analyze_coverage.py

Analyze Jest/Istanbul coverage reports to identify gaps:

```bash
python3 scripts/analyze_coverage.py [coverage-file]
```

Automatically finds common coverage file locations if not specified.

**Output:**
- Files below coverage threshold
- Statement, branch, and function coverage percentages
- Priority files to improve

### find_untested_code.py

Find source files without corresponding test files:

```bash
python3 scripts/find_untested_code.py [src-dir] [--pattern test|spec]
```

**Output:**
- Total source and test file counts
- Test file coverage percentage
- Untested files categorized by type (API, services, components, etc.)
- Recommendations for prioritization

## Best Practices Summary

1. **Write tests first** (TDD) when adding new features
2. **Test behavior, not implementation** - tests should survive refactoring
3. **Keep tests independent** - no shared state between tests
4. **Use descriptive names** - test names should explain the scenario
5. **Cover edge cases** - null, empty, boundary values, error conditions
6. **Mock external dependencies** - tests should be fast and reliable
7. **Maintain high coverage** - 80%+ for critical code
8. **Fix failing tests immediately** - never commit broken tests
9. **Refactor tests** - apply same quality standards as production code
10. **Use tools** - automate coverage analysis and gap identification
