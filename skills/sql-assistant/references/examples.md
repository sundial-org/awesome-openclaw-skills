# SQL Query Examples

Comprehensive collection of SQL query examples organized by use case and complexity.

---

## Basic Queries

### SELECT Statement

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, name, email FROM users;

-- Select with alias
SELECT
    id AS user_id,
    name AS user_name,
    email AS contact_email
FROM users;

-- Select distinct values
SELECT DISTINCT status FROM orders;
```

### WHERE Clause

```sql
-- Simple conditions
SELECT * FROM users WHERE age > 18;

-- Multiple conditions with AND/OR
SELECT * FROM users
WHERE age > 18 AND country = 'USA';

SELECT * FROM users
WHERE country = 'USA' OR country = 'Canada';

-- Range conditions
SELECT * FROM orders
WHERE total BETWEEN 100 AND 1000;

SELECT * FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Pattern matching
SELECT * FROM users
WHERE name LIKE 'J%';  -- Starts with J

SELECT * FROM users
WHERE email LIKE '%@gmail.com';  -- Ends with @gmail.com

-- NULL checking
SELECT * FROM users
WHERE phone_number IS NULL;

SELECT * FROM users
WHERE phone_number IS NOT NULL;
```

### ORDER BY

```sql
-- Sort by single column (ascending)
SELECT * FROM users ORDER BY name;

-- Sort descending
SELECT * FROM users ORDER BY created_at DESC;

-- Sort by multiple columns
SELECT * FROM users
ORDER BY country ASC, name DESC;
```

### LIMIT & OFFSET

```sql
-- MySQL
SELECT * FROM users LIMIT 10;

-- MySQL with offset
SELECT * FROM users LIMIT 10, 20;

-- PostgreSQL / SQLite
SELECT * FROM users LIMIT 10 OFFSET 20;

-- Get top N by value
SELECT * FROM orders
ORDER BY total DESC
LIMIT 10;
```

---

## Aggregations

### GROUP BY

```sql
-- Count by category
SELECT category, COUNT(*)
FROM products
GROUP BY category;

-- Sum by user
SELECT user_id, SUM(total) as total_spent
FROM orders
GROUP BY user_id;

-- Average with rounding
SELECT
    category,
    ROUND(AVG(price), 2) as avg_price
FROM products
GROUP BY category;

-- Multiple aggregations
SELECT
    user_id,
    COUNT(*) as order_count,
    SUM(total) as total_spent,
    AVG(total) as avg_order_value,
    MAX(total) as max_order,
    MIN(total) as min_order
FROM orders
GROUP BY user_id;
```

### HAVING Clause

```sql
-- Filter grouped results
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5;

-- Having with conditions
SELECT
    category,
    AVG(price) as avg_price
FROM products
GROUP BY category
HAVING AVG(price) > 50;
```

---

## Joins

### INNER JOIN

```sql
-- Basic inner join
SELECT
    u.name,
    o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Join with conditions
SELECT
    u.name,
    COUNT(o.id) as order_count
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
GROUP BY u.id, u.name;
```

### LEFT JOIN

```sql
-- All users, even those without orders
SELECT
    u.name,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Find users with no orders
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

### RIGHT JOIN

```sql
-- All orders, even if user doesn't exist
SELECT
    u.name,
    o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

### FULL OUTER JOIN (PostgreSQL)

```sql
-- All users and all orders
SELECT
    u.name,
    o.total
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;
```

### Multiple Joins

```sql
SELECT
    u.name,
    p.name as product_name,
    o.total,
    c.name as category_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE o.status = 'completed';
```

---

## Subqueries

### Scalar Subquery

```sql
-- Subquery returning single value
SELECT name,
    (SELECT AVG(price) FROM products) as avg_price
FROM products;
```

### IN Subquery

```sql
-- Products in categories with average price > 100
SELECT * FROM products
WHERE category_id IN (
    SELECT id FROM categories
    WHERE avg_price > 100
);
```

### EXISTS Subquery

```sql
-- Users who have placed orders
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id
);
```

### FROM Subquery

```sql
-- Using subquery as a table
SELECT * FROM (
    SELECT
        user_id,
        COUNT(*) as order_count
    FROM orders
    GROUP BY user_id
) as user_orders
WHERE order_count > 5;
```

---

## Common Table Expressions (CTE)

```sql
-- Basic CTE
WITH user_orders AS (
    SELECT
        user_id,
        COUNT(*) as order_count,
        SUM(total) as total_spent
    FROM orders
    GROUP BY user_id
)
SELECT u.name, uo.*
FROM users u
JOIN user_orders uo ON u.id = uo.user_id;

