# Testing Patterns and Best Practices

## Unit Testing Patterns

### AAA Pattern (Arrange-Act-Assert)
Structure tests in three clear phases:
- **Arrange**: Set up test data and dependencies
- **Act**: Execute the function/method being tested
- **Assert**: Verify the expected outcome

```typescript
test('calculateTotal adds items correctly', () => {
  // Arrange
  const items = [10, 20, 30];

  // Act
  const result = calculateTotal(items);

  // Assert
  expect(result).toBe(60);
});
```

### Test Doubles

#### Mocks
Use mocks to verify interactions and calls:
```typescript
const mockFn = jest.fn();
service.subscribe(mockFn);
service.notify('event');
expect(mockFn).toHaveBeenCalledWith('event');
```

#### Stubs
Use stubs to provide predetermined responses:
```typescript
const stub = jest.fn().mockReturnValue(42);
```

#### Spies
Use spies to track calls while preserving original implementation:
```typescript
const spy = jest.spyOn(object, 'method');
```

### Parameterized Tests
Test multiple scenarios efficiently:
```typescript
test.each([
  [1, 1, 2],
  [2, 3, 5],
  [10, -5, 5],
])('adds %i + %i to equal %i', (a, b, expected) => {
  expect(add(a, b)).toBe(expected);
});
```

## Integration Testing Patterns

### Test Database Setup
Use test-specific databases with proper setup/teardown:
```typescript
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
```

### API Testing Pattern
Test API endpoints with proper request/response validation:
```typescript
test('POST /users creates user', async () => {
  const response = await request(app)
    .post('/users')
    .send({ name: 'John', email: 'john@test.com' })
    .expect(201);

  expect(response.body).toMatchObject({
    id: expect.any(Number),
    name: 'John',
    email: 'john@test.com'
  });
});
```

## End-to-End Testing Patterns

### Page Object Model
Encapsulate page interactions:
```typescript
class LoginPage {
  async navigate() {
    await page.goto('/login');
  }

  async login(email: string, password: string) {
    await page.fill('[data-testid="email"]', email);
    await page.fill('[data-testid="password"]', password);
    await page.click('[data-testid="submit"]');
  }

  async getErrorMessage() {
    return page.textContent('[data-testid="error"]');
  }
}
```

### User Journey Testing
Test complete user workflows:
```typescript
test('user can complete purchase flow', async () => {
  await homePage.navigate();
  await homePage.searchProduct('laptop');
  await productPage.addToCart();
  await cartPage.proceedToCheckout();
  await checkoutPage.fillShippingInfo(testAddress);
  await checkoutPage.fillPaymentInfo(testCard);
  await checkoutPage.submitOrder();

  expect(await confirmationPage.getOrderNumber()).toBeTruthy();
});
```

## Test Coverage Strategies

### Coverage Targets
- **Statements**: 80%+ for critical paths
- **Branches**: 75%+ to ensure all conditionals tested
- **Functions**: 90%+ for public APIs
- **Lines**: 80%+ overall

### Critical Path Priority
1. Business-critical functionality (payment, auth, data integrity)
2. Complex logic with multiple branches
3. Bug-prone areas (identified from production issues)
4. Public APIs and interfaces
5. Edge cases and error handling

## Error and Edge Case Testing

### Boundary Testing
Test values at boundaries:
```typescript
describe('age validation', () => {
  test.each([
    [-1, false],
    [0, true],
    [17, false],
    [18, true],
    [120, true],
    [121, false],
  ])('validates age %i as %s', (age, expected) => {
    expect(isValidAge(age)).toBe(expected);
  });
});
```

### Error Handling
Test both success and failure paths:
```typescript
test('handles network errors gracefully', async () => {
  mockApi.get.mockRejectedValue(new Error('Network failure'));

  await expect(fetchData()).rejects.toThrow('Network failure');
  expect(logger.error).toHaveBeenCalled();
});
```

### Null/Undefined Testing
Test with missing or invalid data:
```typescript
test.each([null, undefined, '', {}, []])
  ('handles invalid input: %p', (input) => {
    expect(() => processData(input)).toThrow();
  });
```

## Async Testing Patterns

### Promise Testing
```typescript
test('async operation succeeds', async () => {
  await expect(fetchUser(1)).resolves.toMatchObject({
    id: 1,
    name: expect.any(String)
  });
});

test('async operation fails', async () => {
  await expect(fetchUser(-1)).rejects.toThrow('User not found');
});
```

### Timeout Handling
```typescript
test('operation completes within timeout', async () => {
  const start = Date.now();
  await performOperation();
  const duration = Date.now() - start;

  expect(duration).toBeLessThan(1000);
}, 5000); // 5 second test timeout
```

## Snapshot Testing

Use snapshots for UI components and data structures:
```typescript
test('renders correctly', () => {
  const tree = renderer.create(<Component prop="value" />).toJSON();
  expect(tree).toMatchSnapshot();
});
```

**When to use snapshots:**
- UI component rendering
- Large data structure validation
- API response format verification

**When to avoid snapshots:**
- Dynamic data (timestamps, IDs)
- Frequently changing structures
- When specific assertions are clearer

## Test Organization

### File Structure
```
src/
  components/
    Button.tsx
    Button.test.tsx
  services/
    api.ts
    api.test.ts
  __tests__/
    integration/
      user-flow.test.ts
    e2e/
      checkout.test.ts
```

### Test Naming
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    test('creates user with valid data', () => {});
    test('throws error when email is invalid', () => {});
    test('throws error when email already exists', () => {});
  });
});
```

## Performance Testing

### Benchmarking
```typescript
test('processes large dataset efficiently', () => {
  const largeArray = Array.from({ length: 10000 }, (_, i) => i);

  const start = performance.now();
  processArray(largeArray);
  const duration = performance.now() - start;

  expect(duration).toBeLessThan(100); // Should complete in <100ms
});
```

## Security Testing Patterns

### Input Validation
```typescript
test('prevents SQL injection', () => {
  const maliciousInput = "'; DROP TABLE users; --";
  expect(() => queryDatabase(maliciousInput)).not.toThrow();
  expect(database.getTables()).toContain('users');
});

test('prevents XSS attacks', () => {
  const maliciousScript = '<script>alert("XSS")</script>';
  const sanitized = sanitizeInput(maliciousScript);
  expect(sanitized).not.toContain('<script>');
});
```

### Authentication Testing
```typescript
test('requires authentication for protected routes', async () => {
  const response = await request(app)
    .get('/api/protected')
    .expect(401);
});

test('validates JWT tokens', async () => {
  const invalidToken = 'invalid.jwt.token';
  const response = await request(app)
    .get('/api/protected')
    .set('Authorization', `Bearer ${invalidToken}`)
    .expect(401);
});
```

## Common Anti-Patterns to Avoid

1. **Testing Implementation Details**: Test behavior, not internal implementation
2. **Fragile Tests**: Avoid tests that break with minor refactoring
3. **Test Interdependence**: Each test should be independent
4. **Excessive Mocking**: Don't mock everything; test real integrations when possible
5. **Long Tests**: Keep tests focused on a single behavior
6. **Magic Numbers**: Use named constants for test values
7. **Ignoring Test Failures**: Never commit with failing tests
8. **Testing Third-Party Code**: Focus on your code, not libraries
