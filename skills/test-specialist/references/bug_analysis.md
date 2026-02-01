# Bug Analysis and Debugging Framework

## Systematic Bug Analysis Approach

### 1. Reproduction
First, reliably reproduce the bug:
- Identify exact steps to trigger the issue
- Determine required environment/state
- Document inputs that cause the failure
- Note expected vs actual behavior

### 2. Isolation
Narrow down the problem:
- Binary search through the code path
- Remove unrelated code/dependencies
- Create minimal reproduction case
- Identify the smallest failing unit

### 3. Root Cause Analysis
Determine the underlying cause:
- Trace execution flow
- Check assumptions and preconditions
- Review recent changes (git blame, git log)
- Look for similar patterns in codebase

### 4. Fix Implementation
Implement the solution:
- Write a failing test first
- Implement the fix
- Verify test passes
- Check for similar issues elsewhere

### 5. Validation
Ensure the fix is complete:
- Run full test suite
- Test edge cases
- Verify no regressions
- Update documentation if needed

## Bug Categories and Detection

### Logic Errors

**Symptoms:**
- Incorrect calculations
- Wrong conditional branches taken
- Unexpected state transitions
- Data corruption

**Detection Strategies:**
```typescript
// Add assertions to verify invariants
function transfer(from: Account, to: Account, amount: number) {
  const beforeTotal = from.balance + to.balance;

  from.balance -= amount;
  to.balance += amount;

  const afterTotal = from.balance + to.balance;
  console.assert(beforeTotal === afterTotal, 'Balance mismatch');
}

// Unit tests for all branches
test.each([
  [100, 50, true],   // Normal case
  [100, 100, true],  // Exact balance
  [100, 101, false], // Insufficient funds
  [100, 0, false],   // Zero amount
  [100, -50, false], // Negative amount
])('transfer validation', (balance, amount, shouldSucceed) => {
  // Test implementation
});
```

### Race Conditions

**Symptoms:**
- Intermittent failures
- Tests pass/fail randomly
- Different behavior in production vs development
- Issues under load

**Detection Strategies:**
```typescript
// Test concurrent operations
test('handles concurrent updates correctly', async () => {
  const promises = Array.from({ length: 100 }, () =>
    incrementCounter()
  );

  await Promise.all(promises);
  expect(getCounter()).toBe(100);
});

// Add delays to expose timing issues
test('handles async race condition', async () => {
  const result1 = fetchData();
  await new Promise(resolve => setTimeout(resolve, 10));
  const result2 = fetchData();

  await expect(Promise.all([result1, result2])).resolves.toBeTruthy();
});
```

### Memory Leaks

**Symptoms:**
- Increasing memory usage over time
- Application slowdown
- Out of memory errors
- Event listeners not cleaned up

**Detection Strategies:**
```typescript
// Test for cleanup
test('cleans up event listeners', () => {
  const component = new Component();
  const listenerCount = getEventListenerCount();

  component.mount();
  expect(getEventListenerCount()).toBeGreaterThan(listenerCount);

  component.unmount();
  expect(getEventListenerCount()).toBe(listenerCount);
});

// Monitor memory in long-running tests
test('does not leak memory', async () => {
  const initialMemory = process.memoryUsage().heapUsed;

  for (let i = 0; i < 1000; i++) {
    await performOperation();
  }

  // Force garbage collection if available
  if (global.gc) global.gc();

  const finalMemory = process.memoryUsage().heapUsed;
  const growth = finalMemory - initialMemory;

  // Allow some growth but not linear with iterations
  expect(growth).toBeLessThan(10 * 1024 * 1024); // 10MB threshold
});
```

### Off-by-One Errors

**Symptoms:**
- Array index out of bounds
- Loop iterations incorrect
- Boundary values handled wrong

**Detection Strategies:**
```typescript
// Test boundary conditions explicitly
describe('array operations', () => {
  test('handles empty array', () => {
    expect(processArray([])).toEqual([]);
  });

  test('handles single element', () => {
    expect(processArray([1])).toEqual([1]);
  });

  test('handles first element', () => {
    const result = processArray([1, 2, 3]);
    expect(result[0]).toBe(1);
  });

  test('handles last element', () => {
    const result = processArray([1, 2, 3]);
    expect(result[result.length - 1]).toBe(3);
  });
});
```

### Null/Undefined Reference Errors

**Symptoms:**
- Cannot read property of undefined
- Null reference exceptions
- Type errors at runtime

