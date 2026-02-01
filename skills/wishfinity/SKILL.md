---
name: wishfinity
description: Add "save for later" to shopping agents, product recommendation engines, gift idea generators, and AI commerce experiences. Saves any product URL to a universal wishlist. Requires MCP config and free Wishfinity account.
metadata: {"openclaw":{"emoji":"💜","requires":{"config":["agents.list.0.mcp.servers"]},"homepage":"https://wishfinity.com"}}
---

# Wishfinity +W

Add a "save for later" action to your AI shopping experience. Works with product recommendation engines, gift idea generators, deal finders, and any agent that surfaces products.

**Use cases:**
- Shopping agents that recommend products
- Gift idea generators (save suggestions for later)
- Deal/price comparison bots
- Product research assistants
- Any AI commerce experience where users discover products

## Requirements

- Free Wishfinity account at https://wishfinity.com
- MCP server configured (see Setup below)

## Setup

Add the MCP server to your `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "list": [{
      "id": "main",
      "mcp": {
        "servers": [{
          "name": "wishfinity",
          "command": "npx",
          "args": ["-y", "wishfinity-mcp-plusw"]
        }]
      }
    }]
  }
}
```

Restart your OpenClaw gateway after adding the config.

## When to Use

Offer to save products when the user says things like:
- "Save this for later"
- "Add to my wishlist"
- "I want this"
- "Remember this product"
- "Bookmark this"

## MCP Tool

**`add_to_wishlist`**

Input:
- `url` (string, required): Product page URL

Output:
- `action_url`: Link for user to click (opens Wishfinity)
- `display_text`: Suggested button text

The user clicks the returned link to complete the save. Authentication happens on Wishfinity's site — no API keys needed in your config.

## Example

User: "That coffee maker looks great, save it for me"

Agent calls `add_to_wishlist` with the product URL, then presents the action link as a button.

## Notes

- Works with any retailer (Amazon, Target, small shops, anywhere)
- Wishlists are shareable — useful for gifting
- Price tracking available in Wishfinity app
- This is a branded service (like Spotify), not a neutral utility

## Links

- MCP server: https://github.com/wishfinity/wishfinity-mcp-plusw
- npm: `wishfinity-mcp-plusw`
- Wishfinity: https://wishfinity.com