-- Multiple CTEs
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(total) as sales_total
    FROM orders
    GROUP BY month
),
monthly_targets AS (
    SELECT
        month,
        target_amount
    FROM sales_targets
)
SELECT
    ms.month,
    ms.sales_total,
    mt.target_amount,
    ms.sales_total - mt.target_amount as variance
FROM monthly_sales ms
JOIN monthly_targets mt ON ms.month = mt.month;
```

---

## Window Functions

### ROW_NUMBER

```sql
-- Rank rows within groups
SELECT
    user_id,
    total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) as rank
FROM orders;

-- Get top 3 orders per user
WITH ranked_orders AS (
    SELECT
        user_id,
        total,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) as rank
    FROM orders
)
SELECT * FROM ranked_orders
WHERE rank <= 3;
```

### RANK / DENSE_RANK

```sql
-- Rank with ties
SELECT
    user_id,
    total,
    RANK() OVER (ORDER BY total DESC) as rank,
    DENSE_RANK() OVER (ORDER BY total DESC) as dense_rank
FROM orders;
```

### LAG / LEAD

```sql
-- Compare with previous row
SELECT
    user_id,
    order_date,
    total,
    LAG(total) OVER (PARTITION BY user_id ORDER BY order_date) as prev_total,
    total - LAG(total) OVER (PARTITION BY user_id ORDER BY order_date) as diff
FROM orders;
```

### Running Total

```sql
-- Cumulative sum
SELECT
    order_date,
    total,
    SUM(total) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM orders;
```

---

## Data Modification

### INSERT

```sql
-- Insert single row
INSERT INTO users (name, email, age)
VALUES ('John Doe', 'john@example.com', 30);

-- Insert multiple rows
INSERT INTO users (name, email, age)
VALUES
    ('Jane Doe', 'jane@example.com', 28),
    ('Bob Smith', 'bob@example.com', 35);

-- Insert from SELECT
INSERT INTO active_users (user_id, name)
SELECT id, name
FROM users
WHERE status = 'active';
```

### UPDATE

```sql
-- Update single column
UPDATE users
SET email = 'newemail@example.com'
WHERE id = 1;

-- Update multiple columns
UPDATE users
SET
    name = 'John Smith',
    age = 31,
    updated_at = NOW()
WHERE id = 1;

-- Update with condition
UPDATE orders
SET status = 'cancelled'
WHERE created_at < '2024-01-01' AND status = 'pending';
```

### DELETE

```sql
-- Delete specific row
DELETE FROM users
WHERE id = 1;

-- Delete with condition
DELETE FROM orders
WHERE status = 'cancelled' AND created_at < '2024-01-01';

-- Delete using subquery
DELETE FROM order_items
WHERE order_id IN (
    SELECT id FROM orders WHERE status = 'cancelled'
);
```

---

## Date & Time Functions

### MySQL

```sql
-- Current date/time
SELECT NOW();
SELECT CURDATE();
SELECT CURTIME();

-- Date arithmetic
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);
SELECT DATE_SUB(NOW(), INTERVAL 1 MONTH);
SELECT DATEDIFF('2024-12-31', '2024-01-01');

-- Date parts
SELECT YEAR(NOW());
SELECT MONTH(NOW());
SELECT DAY(NOW());
SELECT DAYNAME(NOW());

-- Date formatting
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d');
```

### PostgreSQL

```sql
-- Current date/time
SELECT NOW();
SELECT CURRENT_DATE;
SELECT CURRENT_TIME;

-- Date arithmetic
SELECT NOW() + INTERVAL '7 days';
SELECT NOW() - INTERVAL '1 month';

-- Date parts
SELECT EXTRACT(YEAR FROM NOW());
SELECT EXTRACT(MONTH FROM NOW());
SELECT EXTRACT(DAY FROM NOW());

