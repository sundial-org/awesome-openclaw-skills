# Monarch Money API Reference

## Table of Contents

- [Authentication](#authentication)
- [Transactions API](#transactions-api)
- [Categories API](#categories-api)
- [Accounts API](#accounts-api)
- [GraphQL Direct Access](#graphql-direct-access)

## Authentication

The MonarchClient handles authentication automatically:

```typescript
import { MonarchClient } from 'monarch-money';

const client = new MonarchClient({
  baseURL: 'https://api.monarch.com',
  enablePersistentCache: false
});

await client.login({
  email: process.env.MONARCH_EMAIL,
  password: process.env.MONARCH_PASSWORD,
  mfaSecretKey: process.env.MONARCH_MFA_SECRET,
  useSavedSession: true,
  saveSession: true
});
```

### Session Management

Sessions are encrypted and stored at `~/.mm/session.json`. The `useSavedSession` option loads existing sessions, and `saveSession` persists new ones.

```typescript
// Load saved session
const loaded = client.loadSession();

// Delete session
client.deleteSession();

// Close client
await client.close();
```

## Transactions API

### Get Transactions

```typescript
const result = await client.transactions.getTransactions({
  limit: 50,
  startDate: '2026-01-01',
  endDate: '2026-01-31',
  verbosity: 'light'  // 'ultra-light' | 'light' | 'standard'
});

// result.transactions contains array of Transaction objects
```

### Transaction Object

```typescript
interface Transaction {
  id: string;
  amount: number;
  date: string;
  merchant: {
    id: string;
    name: string;
  };
  category: {
    id: string;
    name: string;
  };
  account: {
    id: string;
    displayName: string;
  };
  notes?: string;
  reviewStatus: 'needs_review' | 'reviewed';
  isPending: boolean;
}
```

### Update Transaction

```typescript
await client.transactions.updateTransaction(transactionId, {
  categoryId: 'new_category_id',
  notes: 'Updated notes',
  merchantName: 'New Merchant Name'
});
```

### Split Transaction

```typescript
const splits = [
  { amount: -20.00, categoryId: 'cat1', merchantName: 'Store', notes: 'Item 1' },
  { amount: -15.00, categoryId: 'cat2', merchantName: 'Store', notes: 'Item 2' }
];

await client.transactions.splitTransaction(transactionId, splits);
```

## Categories API

### Get All Categories

```typescript
const categories = await client.categories.getCategories();

// categories is array of Category objects
```

### Category Object

```typescript
interface Category {
  id: string;
  name: string;
  group: {
    id: string;
    name: string;
    type: 'income' | 'expense' | 'transfer';
  };
  icon?: string;
}
```

### Common Category IDs

Categories vary by user account. Use the CLI to get your specific IDs:

```bash
monarch-money cat list --show-ids
```

## Accounts API

### Get All Accounts

```typescript
const accounts = await client.accounts.getAll({
  includeHidden: false,
  verbosity: 'light'
});
```

### Account Object

```typescript
interface Account {
  id: string;
  displayName: string;
  currentBalance: number;
  type: string;
  subtype: string;
  institution: {
    id: string;
    name: string;
  };
  isHidden: boolean;
}
```

## GraphQL Direct Access

For advanced use cases, access the GraphQL client directly:

```typescript
// Query
const result = await client['graphql'].query(queryString, variables);

// Mutation
const result = await client['graphql'].mutation(mutationString, variables);
```

### Example: Custom Query

```typescript
const query = `
  query GetTransactionDetails($id: UUID!) {
    getTransaction(id: $id) {
      id
      amount
      date
      merchant { name }
      category { name }
      notes
    }
  }
`;

const result = await client['graphql'].query(query, { id: transactionId });
```

### Working Mutations

**Update Transaction:**
```graphql
mutation UpdateTransaction($input: UpdateTransactionInput!) {
  updateTransaction(input: $input) {
    transaction { id }
    errors { message }
  }
}
```

**Split Transaction:**
```graphql
mutation SplitTransaction($input: UpdateTransactionSplitInput!) {
  updateTransactionSplit(input: $input) {
    transaction { id }
    errors { message }
  }
}
```

## Verbosity Levels

Control response detail with verbosity:

| Level | Use Case | Data Included |
|-------|----------|---------------|
| `ultra-light` | Quick overviews | IDs, amounts, names only |
| `light` | Standard display | Core fields + dates + categories |
| `standard` | Full analysis | All fields including metadata |

```typescript
const accounts = await client.accounts.getAll({ verbosity: 'ultra-light' });
// Returns minimal data for fast processing
```

## Rate Limiting

The client includes built-in rate limiting. Default settings:

- 10 requests per second
- 20 burst size

Configure in client options:

```typescript
const client = new MonarchClient({
  baseURL: 'https://api.monarch.com',
  rateLimit: {
    requestsPerSecond: 5,
    burstSize: 10
  }
});
```

## Caching

Two levels of caching available:

**Memory Cache:** In-session caching (default enabled)
**Persistent Cache:** Cross-session caching (optional)

```typescript
const client = new MonarchClient({
  baseURL: 'https://api.monarch.com',
  cache: {
    enabled: true,
    ttl: 300000  // 5 minutes
  },
  enablePersistentCache: true
});
```
