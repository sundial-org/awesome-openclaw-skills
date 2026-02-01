# Code Comments Guide

This document provides examples and patterns for writing effective inline documentation that helps new developers understand code quickly.

## Core Principles

1. **Explain "Why" not "What"** - The code shows what it does; comments should explain why it exists
2. **Provide Context** - Help readers understand the bigger picture
3. **Document Edge Cases** - Explain non-obvious behavior and special handling
4. **Include Examples** - Show how to use complex functions
5. **Keep Comments Current** - Update comments when code changes

## Function/Method Documentation

### JavaScript/TypeScript (JSDoc)

```javascript
/**
 * Calculates the prorated subscription cost for a partial billing period.
 *
 * Why this exists: Users can subscribe mid-month, so we need to charge
 * them only for the days remaining in the current billing cycle.
 *
 * @param {number} fullPrice - The normal monthly subscription price
 * @param {Date} startDate - When the user's subscription begins
 * @param {Date} periodEnd - End of the current billing period
 * @returns {number} The prorated amount to charge
 *
 * @example
 * // User subscribes on Jan 15, period ends Jan 31
 * calculateProratedCost(30, new Date('2024-01-15'), new Date('2024-01-31'))
 * // Returns: 16.13 (17 days out of 31 days * $30)
 *
 * @throws {Error} If startDate is after periodEnd
 */
function calculateProratedCost(fullPrice, startDate, periodEnd) {
  if (startDate > periodEnd) {
    throw new Error('Start date must be before period end');
  }

  const daysInPeriod = (periodEnd - startDate) / (1000 * 60 * 60 * 24);
  const daysInMonth = new Date(periodEnd.getYear(), periodEnd.getMonth() + 1, 0).getDate();

  return (fullPrice / daysInMonth) * daysInPeriod;
}
```

### Python (Docstring)

```python
def calculate_prorated_cost(full_price: float, start_date: datetime, period_end: datetime) -> float:
    """
    Calculates the prorated subscription cost for a partial billing period.

    Why this exists: Users can subscribe mid-month, so we need to charge
    them only for the days remaining in the current billing cycle.

    Args:
        full_price: The normal monthly subscription price
        start_date: When the user's subscription begins
        period_end: End of the current billing period

    Returns:
        The prorated amount to charge

    Raises:
        ValueError: If start_date is after period_end

    Example:
        >>> # User subscribes on Jan 15, period ends Jan 31
        >>> calculate_prorated_cost(30, date(2024, 1, 15), date(2024, 1, 31))
        16.13  # 17 days out of 31 days * $30
    """
    if start_date > period_end:
        raise ValueError('Start date must be before period end')

    days_in_period = (period_end - start_date).days
    days_in_month = monthrange(period_end.year, period_end.month)[1]

    return (full_price / days_in_month) * days_in_period
```

### Java (JavaDoc)

```java
/**
 * Calculates the prorated subscription cost for a partial billing period.
 *
 * <p>Why this exists: Users can subscribe mid-month, so we need to charge
 * them only for the days remaining in the current billing cycle.</p>
 *
 * @param fullPrice The normal monthly subscription price
 * @param startDate When the user's subscription begins
 * @param periodEnd End of the current billing period
 * @return The prorated amount to charge
 * @throws IllegalArgumentException if startDate is after periodEnd
 *
 * <p>Example:
 * <pre>
 * // User subscribes on Jan 15, period ends Jan 31
 * double cost = calculateProratedCost(30.0,
 *     LocalDate.of(2024, 1, 15),
 *     LocalDate.of(2024, 1, 31));
 * // Returns: 16.13 (17 days out of 31 days * $30)
 * </pre>
 */
public double calculateProratedCost(double fullPrice, LocalDate startDate, LocalDate periodEnd) {
    if (startDate.isAfter(periodEnd)) {
        throw new IllegalArgumentException("Start date must be before period end");
    }

    long daysInPeriod = ChronoUnit.DAYS.between(startDate, periodEnd);
    int daysInMonth = periodEnd.lengthOfMonth();

    return (fullPrice / daysInMonth) * daysInPeriod;
}
```

## Complex Logic Documentation

### Documenting Business Rules

```javascript
// Why we check status in this specific order:
// 1. "cancelled" takes precedence because users might cancel during trial
// 2. "trial" is checked next so we can show trial-specific messaging
// 3. "active" is the default state for paying customers
// This ordering prevents edge cases like showing "active" status to
// cancelled trial users.

if (subscription.status === 'cancelled') {
  return <CancelledMessage />;
} else if (subscription.status === 'trial') {
  return <TrialMessage daysRemaining={subscription.trialDaysLeft} />;
} else if (subscription.status === 'active') {
  return <ActiveMessage />;
}
```

### Documenting Edge Cases

