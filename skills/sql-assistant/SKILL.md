---
name: sql-assistant
description: Comprehensive SQL query assistant for database operations, optimization, and troubleshooting. Use when Codex needs to write, debug, optimize, or explain SQL queries; analyze database schemas; or help with SQL-related tasks including joins, subqueries, aggregations, and performance tuning. Supports MySQL, PostgreSQL, SQLite, and other SQL dialects.
---

# SQL Assistant

## Overview

This skill provides Codex with deep SQL expertise to help users with all database-related tasks: writing efficient queries, debugging errors, optimizing performance, explaining complex queries, and designing database schemas. Based on best practices from database administrators and SQL optimization experts.

## Core Capabilities

### 1. Query Writing

Write clean, efficient SQL queries based on user requirements:

**Basic Query Construction:**
```
User: "Show me all users who signed up in the last 7 days"
Codex: SELECT * FROM users WHERE created_at >= DATE('now', '-7 days');
```

**Complex Queries:**
- **Joins**: Inner, left, right, full outer joins
- **Subqueries**: Nested queries, correlated subqueries
- **Aggregations**: GROUP BY, HAVING, window functions
- **CTEs**: Common Table Expressions for complex logic
- **Unions**: Combining results from multiple queries

**Example Multi-Join Query:**
```sql
SELECT
    u.name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 10;
```

### 2. Query Debugging

Identify and fix common SQL errors:

**Common Errors to Fix:**
- Syntax errors (missing commas, unbalanced parentheses)
- Column/table name typos
- Invalid data type usage
- Missing FROM clauses
- Incorrect GROUP BY usage
- Unquoted string literals

**Debugging Process:**
1. Analyze the error message
2. Identify the root cause
3. Explain why the error occurred
4. Provide the corrected query
5. Explain the fix to help the user learn

**Example:**
```
User: SELECT * FROM users WHERE created_at = '2024-01-01' AND status = active
Error: column "active" does not exist

Codex: The issue is that 'active' should be quoted as a string literal:

SELECT * FROM users WHERE created_at = '2024-01-01' AND status = 'active';

Without quotes, SQL treats 'active' as a column name rather than a string value.
```

### 3. Query Optimization

Improve query performance through indexing and rewriting:

**Optimization Strategies:**
- **Indexing**: Add indexes on frequently filtered columns
- **Query Rewriting**: Use efficient patterns (EXISTS vs IN, etc.)
- **Subquery Optimization**: Convert subqueries to joins when beneficial
- **Limit Results**: Use LIMIT/OFFSET or pagination
- **Avoid SELECT ***: Only select needed columns
- **Proper Join Order**: Join smaller tables first

**Before Optimization:**
```sql
SELECT * FROM orders o
WHERE user_id IN (SELECT id FROM users WHERE status = 'active');
```

**After Optimization:**
```sql
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.status = 'active';

-- Better performance because:
-- 1. Uses indexed join instead of subquery
-- 2. Database can optimize the join execution plan
-- 3. Potentially uses existing indexes on both tables
```

### 4. Query Explanation

Break down complex queries in plain English:

**Explanation Template:**
1. **Purpose**: What the query does overall
2. **Step-by-Step**: Breakdown of each clause
3. **Result**: What the final output looks like
4. **Performance Notes**: Any optimization considerations

**Example Explanation:**
```
Query: SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id;

Explanation:
1. FROM users u: Start with the users table (alias 'u')
2. LEFT JOIN orders o: For each user, include matching orders (or NULL if none)
3. ON u.id = o.user_id: Match records where user IDs are equal
4. GROUP BY u.id: Group results by each user
5. COUNT(o.id): Count orders for each user (NULL counts as 0 with LEFT JOIN)
6. Result: List of users with their order count, including users with 0 orders
```

### 5. Database Schema Design

Help design efficient database schemas:

**Schema Design Principles:**
- **Normalization**: Reduce data redundancy (1NF, 2NF, 3NF)
- **Proper Data Types**: Use appropriate types (VARCHAR, INT, DECIMAL, etc.)
- **Primary Keys**: Always have a primary key for each table
- **Foreign Keys**: Enforce referential integrity
- **Indexes**: Add indexes on frequently queried columns
- **Naming Conventions**: Use consistent, descriptive names

**Example Schema:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Create index on email for fast lookups
CREATE INDEX idx_users_email ON users(email);
```

## Quick Start

**Scenario 1: Write a Query**
```
User: "Find the top 5 customers by total spending"
Codex: [Writes efficient query with JOIN and aggregation]
```

**Scenario 2: Fix a Broken Query**
```
User: [Posts query with error]
Codex: [Explains error and provides corrected version]
```

**Scenario 3: Optimize a Slow Query**
```
User: "This query takes too long: [query]"
Codex: [Analyzes and provides optimized version with index recommendations]
```

## SQL Dialect Support

This skill supports multiple SQL dialects:

### MySQL / MariaDB
- Uses ``` (backticks) for identifiers
- LIMIT syntax: LIMIT offset, count
- String functions: CONCAT(), SUBSTRING(), etc.
- Date functions: NOW(), DATE_ADD(), etc.

