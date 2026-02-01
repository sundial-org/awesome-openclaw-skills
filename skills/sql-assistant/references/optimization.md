# SQL Query Optimization Guide

Strategies and techniques for improving SQL query performance.

---

## 1. Indexing Fundamentals

### What is an Index?

An index is a data structure (usually B-tree) that improves the speed of data retrieval operations on a database table at the cost of additional writes and storage space.

### When to Create Indexes

**Create indexes on:**
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY
- Columns used in GROUP BY
- Foreign key columns

**Avoid indexes on:**
- Tables with frequent INSERT/UPDATE/DELETE operations
- Columns with low cardinality (few unique values)
- Tables that are very small
- Columns that are rarely queried

### Index Types

```sql
-- Single-column index
CREATE INDEX idx_user_email ON users(email);

-- Multi-column (composite) index
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Unique index (enforces uniqueness)
CREATE UNIQUE INDEX idx_unique_email ON users(email);

-- Partial index (index only rows meeting condition)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Expression index (index computed value)
CREATE INDEX idx_lower_email ON users(LOWER(email));
```

### Index Column Order Matters

For composite indexes, the order of columns is crucial:

```sql
-- Good for queries with user_id AND order_date
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Efficient: Uses the index
SELECT * FROM orders WHERE user_id = 1 AND order_date > '2024-01-01';

-- Efficient: Uses the index (user_id is first column)
SELECT * FROM orders WHERE user_id = 1;

-- Not efficient: Cannot use index (order_date is not first)
SELECT * FROM orders WHERE order_date > '2024-01-01';

-- Efficient: Uses the index for sorting
SELECT * FROM orders WHERE user_id = 1 ORDER BY order_date;
```

### Covering Indexes

A covering index includes all columns needed for a query, avoiding table lookups:

```sql
-- Query
SELECT user_id, order_date, total FROM orders
WHERE user_id = 1;

-- Covering index (includes all columns in SELECT)
CREATE INDEX idx_covering ON orders(user_id, order_date, total);
```

---

## 2. Query Rewrite Techniques

### Use EXISTS Instead of IN

```sql
-- Less efficient (scans subquery for each row)
SELECT * FROM users u
WHERE u.id IN (SELECT user_id FROM orders);

-- More efficient (stops at first match)
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

### Use JOIN Instead of Subquery in FROM

```sql
-- Less efficient (creates temporary table)
SELECT * FROM (
    SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id
) AS o JOIN users u ON o.user_id = u.id;

-- More efficient (direct join)
SELECT u.*, COUNT(o.id) as cnt
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

### Avoid SELECT *

```sql
-- Less efficient (reads all columns)
SELECT * FROM users WHERE id = 1;

-- More efficient (reads only needed columns)
SELECT id, name, email FROM users WHERE id = 1;
```

### Use LIMIT to Reduce Result Set

```sql
-- Without limit (returns all rows)
SELECT * FROM logs ORDER BY timestamp DESC;

-- With limit (returns only first 1000)
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 1000;
```

### Use UNION ALL Instead of UNION

```sql
-- UNION eliminates duplicates (slower)
SELECT name FROM users_a
UNION
SELECT name FROM users_b;

-- UNION ALL keeps duplicates (faster)
SELECT name FROM users_a
UNION ALL
SELECT name FROM users_b;
```

### Use Wildcards Carefully

```sql
-- Less efficient (full scan)
SELECT * FROM users WHERE name LIKE '%John%';

-- More efficient (uses index)
SELECT * FROM users WHERE name LIKE 'John%';
```

---

## 3. JOIN Optimization

### Use INNER JOIN When Possible

```sql
-- INNER JOIN is typically faster than LEFT JOIN
SELECT * FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

### Join Order

Join smaller tables first:

```sql
-- Join smaller table (categories) first
SELECT * FROM categories c
JOIN products p ON c.id = p.category_id
JOIN orders o ON p.id = o.product_id;
```

### Use Appropriate Join Type

- **INNER JOIN**: Only matching rows
- **LEFT JOIN**: All rows from left table, matching from right
- **RIGHT JOIN**: All rows from right table, matching from left
- **FULL OUTER JOIN**: All rows from both tables

Choose the join type that best matches your query requirements.

---

## 4. Subquery Optimization

### Use CTEs for Complex Subqueries

```sql
-- Clearer and often optimized better
WITH user_orders AS (
    SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id
)
SELECT u.name, uo.cnt
FROM users u
JOIN user_orders uo ON u.id = uo.user_id;
```

### Correlated Subqueries Can Be Slow

```sql
-- Less efficient (executes subquery for each row)
SELECT u.name,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as cnt
FROM users u;

-- More efficient (single query with JOIN)
SELECT u.name, COUNT(o.id) as cnt
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

---

## 5. Aggregation Optimization

### Filter Before Aggregating

