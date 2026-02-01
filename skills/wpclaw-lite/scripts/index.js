const axios = require('axios');
const crypto = require('crypto');

// 1. Configuration
const { WPCLAW_STORE_URL, WPCLAW_STORE_SECRET } = process.env;

if (!WPCLAW_STORE_URL || !WPCLAW_STORE_SECRET) {
    throw new Error('Configuration Error: WPCLAW_STORE_URL and WPCLAW_STORE_SECRET environment variables are required.');
}

// 2. Helper Function
async function callWoo(endpoint, payload) {
    try {
        const url = `${WPCLAW_STORE_URL}/wp-json/wpclaw/v1${endpoint}`;
        const body = JSON.stringify(payload);

        // Generate HMAC-SHA256 Signature
        const signature = crypto
            .createHmac('sha256', WPCLAW_STORE_SECRET)
            .update(body)
            .digest('hex');

        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-WPClaw-Signature': signature
            }
        };

        const response = await axios.post(url, body, config);
        return response.data;

    } catch (error) {
        if (error.response) {
            throw new Error(`Store Error ${error.response.status}: ${error.response.data.message || error.response.statusText}`);
        } else if (error.request) {
            throw new Error('Store Error: No response received from server.');
        } else {
            throw new Error(`Store Error: ${error.message}`);
        }
    }
}

// 3. Exported Tools
module.exports = {

    /**
     * Tool: check_order
     * Description: Get details of a specific order by ID.
     */
    check_order: async ({ id }) => {
        try {
            if (!id) throw new Error('Order ID is required.');
            
            const order = await callWoo('/orders/get', { id: parseInt(id) });
            
            let output = `📦 Order #${order.id} | Status: ${order.status} | Total: ${order.currency} ${order.total}\n`;
            output += `Date: ${order.date_created}\n`;
            output += `Customer: ${order.billing.first_name || ''} ${order.billing.last_name || ''}\n`;
            output += `Items:\n`;
            
            if (order.items && order.items.length > 0) {
                order.items.forEach(item => {
                    output += `- ${item.quantity}x ${item.name} (${item.total})\n`;
                });
            } else {
                output += `- No items found.\n`;
            }

            return output.trim();
        } catch (error) {
            return `❌ Failed to fetch order: ${error.message}`;
        }
    },

    /**
     * Tool: find_product
     * Description: Search for a product by name or ID.
     */
    find_product: async ({ query }) => {
        try {
            if (!query) throw new Error('Search query is required.');

            const products = await callWoo('/products/search', { query: String(query) });

            if (!products || products.length === 0) {
                return `🔎 No products found for "${query}".`;
            }

            let output = `🔎 Found Products:\n`;
            products.forEach((p, index) => {
                output += `${index + 1}. ${p.name} (ID: ${p.id}) | Stock: ${p.stock_quantity ?? 'N/A'} | Price: ${p.price}\n`;
            });

            return output.trim();
        } catch (error) {
            return `❌ Search failed: ${error.message}`;
        }
    },

    /**
     * Tool: store_status
     * Description: Check connection status.
     */
    store_status: async () => {
        try {
            const url = `${WPCLAW_STORE_URL}/wp-json/wpclaw/v1/system/status`;
            const response = await axios.get(url); 
            
            const data = response.data;
            if (data.status === 'ok') {
                return `✅ Store is Online (Plugin v${data.version}).`;
            } else {
                return `⚠️ Store returned unexpected status: ${JSON.stringify(data)}`;
            }
        } catch (error) {
            return `❌ Connection Failed: ${error.message}`;
        }
    }
};