### PostgreSQL
- Uses "" (double quotes) for identifiers
- LIMIT syntax: LIMIT count OFFSET offset
- String functions: || for concatenation, SUBSTR(), etc.
- Date functions: NOW(), DATE_TRUNC(), etc.

### SQLite
- Uses "" (double quotes) or [] for identifiers
- LIMIT syntax: LIMIT count OFFSET offset
- String functions: || for concatenation, substr(), etc.
- Date functions: date(), datetime(), etc.

### SQL Server (T-SQL)
- Uses "" (double quotes) or [] for identifiers
- LIMIT syntax: TOP count, or OFFSET-FETCH
- String functions: + for concatenation, SUBSTRING(), etc.
- Date functions: GETDATE(), DATEADD(), etc.

**Tip**: Always ask the user which database system they're using to provide accurate syntax.

## Common Query Patterns

### Pagination
```sql
-- MySQL
SELECT * FROM users LIMIT 10 OFFSET 20;

-- PostgreSQL / SQLite
SELECT * FROM users LIMIT 10 OFFSET 20;

-- SQL Server
SELECT * FROM users ORDER BY id OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

### Ranking
```sql
-- Row numbers
SELECT name, score,
    ROW_NUMBER() OVER (ORDER BY score DESC) as rank
FROM scores;

-- Percentiles
SELECT name, score,
    PERCENT_RANK() OVER (ORDER BY score) as percentile
FROM scores;
```

### Conditional Aggregation
```sql
SELECT
    DATE(created_at) as day,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    COUNT(*) as total
FROM orders
GROUP BY DATE(created_at);
```

## When to Use This Skill

Use this skill when:
- User asks to write or create SQL queries
- User needs help debugging SQL errors
- User mentions "SQL query", "database", "write SQL"
- User wants to optimize query performance
- User asks about joins, aggregations, or SQL features
- User needs database schema design advice
- User wants to understand how a complex query works

## Best Practices

1. **Always Explain**: Don't just give the answer—teach the concept
2. **Performance First**: Always consider query performance
3. **Use Examples**: Provide concrete examples for every concept
4. **Check Dialect**: Confirm the database system before writing queries
5. **Suggest Indexes**: Recommend indexes for frequently used columns
6. **Security Awareness**: Warn about SQL injection and use parameterized queries
7. **Test Before Sharing**: Run queries in your head to verify they work

## Advanced Features

### Performance Analysis

When analyzing slow queries:
1. Check for missing indexes on WHERE/JOIN columns
2. Look for full table scans
3. Examine the execution plan (EXPLAIN)
4. Consider query rewriting
5. Suggest appropriate indexes

**Example EXPLAIN Analysis:**
```
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- Look for:
-- Index Scan (good) vs Sequential Scan (bad)
-- Cost estimates
-- Number of rows examined
```

### Window Functions

Advanced queries with window functions:
- ROW_NUMBER(): Unique row numbers
- RANK() / DENSE_RANK(): Ranking with ties
- LAG() / LEAD(): Access rows before/after
- SUM() OVER(): Running totals
- FIRST_VALUE() / LAST_VALUE(): Window aggregates

**Example:**
```sql
SELECT
    user_id,
    created_at,
    amount,
    SUM(amount) OVER (
        PARTITION BY user_id
        ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM orders;
```

### Pivot Tables

Convert rows to columns:
```sql
-- Standard SQL approach
SELECT
    user_id,
    SUM(CASE WHEN month = 'Jan' THEN amount ELSE 0 END) as jan,
    SUM(CASE WHEN month = 'Feb' THEN amount ELSE 0 END) as feb,
    SUM(CASE WHEN month = 'Mar' THEN amount ELSE 0 END) as mar
FROM monthly_sales
GROUP BY user_id;
```

## Resources

### references/examples.md
Extensive collection of SQL query examples organized by:
- Query type (SELECT, INSERT, UPDATE, DELETE)
- Complexity (basic, intermediate, advanced)
- Use case (analytics, reporting, transaction processing)
- Database system (MySQL, PostgreSQL, SQLite, SQL Server)

### references/optimization.md
SQL optimization techniques including:
- Indexing strategies
- Query rewriting patterns
- Execution plan analysis
- Common performance anti-patterns

### references/common-errors.md
Frequently encountered SQL errors with solutions:
- Syntax errors and their fixes
- Data type mismatches
- Constraint violations
- Deadlock scenarios

## Tips for Codex

- Always verify SQL syntax before providing queries
- When unsure about a specific database system, ask the user
- Provide both simple and advanced versions when appropriate
- Use comments in complex queries to explain each part
- Suggest testing queries on a small dataset first
- Remind users about database backups before running DELETE/DROP operations