```sql
-- Less efficient (aggregates all rows, then filters)
SELECT user_id, COUNT(*)
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 10;

-- More efficient (filters first, then aggregates)
SELECT user_id, COUNT(*)
FROM orders
WHERE user_id IN (SELECT user_id FROM users WHERE is_premium = true)
GROUP BY user_id
HAVING COUNT(*) > 10;
```

### Use Approximate Functions for Large Datasets

```sql
-- Exact count (slower on large datasets)
SELECT COUNT(*) FROM large_table;

-- Approximate count (much faster)
SELECT COUNT(*) as approx_count FROM large_table TABLESAMPLE SYSTEM(1);
```

---

## 6. Date/Time Optimization

### Use Index-Friendly Date Comparisons

```sql
-- Less efficient (function on column prevents index use)
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- More efficient (uses index)
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

### Use Appropriate Date Functions

```sql
-- Less efficient (function on every row)
SELECT * FROM orders WHERE DATE(order_date) = '2024-01-01';

-- More efficient (range comparison)
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2024-01-02';
```

---

## 7. Analyzing Query Performance

### Use EXPLAIN

```sql
-- Analyze query plan
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Detailed plan (PostgreSQL)
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Detailed plan (MySQL)
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'test@example.com';
```

### Understanding EXPLAIN Output

**Key indicators to look for:**

- **Seq Scan**: Sequential table scan (slow on large tables)
- **Index Scan**: Uses index (fast)
- **Index Only Scan**: Uses covering index (fastest)
- **Hash Join**: Efficient for joining large datasets
- **Nested Loop**: May be slow if inner table is large

**Example (PostgreSQL):**
```
Seq Scan on users  (cost=0.00..1234.56 rows=100 width=50)
  Filter: (email = 'test@example.com'::text)

vs

Index Scan using idx_users_email on users  (cost=0.00..12.34 rows=1 width=50)
  Index Cond: (email = 'test@example.com'::text)
```

---

## 8. Common Performance Issues

### N+1 Query Problem

**Problem:** Executing N+1 queries instead of 1.

```sql
-- Bad: N+1 queries
SELECT * FROM users;  -- 1 query
-- For each user, execute:
SELECT * FROM orders WHERE user_id = ?;  -- N queries

-- Good: Single query with JOIN
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### Cartesian Product

**Problem:** Accidentally creating all combinations of rows.

```sql
-- Bad: No join condition
SELECT * FROM users, orders;  -- Returns users × orders rows

-- Good: Proper join condition
SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
```

### Missing Index on Foreign Keys

**Problem:** JOIN queries are slow.

```sql
-- Solution: Create index on foreign key
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Over-Indexing

**Problem:** Too many indexes slow down INSERT/UPDATE/DELETE.

**Solution:** Only create indexes for frequently queried columns.

---

## 9. Database-Specific Optimization

### MySQL

```sql
-- Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Use FORCE INDEX to force index usage
SELECT * FROM users FORCE INDEX (idx_email) WHERE email = 'test@example.com';

-- Use SQL_NO_CACHE to test query without cache
SELECT SQL_NO_CACHE * FROM users WHERE email = 'test@example.com';

-- Use ANALYZE TABLE to update statistics
ANALYZE TABLE users;
```

### PostgreSQL

```sql
-- Use EXPLAIN ANALYZE for detailed analysis
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Use VACUUM ANALYZE to update statistics
VACUUM ANALYZE users;

-- Use CLUSTER to physically reorder table by index
CLUSTER users USING idx_email;

-- Use parallel queries for large tables
SET max_parallel_workers_per_gather = 4;
```

### SQLite

```sql
-- Use EXPLAIN QUERY PLAN
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Use ANALYZE to update statistics
ANALYZE;

-- Use PRAGMA to configure optimization
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

---

## 10. Best Practices

1. **Always EXPLAIN** before optimizing
2. **Index first**, optimize query later
3. **Avoid SELECT *** for performance and clarity
4. **Use appropriate data types** (INT instead of VARCHAR for numbers)
5. **Normalize for data integrity**, denormalize for read performance
6. **Use connection pooling** for application performance
7. **Monitor slow queries** regularly
8. **Update database statistics** after large data changes
9. **Test optimizations** on production-like data
10. **Document indexing strategy** for future maintenance

---

## 11. Tools and Resources

### Built-in Tools

- **EXPLAIN**: Query plan analysis
- **EXPLAIN ANALYZE**: Execution statistics
- **Slow Query Log**: Identify slow queries
- **Performance Schema (MySQL)**: Query performance metrics

### External Tools

- **pgAdmin (PostgreSQL)**: Database management and optimization
- **MySQL Workbench**: MySQL performance monitoring
- **DBeaver**: Universal database tool with query profiling
- **pt-query-digest (Percona)**: MySQL slow query analysis

### Further Reading

- Database documentation (PostgreSQL, MySQL, SQLite)
- "SQL Performance Explained" by Markus Winand
- Database-specific optimization blogs and communities
