# OpenClaw Connector Skill 🦞

This is an OpenClaw Skill designed to bridge the gap between your AI agents and your WooCommerce store. It works in tandem with the **OpenClaw Connector Lite** WordPress plugin.

## 🛠 Prerequisites

To use this skill, you must have the **OpenClaw Connector Lite** plugin installed and active on your WordPress site.

1.  Install the plugin on your WordPress site.
2.  Go to **OpenClaw Lite** (or WooCommerce > Settings > OpenClaw).
3.  Copy your **Store Secret Key**.

## 🚀 Installation (Skill)

1.  Place the `openclaw` folder in your OpenClaw skills directory.
2.  Open a terminal in the folder and run:
    ```bash
    npm install
    ```

## ⚙️ Configuration

Configure your bot environment with the following variables:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `OPENCLAW_STORE_URL` | Your website base URL | `https://yourstore.com` |
| `OPENCLAW_STORE_SECRET` | The `sk_live_...` key from the plugin | `sk_live_abc123...` |

## 🧰 Available Tools

Once installed, your agent will have access to:

*   **`check_order`**: Retrieve status, totals, customer info, and line items for any Order ID.
*   **`find_product`**: Search for products by name or SKU to check stock and pricing.
*   **`store_status`**: Quickly verify if the connection between the bot and the site is healthy.

## 🔒 Security

Connection is secured via **HMAC-SHA256 signature verification**. Every request sent by this skill is signed with your Store Secret, ensuring that your data can only be accessed by authorized bots.
