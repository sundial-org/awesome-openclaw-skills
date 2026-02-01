---
name: wpclaw-connector
description: Connects to a WooCommerce store via the WPClaw Connector plugin to fetch orders and products.
user-invocable: true
---

# WPClaw Connector

This skill allows you to interact with a WooCommerce store. You can check order status, search for products, and verify the store's connection health.

## Configuration

The following environment variables are required:
*   `WPCLAW_STORE_URL`: The full URL of your WordPress site (e.g., https://example.com).
*   `WPCLAW_STORE_SECRET`: The Secret Key from the WPClaw Connector plugin settings.

## Tools

### `check_order`
Use this tool to retrieve detailed information about a specific order.
*   **Input:** `id` (integer) - The Order ID.
*   **Output:** Formatted string with Status, Total, Customer, and Items.

### `find_product`
Use this tool to search for products by name or SKU.
*   **Input:** `query` (string) - The search term.
*   **Output:** List of matching products with IDs, Stock, and Price.

### `store_status`
Use this tool to check if the store is reachable and the plugin is active.
*   **Input:** (None)
*   **Output:** Connection status message.