-- Date truncation
SELECT DATE_TRUNC('month', NOW());
SELECT DATE_TRUNC('week', NOW());
```

---

## String Functions

```sql
-- Concatenation
-- MySQL
SELECT CONCAT(first_name, ' ', last_name) as full_name;

-- PostgreSQL / SQLite
SELECT first_name || ' ' || last_name as full_name;

-- String manipulation
SELECT UPPER('hello');  -- HELLO
SELECT LOWER('HELLO');  -- hello
SELECT TRIM('  hello  ');  -- hello
SELECT SUBSTRING('hello world', 1, 5);  -- hello
SELECT REPLACE('hello world', 'world', 'there');  -- hello there

-- String length
SELECT LENGTH('hello');  -- 5

-- Position
SELECT POSITION('world' IN 'hello world');  -- 7
```

---

## Conditional Logic

### CASE

```sql
-- Basic CASE
SELECT
    name,
    age,
    CASE
        WHEN age < 18 THEN 'Minor'
        WHEN age < 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM users;

-- CASE with aggregation
SELECT
    category,
    COUNT(*) as total_products,
    SUM(CASE WHEN price > 100 THEN 1 ELSE 0 END) as expensive_products,
    SUM(CASE WHEN price <= 100 THEN 1 ELSE 0 END) as affordable_products
FROM products
GROUP BY category;

-- CASE in WHERE
SELECT * FROM users
WHERE
    CASE
        WHEN country = 'USA' THEN age >= 21
        ELSE age >= 18
    END;
```

---

## NULL Handling

```sql
-- COALESCE (return first non-NULL)
SELECT
    name,
    COALESCE(phone, 'N/A') as phone_number
FROM users;

-- NULLIF (return NULL if equal)
SELECT
    a / NULLIF(b, 0) as result
FROM numbers;

-- CASE for NULL handling
SELECT
    name,
    CASE
        WHEN phone IS NOT NULL THEN phone
        ELSE 'No phone provided'
    END as phone_display
FROM users;
```

---

## Common Patterns

### Pagination

```sql
-- MySQL
SELECT * FROM users
ORDER BY id
LIMIT 20 OFFSET 0;  -- Page 1

SELECT * FROM users
ORDER BY id
LIMIT 20 OFFSET 20;  -- Page 2

-- PostgreSQL
SELECT * FROM users
ORDER BY id
LIMIT 20 OFFSET 0;
```

### Top N Per Group

```sql
-- Using DISTINCT ON (PostgreSQL)
SELECT DISTINCT ON (user_id)
    user_id,
    total,
    order_date
FROM orders
ORDER BY user_id, total DESC;

-- Using window functions
WITH ranked_orders AS (
    SELECT
        user_id,
        total,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) as rank
    FROM orders
)
SELECT * FROM ranked_orders
WHERE rank = 1;
```

### Running Total

```sql
SELECT
    order_date,
    total,
    SUM(total) OVER (ORDER BY order_date) as running_total
FROM orders;
```

### Percentage of Total

```sql
SELECT
    category,
    COUNT(*) as category_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM products
GROUP BY category;
```

### Pivot Table

```sql
-- Convert rows to columns
SELECT
    user_id,
    SUM(CASE WHEN month = 'Jan' THEN total ELSE 0 END) as jan_total,
    SUM(CASE WHEN month = 'Feb' THEN total ELSE 0 END) as feb_total,
    SUM(CASE WHEN month = 'Mar' THEN total ELSE 0 END) as mar_total
FROM monthly_sales
GROUP BY user_id;
```

### Recursive CTE (PostgreSQL)

```sql
-- Find all subordinates
WITH RECURSIVE org_chart AS (
    -- Base case
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT
        e.id,
        e.name,
        e.manager_id,
        oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart
ORDER BY level, name;
```

---

## Performance Tips

1. **Use indexes on columns in WHERE, JOIN, and ORDER BY**
2. **Avoid SELECT *** - only select needed columns
3. **Use LIMIT when you don't need all results**
4. **Use EXISTS instead of IN for subqueries**
5. **Consider using UNION ALL instead of UNION if you know there are no duplicates**
6. **Use appropriate data types**
7. **Use EXPLAIN to analyze query plans**
8. **Denormalize when read performance is critical**
