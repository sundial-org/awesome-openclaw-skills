# Store-Specific Navigation and Extraction Guide

This document provides tested, working navigation paths for the two automation-friendly retailers. Follow these instructions exactly to avoid multi-turn debugging.

## Table of Contents

1. [Target](#target)
2. [Global Brands Store](#global-brands-store)
3. [Common Patterns](#common-patterns-across-both-stores)

---

## Target

**URL**: https://www.target.com/c/pants-men-s-clothing/-/N-5xu29

**Store Type**: US budget-friendly retailer
**Strengths**: Excellent value ($29.99-$59.99), wide size availability, no bot protection
**Price Range**: $29.99-$59.99 for most jeans
**Currency**: USD ($)

### Navigation Strategy

**Starting point**: Direct navigation to the men's pants collection URL above. This URL loads reliably without bot detection.

**Step-by-step automation sequence:**

1. **Navigate and wait**
   ```bash
   agent-browser open "https://www.target.com/c/pants-men-s-clothing/-/N-5xu29"
   agent-browser wait 3000
   ```

2. **Scroll to load initial products**
   ```bash
   agent-browser scroll down 500
   agent-browser wait 2000
   ```

3. **Take snapshot to get filter button refs**
   ```bash
   agent-browser snapshot -i --json
   ```

4. **Click Size filter button**
   - Look for button with name "Size"
   - Example ref: `@e32` (ref numbers change per page load)
   ```bash
   # Find Size button ref from snapshot
   agent-browser click @e{SIZE_BUTTON_REF}
   agent-browser wait 1500
   ```

5. **Take new snapshot to get size checkboxes**
   ```bash
   agent-browser snapshot -i --json
   ```

6. **Select desired size (e.g., 30x30)**
   - Look for checkbox with name matching exact size (e.g., "30x30")
   - Example ref: `@e34` for size 30x30
   ```bash
   agent-browser click @e{SIZE_CHECKBOX_REF}
   agent-browser wait 2500
   ```

7. **Close filter modal and navigate to jeans**
   ```bash
   agent-browser press Escape
   agent-browser wait 1000
   ```

8. **Take snapshot to find jeans category link**
   ```bash
   agent-browser snapshot -i --json
   ```

9. **Click Jeans category link** (optional - to narrow from all pants to just jeans)
   - Look for link with name "Jeans"
   - Example ref: `@e26`
   ```bash
   agent-browser click @e{JEANS_LINK_REF}
   agent-browser wait 3000
   ```

10. **Scroll to load more products**
    ```bash
    agent-browser scroll down 600
    agent-browser wait 2000
    agent-browser scroll down 600
    agent-browser wait 2000
    # Repeat as needed - typically 3-4 scrolls loads 20-30 products
    ```

### Data Extraction

**Product information visible on page:**
- Product name (e.g., "Wrangler Men's Relaxed Fit Straight Jeans")
- Current price (e.g., "$29.99")
- Star rating (e.g., "4.8★")
- Review count (e.g., "(90 reviews)")
- Popularity indicator (e.g., "300+ bought in last month")
- Brand name
- Color options
- Stock status (e.g., "Only 2 left at El Paso Joe Battle Blvd")

**Extraction approach:**
1. Take final snapshot after scrolling
2. Look for link elements containing product names
3. Extract text for prices, ratings, brands
4. Product URLs can be extracted from link href attributes

**Key data points to capture:**
- `product_name`: Full product title from link text
- `price_current`: Price shown (always in USD)
- `rating`: Star rating if available
- `review_count`: Number in parentheses after rating
- `brand`: Brand name (Wrangler, Goodfellow & Co, Levi's, etc.)
- `in_stock`: Based on stock status text or absence of "out of stock" indicator
- `url`: Extract href attribute from product link

### Special Considerations

**Size availability:**
- Target shows size-specific results after filtering
- If size 30x30 is selected, only products available in 30x30 will appear
- No need to verify size on individual product pages

**Filter refs change:**
- Element refs (@e1, @e2, etc.) change with each page load
- Always take a fresh snapshot before clicking elements
- Use descriptive search (name, role) to find correct ref

**Jeans vs All Pants:**
- Starting URL shows all pants (chinos, cargo, jeans, dress pants)
- Clicking "Jeans" category link narrows to jeans only
- Both approaches work - choose based on user preference

**Price display:**
- Clearance items show original price with strikethrough
- Sale items show "Select items on clearance" badge
- Regular price items show single price

**Common issues and solutions:**
- **Modal blocking clicks**: Use `agent-browser press Escape` before clicking
- **Slow loading**: Increase wait time to 3000ms after navigation
- **Filter not applying**: Wait 2500ms after clicking size checkbox

---

## Global Brands Store

**URL**: https://www.globalbrandsstore.com/en/c/men/clothing/jeans

**Store Type**: European designer outlet
**Strengths**: Designer brands (BOSS, HUGO), no bot protection, wide selection
**Price Range**: €125-€185+ for designer jeans
**Currency**: EUR (€)

### Navigation Strategy

**Starting point**: Direct navigation to men's jeans collection URL above. This URL loads reliably.

**Step-by-step automation sequence:**

1. **Navigate and wait**
   ```bash
   agent-browser open "https://www.globalbrandsstore.com/en/c/men/clothing/jeans"
   agent-browser wait 3000
   ```

2. **Scroll to see initial products**
   ```bash
   agent-browser scroll down 400
   agent-browser wait 1500
   ```

3. **Take snapshot to get filter refs**
   ```bash
   agent-browser snapshot -i --json
   ```

4. **Click Size filter button**
   - Look for button with name "Size"
   - Example ref: `@e16`
   ```bash
   agent-browser click @e{SIZE_BUTTON_REF}
   agent-browser wait 1500
   ```

5. **Take screenshot to see size options**
   ```bash
   agent-browser screenshot /tmp/globalbrands-sizes.png
   ```
   - Verify size options are visible (28, 30, 32, 34, 36, 42, 44)

6. **Select size using JavaScript** (checkbox clicking has issues due to multiple "30" elements)
   ```bash
   # For size 30, use JavaScript to click the checkbox directly
   agent-browser eval "document.querySelector('input[type=\"checkbox\"][value=\"30\"]')?.click()"
   agent-browser wait 2000
   ```

   **Alternative approach if checkbox value differs:**
   ```bash
   # Find the label containing "30" and click its associated input
   agent-browser eval "Array.from(document.querySelectorAll('.refinement-name')).find(el => el.textContent.trim() === '30')?.closest('button')?.click()"
   agent-browser wait 2000
   ```

7. **Scroll to load products**
   ```bash
   agent-browser scroll down 600
   agent-browser wait 2000
   agent-browser scroll down 600
   agent-browser wait 2000
   ```

### Data Extraction

**Product information visible on page:**
- Brand name (HUGO, BOSS, HUGO BLUE, etc.)
- Product description (e.g., "Relaxed fit jeans in dark blue denim")
- Price in Euros (e.g., "€ 154.99")
- Product images
- Size labels (28, 30, 32, etc.)

**Extraction approach:**
1. Take snapshot after scrolling
2. Look for product card elements
3. Extract brand, description, and price
4. Product links can be extracted from href attributes

**Key data points to capture:**
- `store_name`: "Global Brands Store"
- `brand`: Brand name (HUGO, BOSS, etc.)
- `product_name`: Combine brand + description
- `price_current`: Price in Euros (€)
- `price_usd`: Convert EUR to USD (approximate rate: €1 = $1.09)
- `sizes_available`: Size shown in UK/USA format
- `url`: Extract href from product card
- `in_stock`: Assume in stock if displayed after filter

### Special Considerations

**Currency conversion:**
- All prices are in Euros (€)
- Provide USD conversion for comparison: multiply EUR by ~1.09
- Example: €125.00 ≈ $136.25 USD
- Note exchange rate in output

**Size selection challenges:**
- Multiple "30" text elements on page (price ranges, size filters, etc.)
- Using `agent-browser find text "30" click` fails with strict mode violation
- **Solution**: Use JavaScript eval to target specific checkbox
- Alternative: Use CSS selectors to target the size filter section specifically

**Size format:**
- Uses UK/USA sizing (28, 30, 32, 34, 36)
- Does not use inseam (no 30x30 format)
- Standard European sizing approach

**Brand importance:**
- Designer brands are the main selling point
- Always include brand name prominently in results
- BOSS and HUGO are premium brands worth highlighting

**International shipping:**
- European retailer - may have higher shipping costs to US
- Mention this limitation when presenting results
- Delivery times may be longer than US retailers

**Product display:**
- Shows model wearing jeans
- Color swatches available for some products
- "New" badges for recent arrivals
- Sale badges (e.g., "-20%") for discounted items

**Common issues and solutions:**
- **Multiple "30" matches**: Use JavaScript eval with specific selector
- **Checkbox not clicking**: Target input element directly, not label
- **Products not loading**: Scroll incrementally (400-600px at a time)
- **Filter not applying**: Wait 2000ms after clicking size

---

## Common Patterns Across Both Stores

### General Automation Best Practices

**1. Wait times:**
- After navigation: 3000ms minimum
- After clicking filters: 1500-2500ms
- After scrolling: 1500-2000ms
- Between actions: 1000ms minimum

**2. Snapshot strategy:**
- Always take fresh snapshot after navigation or filter changes
- Use `-i` flag for interactive elements only (faster)
- Use `--json` flag for machine-readable output
- Parse JSON to find specific refs by name or role

**3. Scrolling for lazy-loaded content:**
```bash
# Standard scroll pattern
agent-browser scroll down 500-600
agent-browser wait 2000
# Repeat 3-4 times for 20-30 products
```

**4. Modal/overlay handling:**
```bash
agent-browser press Escape
agent-browser wait 1000
```

**5. Finding elements by name/role:**
```bash
# Example: Find Size button
agent-browser snapshot -i --json 2>/dev/null | jq -r '.data.refs | to_entries[] | select(.value.name == "Size") | "\(.key)"'
```

### Error Prevention

**Multi-turn debugging issues we solved:**

1. **"Element is blocked by another element"**
   - Solution: Press Escape to close modals before clicking
   - Wait 1000ms after Escape

2. **"Strict mode violation: resolved to X elements"**
   - Solution: Don't use generic text like "30" with `find text` command
   - Use specific selectors or JavaScript eval

3. **"Timeout waiting for networkidle"**
   - Solution: Skip networkidle wait, use fixed time waits instead
   - 3000ms is reliable for both stores

4. **Refs not found after filter change**
   - Solution: Always retake snapshot after clicking filters
   - Refs change when DOM updates

5. **Size not applying**
   - Solution: Wait longer (2500ms) after clicking size checkbox
   - Verify with screenshot before proceeding

### Data Quality Checks

Before presenting results to user:
- ✅ Verify price is numeric and reasonable
- ✅ Check product name is not empty or truncated
- ✅ Confirm size matches user request
- ✅ Ensure URLs are complete and valid
- ✅ For Global Brands Store: Convert EUR to USD
- ✅ Include stock status if available
- ✅ Add ratings/reviews if available (Target)

### Output Format

Present results in this order:
1. Store name
2. Brand + Product name
3. Price (with currency)
4. Size confirmation
5. Additional details (rating, reviews, stock)
6. Direct link
7. Brief value proposition

**Example:**
```
1. Target - Wrangler Men's Relaxed Fit Straight Jeans
   $29.99
   Size 30x30 IN STOCK
   Rating: 4.8★ (90 reviews)
   → https://www.target.com/...
   Why: Unbeatable value - classic Wrangler quality
```

---

## Troubleshooting Quick Reference

| Issue | Store | Solution |
|-------|-------|----------|
| Modal blocking clicks | Target | `agent-browser press Escape && wait 1000` |
| Size filter not opening | Both | Increase wait to 2000ms after click |
| Multiple "30" matches | Global Brands | Use JavaScript eval with specific selector |
| Products not loading | Both | Scroll incrementally, wait 2000ms between scrolls |
| Refs not found | Both | Retake snapshot after DOM changes |
| Page blank/loading | Both | Wait 3000ms after navigation |
| Filter not applying | Target | Wait 2500ms after size checkbox click |

---

## Testing Checklist

Before deploying changes, verify:
- [ ] Target URL loads without "Access Denied"
- [ ] Global Brands Store URL loads without blocking
- [ ] Size filter can be clicked on both stores
- [ ] Size 30 can be selected on both stores
- [ ] Products load after filtering
- [ ] Can extract product names and prices
- [ ] Scrolling loads additional products
- [ ] No multi-turn debugging required
- [ ] First-try success on both stores