**Detection Strategies:**
```typescript
// Test with missing/null/undefined values
describe('null safety', () => {
  test.each([
    [null, 'handles null'],
    [undefined, 'handles undefined'],
    ['', 'handles empty string'],
    [0, 'handles zero'],
    [false, 'handles false'],
  ])('safely handles %p', (input, description) => {
    expect(() => processInput(input)).not.toThrow();
  });

  // Use optional chaining and nullish coalescing
  const value = obj?.nested?.property ?? defaultValue;
});

// Enable strict null checks in TypeScript
// tsconfig.json: "strictNullChecks": true
```

### API Integration Errors

**Symptoms:**
- Unexpected response formats
- Network timeouts
- Authentication failures
- Rate limiting issues

**Detection Strategies:**
```typescript
// Test error responses
test('handles API errors', async () => {
  mockApi.get.mockRejectedValue({
    status: 500,
    message: 'Internal Server Error'
  });

  await expect(fetchData()).rejects.toThrow('Internal Server Error');
  expect(errorHandler).toHaveBeenCalled();
});

// Test timeout scenarios
test('handles timeout', async () => {
  jest.useFakeTimers();

  const promise = fetchWithTimeout('https://api.example.com', 5000);

  jest.advanceTimersByTime(6000);

  await expect(promise).rejects.toThrow('Timeout');

  jest.useRealTimers();
});

// Test malformed responses
test('handles invalid JSON', async () => {
  mockApi.get.mockResolvedValue('invalid json{');

  await expect(fetchData()).rejects.toThrow();
});
```

### State Management Bugs

**Symptoms:**
- Stale data displayed
- State updates not reflected
- Inconsistent UI state
- Lost updates

**Detection Strategies:**
```typescript
// Test state transitions
describe('state machine', () => {
  test('transitions from idle to loading', () => {
    const state = { status: 'idle' };
    const newState = transition(state, 'FETCH');
    expect(newState.status).toBe('loading');
  });

  test('prevents invalid transitions', () => {
    const state = { status: 'idle' };
    expect(() => transition(state, 'COMPLETE')).toThrow();
  });
});

// Test state consistency
test('maintains state consistency', async () => {
  const store = createStore();

  const action1 = store.dispatch(updateUser({ name: 'Alice' }));
  const action2 = store.dispatch(updateUser({ name: 'Bob' }));

  await Promise.all([action1, action2]);

  const state = store.getState();
  expect(['Alice', 'Bob']).toContain(state.user.name);
});
```

### Performance Bugs

**Symptoms:**
- Slow response times
- UI freezing/blocking
- High CPU/memory usage
- Inefficient algorithms

**Detection Strategies:**
```typescript
// Benchmark performance
test('performs efficiently with large datasets', () => {
  const largeDataset = generateData(10000);

  const start = performance.now();
  const result = processData(largeDataset);
  const duration = performance.now() - start;

  expect(duration).toBeLessThan(100); // 100ms threshold
  expect(result.length).toBe(10000);
});

// Test for N+1 queries
test('avoids N+1 database queries', async () => {
  const queryCounter = createQueryCounter();

  await fetchUsersWithPosts(100);

  // Should use JOIN, not individual queries per user
  expect(queryCounter.count).toBeLessThan(5);
});

// Monitor re-renders
test('minimizes unnecessary re-renders', () => {
  const renderSpy = jest.fn();
  const { rerender } = render(<Component onRender={renderSpy} />);

  rerender(<Component onRender={renderSpy} />);

  expect(renderSpy).toHaveBeenCalledTimes(1); // No props changed
});
```

### Security Vulnerabilities

**Symptoms:**
- Unauthorized access
- Data leaks
- Injection attacks possible
- Improper input validation

**Detection Strategies:**
```typescript
// Test authentication/authorization
test('prevents unauthorized access', async () => {
  const response = await request(app)
    .get('/api/admin/users')
    .set('Authorization', 'Bearer user-token')
    .expect(403);
});

// Test input sanitization
test('sanitizes user input', () => {
  const maliciousInputs = [
    '<script>alert("xss")</script>',
    '"; DROP TABLE users; --',
    '../../../etc/passwd',
    '${process.env.SECRET}',
  ];

  maliciousInputs.forEach(input => {
    const sanitized = sanitizeInput(input);
    expect(sanitized).not.toContain('<script>');
    expect(sanitized).not.toContain('DROP TABLE');
    expect(sanitized).not.toContain('../');
  });
});

// Test CSRF protection
test('requires CSRF token', async () => {
  await request(app)
    .post('/api/transfer')
    .send({ amount: 1000 })
    .expect(403);

  await request(app)
    .post('/api/transfer')
    .set('X-CSRF-Token', validToken)
    .send({ amount: 1000 })
    .expect(200);
});
```

