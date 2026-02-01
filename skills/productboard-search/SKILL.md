---
name: productboard-search
description: Search and explore ProductBoard features, products, and feedback
user-invocable: true
homepage: https://github.com/robertoamoreno/openclaw-productboard
metadata: {"openclaw":{"emoji":"🔍"}}
---

# ProductBoard Search Skill

Search and explore your ProductBoard workspace to find features, products, components, and customer feedback.

## Available Tools

- `pb_search` - Global search across all ProductBoard entities
- `pb_feature_list` - List features with filters
- `pb_feature_get` - Get detailed feature information
- `pb_feature_search` - Search features by name/description
- `pb_product_list` - List all products
- `pb_product_get` - Get product details with components
- `pb_product_hierarchy` - View full product/component tree
- `pb_note_list` - List customer feedback notes

## Search Strategies

### Finding Features

1. **By keyword**: Use `pb_feature_search` with a query term
2. **By product**: Use `pb_feature_list` with `productId` filter
3. **By status**: Use `pb_feature_list` with `status` filter (new, in-progress, shipped, archived)
4. **By component**: Use `pb_feature_list` with `componentId` filter

### Understanding Structure

1. Start with `pb_product_hierarchy` to see the complete workspace organization
2. Use `pb_product_get` to explore a specific product and its components
3. Filter features by product or component to narrow down results

### Finding Customer Feedback

1. Use `pb_note_list` to see recent feedback
2. Filter by date range using `createdFrom` and `createdTo`
3. Use `pb_search` with type `note` to find specific feedback

## Example Queries

**User**: "Find all features related to authentication"
**Action**: Use `pb_feature_search` with query "authentication"

**User**: "What features are currently in progress?"
**Action**: Use `pb_feature_list` with status "in-progress"

**User**: "Show me the product structure"
**Action**: Use `pb_product_hierarchy` to get the full tree

**User**: "Find customer feedback about performance"
**Action**: Use `pb_search` with query "performance" and type "note"

## Tips

- Start broad with `pb_search`, then narrow down with specific tools
- Use `pb_product_hierarchy` first when exploring an unfamiliar workspace
- The search is case-insensitive and matches partial words
- Results include direct links to ProductBoard for quick access