```python
# Why this check exists: The API returns None for deleted users,
# but empty string for users who never set a name. We need to
# distinguish between these cases for the audit log.
if user_name is None:
    # User was deleted - log this as a security event
    log_deletion_event(user_id, timestamp=datetime.now())
elif user_name == "":
    # User never completed onboarding - safe to skip
    continue
else:
    # Normal case - process the user
    process_user(user_id, user_name)
```

### Documenting Performance Considerations

```javascript
// Performance note: We use a Set here instead of an Array because
// we frequently check if user IDs exist (O(1) lookup vs O(n)).
// With 10,000+ users, this saves ~500ms per request.
const activeUserIds = new Set(users.map(u => u.id));

// Avoid: const activeUserIds = users.map(u => u.id); // O(n) lookups
if (activeUserIds.has(currentUserId)) {
  // User is active
}
```

### Documenting Workarounds and Gotchas

```python
# GOTCHA: The third-party API returns timestamps in Unix milliseconds,
# but Python's datetime expects seconds. We must divide by 1000.
# Bug reported upstream: https://github.com/vendor/lib/issues/123
timestamp = datetime.fromtimestamp(api_response['created_at'] / 1000)
```

```javascript
// WORKAROUND: Safari doesn't support lookbehind regex, so we use
// a more verbose approach here. Can simplify once we drop Safari 15 support.
// TODO: Replace with lookbehind regex when Safari 15+ usage drops below 1%
// Original regex: /(?<=@)\w+/g
const mentions = text.split('@').slice(1).map(part => part.split(/\s/)[0]);
```

## Class Documentation

### TypeScript Class

```typescript
/**
 * Manages user authentication state and provides methods for login/logout.
 *
 * Why this exists: We need centralized auth state management that works
 * across multiple components and persists across page refreshes.
 *
 * Usage:
 * ```typescript
 * const auth = new AuthManager();
 *
 * // Log in user
 * await auth.login('user@example.com', 'password');
 *
 * // Check if user is authenticated
 * if (auth.isAuthenticated()) {
 *   // Show authenticated content
 * }
 *
 * // Get current user
 * const user = auth.getCurrentUser();
 * ```
 */
class AuthManager {
  private token: string | null = null;
  private user: User | null = null;

  /**
   * Authenticates a user with email and password.
   *
   * Why async: Makes API call to backend for authentication.
   * Side effects: Stores token in localStorage and updates internal state.
   *
   * @throws {AuthenticationError} If credentials are invalid
   */
  async login(email: string, password: string): Promise<User> {
    // Implementation
  }

  /**
   * Checks if a user is currently authenticated.
   *
   * Note: Performs local check only; doesn't verify token with backend.
   * Use refreshToken() if you need to verify token is still valid.
   */
  isAuthenticated(): boolean {
    return this.token !== null && !this.isTokenExpired();
  }

  /**
   * Checks if the current token has expired.
   *
   * Implementation note: Tokens expire 24 hours after issue.
   * We check 5 minutes before actual expiry to avoid edge cases.
   */
  private isTokenExpired(): boolean {
    // Implementation
  }
}
```

## Algorithm Documentation

### Complex Algorithm

```python
def find_shortest_path(graph, start, end):
    """
    Finds the shortest path between two nodes using Dijkstra's algorithm.

    Why we chose Dijkstra: We have a weighted graph with non-negative weights.
    If we had negative weights, we'd need Bellman-Ford instead.

    Time Complexity: O((V + E) log V) where V = vertices, E = edges
    Space Complexity: O(V) for storing distances and visited nodes

    Algorithm overview:
    1. Initialize distances to all nodes as infinity, except start (0)
    2. Use priority queue to always process closest unvisited node
    3. For each neighbor, check if we found a shorter path
    4. Continue until we reach the end node or exhaust all paths

    Args:
        graph: Adjacency list representation {node: [(neighbor, weight), ...]}
        start: Starting node
        end: Destination node

    Returns:
        List of nodes representing shortest path, or None if no path exists

    Example:
        >>> graph = {
        ...     'A': [('B', 4), ('C', 2)],
        ...     'B': [('D', 3)],
        ...     'C': [('B', 1), ('D', 5)],
        ...     'D': []
        ... }
        >>> find_shortest_path(graph, 'A', 'D')
        ['A', 'C', 'B', 'D']  # Cost: 6 (A->C: 2, C->B: 1, B->D: 3)
    """
    # Priority queue: [(distance, node, path)]
    # We store the full path to reconstruct it at the end
    queue = [(0, start, [start])]
    visited = set()

    while queue:
        # Pop node with smallest distance (priority queue property)
        distance, node, path = heapq.heappop(queue)

        # Skip if we've already processed this node
        # Important: Prevents infinite loops in cyclic graphs
        if node in visited:
            continue

        visited.add(node)

        # Success case: we reached the destination
        if node == end:
            return path

        # Explore neighbors
        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                # Calculate distance to neighbor through current path
                new_distance = distance + weight
                new_path = path + [neighbor]
                heapq.heappush(queue, (new_distance, neighbor, new_path))

    # No path exists between start and end
    return None
```