## Debugging Techniques

### Console Debugging
```typescript
// Strategic logging
function complexCalculation(data: Data[]) {
  console.log('Input:', data);

  const filtered = data.filter(item => item.active);
  console.log('After filter:', filtered);

  const mapped = filtered.map(transform);
  console.log('After transform:', mapped);

  return mapped;
}

// Use debug library for conditional logging
import debug from 'debug';
const log = debug('app:module');

log('Processing %d items', items.length);
```

### Test-Driven Debugging
```typescript
// 1. Write a test that reproduces the bug
test('bug: incorrect total with negative values', () => {
  const items = [10, -5, 20];
  const result = calculateTotal(items);
  expect(result).toBe(25); // This will fail
});

// 2. Fix the implementation
// 3. Verify the test passes
// 4. Add more edge cases
```

### Binary Search Debugging
```typescript
// Isolate the problem by commenting out sections
function problematicFunction(data: any) {
  const step1 = processStep1(data);
  console.log('Step 1 OK'); // Check if we reach here

  const step2 = processStep2(step1);
  console.log('Step 2 OK'); // Problem occurs before this?

  const step3 = processStep3(step2);
  console.log('Step 3 OK');

  return step3;
}
```

### Differential Testing
```typescript
// Compare old vs new implementation
test('new implementation matches old behavior', () => {
  const inputs = generateTestCases(100);

  inputs.forEach(input => {
    const oldResult = oldImplementation(input);
    const newResult = newImplementation(input);

    expect(newResult).toEqual(oldResult);
  });
});
```

## Prevention Strategies

### Defensive Programming
```typescript
// Validate inputs
function divide(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new TypeError('Arguments must be numbers');
  }

  if (b === 0) {
    throw new Error('Division by zero');
  }

  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    throw new Error('Arguments must be finite');
  }

  return a / b;
}

// Use TypeScript strict mode
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Code Review Checklist
- [ ] All edge cases handled?
- [ ] Error handling in place?
- [ ] Input validation implemented?
- [ ] Tests cover new code?
- [ ] No obvious performance issues?
- [ ] Security considerations addressed?
- [ ] Documentation updated?
- [ ] No console.log statements left?

### Static Analysis
```json
// ESLint configuration
{
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn",
    "eqeqeq": "error",
    "no-eval": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

## Common Bug Patterns

### Pattern 1: Async/Await Mistakes
```typescript
// ❌ Wrong: Not awaiting properly
async function wrong() {
  const result = fetch('/api'); // Missing await
  return result.data; // Will fail
}

// ✅ Correct
async function correct() {
  const result = await fetch('/api');
  return result.data;
}

// ❌ Wrong: Not handling errors
async function noErrorHandling() {
  const data = await fetch('/api'); // Throws on error
  return data;
}

// ✅ Correct
async function withErrorHandling() {
  try {
    const data = await fetch('/api');
    return data;
  } catch (error) {
    logger.error(error);
    throw new Error('Failed to fetch data');
  }
}
```

### Pattern 2: Closure Issues
```typescript
// ❌ Wrong: Stale closure
function createHandlers() {
  let count = 0;
  const handlers = [];

  for (var i = 0; i < 3; i++) {
    handlers.push(() => console.log(i)); // All will log 3
  }

  return handlers;
}

// ✅ Correct
function createHandlersFixed() {
  const handlers = [];

  for (let i = 0; i < 3; i++) { // Use let instead of var
    handlers.push(() => console.log(i));
  }

  return handlers;
}
```

### Pattern 3: Mutation Issues
```typescript
// ❌ Wrong: Mutating input
function sortItems(items: Item[]) {
  return items.sort((a, b) => a.value - b.value); // Mutates original
}

// ✅ Correct
function sortItemsFixed(items: Item[]) {
  return [...items].sort((a, b) => a.value - b.value);
}
```

### Pattern 4: Floating Point Precision
```typescript
// ❌ Wrong: Direct float comparison
test('adds decimals', () => {
  expect(0.1 + 0.2).toBe(0.3); // Fails!
});

// ✅ Correct
test('adds decimals', () => {
  expect(0.1 + 0.2).toBeCloseTo(0.3);
});
```