## API Integration Documentation

```javascript
/**
 * Fetches user data from the legacy API with proper error handling.
 *
 * API Quirks to be aware of:
 * 1. Returns 200 with error object instead of proper status codes
 * 2. Rate limit is 100 req/min but not documented in headers
 * 3. User IDs are strings, not numbers (despite API docs saying otherwise)
 * 4. Deleted users return {deleted: true} instead of 404
 *
 * Related Jira tickets:
 * - API-123: Rate limit enhancement request
 * - API-456: Proper status codes migration (planned for Q2)
 *
 * @param {string} userId - User ID as string (e.g., "usr_123abc")
 * @returns {Promise<User|null>} User object or null if deleted
 * @throws {APIError} If API is unavailable or rate limited
 */
async function fetchUserFromLegacyAPI(userId) {
  try {
    const response = await fetch(`https://legacy-api.example.com/users/${userId}`);

    // Check for pseudo-error responses (API returns 200 with error object)
    if (response.ok) {
      const data = await response.json();

      // Check for API's custom error format
      if (data.error) {
        throw new APIError(data.error.message, data.error.code);
      }

      // Check for deleted user (API quirk #4)
      if (data.deleted === true) {
        return null;
      }

      return data;
    }

    throw new APIError(`API returned ${response.status}`, response.status);
  } catch (error) {
    // Add context to help with debugging
    throw new APIError(`Failed to fetch user ${userId}: ${error.message}`);
  }
}
```

## Configuration Documentation

```typescript
// Database connection configuration
//
// Pool size tuning: After load testing, we found:
// - 10 connections: good for < 100 concurrent users
// - 20 connections: good for 100-500 concurrent users
// - 50 connections: good for 500-2000 concurrent users
// - Beyond 2000: consider read replicas
//
// Current setting (20) is sized for our typical load of ~300 concurrent users
// Last updated: 2024-01-15 after Q4 traffic analysis
const dbConfig = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,

  // Connection pooling
  max: 20,  // Maximum number of connections in pool
  min: 5,   // Minimum number of connections (always maintained)

  // Timeout settings
  // - connectionTimeoutMillis: How long to wait for a connection from pool
  // - idleTimeoutMillis: How long a connection can sit idle before being closed
  // - query_timeout: PostgreSQL-specific timeout for long-running queries
  connectionTimeoutMillis: 5000,   // Fail fast if pool is exhausted
  idleTimeoutMillis: 30000,        // Close idle connections after 30s
  query_timeout: 60000,            // Kill queries running longer than 60s
};
```

## TODO Comments

Use TODO comments effectively:

```javascript
// TODO(username, 2024-01-15): Implement caching for this endpoint
// Why: API call takes 500ms, users report slowness
// Impact: High - affects all list views
// Complexity: Medium - need to handle cache invalidation
// Ticket: PERF-123
async function getUserList() {
  return await api.get('/users');
}

// TODO(username): Refactor to use new auth system
// Blocked by: AUTH-456 (auth system migration)
// Can remove after: All clients migrate to v2 API
function legacyAuthCheck(token) {
  // Old auth logic
}

// FIXME(username): This breaks when month has 31 days
// Bug report: BUG-789
// Workaround: Validate date before passing to this function
function calculateEndDate(startDay, daysToAdd) {
  return startDay + daysToAdd; // Simplified example
}

// HACK(username): Temporary workaround for Safari bug
// Remove when: Safari 16 usage drops below 5%
// Tracking: https://bugs.webkit.org/show_bug.cgi?id=12345
if (isSafari()) {
  // Workaround code
}
```

## When NOT to Write Comments

### Don't Explain Obvious Code

```javascript
// ❌ BAD: Comment explains what code obviously does
// Increment counter by 1
counter++;

// ✅ GOOD: No comment needed, code is self-explanatory
counter++;
```

### Don't Describe Implementation That's Clear

```javascript
// ❌ BAD: Describes obvious loop logic
// Loop through all users and find the one with matching ID
const user = users.find(u => u.id === userId);

// ✅ GOOD: No comment needed, code is clear
const user = users.find(u => u.id === userId);
```

### Don't Leave Commented-Out Code

```javascript
// ❌ BAD: Leaving old code as comments
function calculateTotal(items) {
  // return items.reduce((sum, item) => sum + item.price, 0);
  // return items.map(i => i.price).reduce((a, b) => a + b);
  return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

// ✅ GOOD: Delete old code, use version control instead
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}
```

## Summary

**Good comments:**
- Explain WHY, not WHAT
- Provide context and business logic
- Document edge cases and gotchas
- Include examples for complex functions
- Note performance considerations
- Explain workarounds with links to issues

**Avoid:**
- Describing obvious code
- Leaving commented-out code
- Outdated information
- Redundant descriptions
- Comments that duplicate code
