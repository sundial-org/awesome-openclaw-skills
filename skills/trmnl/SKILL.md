---
name: trmnl
description: Generate content for TRMNL e-ink display devices using the TRMNL CSS framework. Use when the user wants to display information on their TRMNL device, send messages to an e-ink display, create dashboard content, show notifications, or update their terminal display. Supports rich layouts with the TRMNL framework (flexbox, grid, tables, progress bars, typography utilities) and sends content via webhook API.
---

# TRMNL Content Generator

Generate HTML content for TRMNL e-ink display devices using the TRMNL CSS framework and webhook API.

## Quick Start Workflow

1. Check for `$TRMNL_WEBHOOK` environment variable
2. If missing, prompt user for webhook URL
3. Confirm device type (default: TRMNL OG, 2-bit, 800x480)
4. Read relevant reference docs based on content needs
5. Generate HTML using TRMNL framework classes
6. Send via POST to webhook with `{"merge_variables": {"content": "HTML"}}`

## Device Assumptions

**Default target:** TRMNL OG
- Display: 7.5" e-ink
- Resolution: 800x480px (landscape)
- Bit depth: 2-bit (4 grayscale levels)

**Prompt user if different:** Ask about device type, resolution, or bit depth if layout requires specific capabilities (e.g., 4-bit features, larger resolution).

## Webhook Configuration

### Environment Variable (Recommended)
```bash
export TRMNL_WEBHOOK="https://trmnl.com/api/custom_plugins/{uuid}"
```

Check with: `echo $TRMNL_WEBHOOK`

### Direct Usage
If ENV variable not set, prompt user for webhook URL.

### Sending Content
```bash
curl "$TRMNL_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"merge_variables": {"content": "<div class=\"layout\">HTML</div>"}}' \
  -X POST
```

**Important:** Escape quotes in JSON strings when using cURL.

## Reference Documentation

Read these files as needed based on content requirements:

### framework-overview.md
Read when:
- First time using skill
- Need device specifications
- Understanding e-ink constraints
- Responsive breakpoints (`sm:`, `md:`, `lg:`)
- Bit-depth variants (`1bit:`, `2bit:`, `4bit:`)

### css-utilities.md
Read when needing:
- Colors (`bg--gray-40`, `text--black`)
- Typography (`value--xlarge`, `label`, `title`, `description`)
- Sizing (`w--48`, `h--full`, `w--[200px]`)
- Spacing (`p--4`, `m--8`, `gap--large`)
- Borders, rounded corners
- Visibility utilities

### layout-systems.md
Read when building:
- Flexbox layouts (`flex`, `flex--col`, `flex--center`)
- Grid layouts (`grid--cols-2`, `col--span-3`)
- Responsive layouts
- Dynamic content (Overflow, Clamp, Content Limiter engines)

### components.md
Read when using:
- Screen, View, Layout containers
- Title Bar component
- Dividers
- Rich Text blocks
- Item components (with meta/index)
- Tables
- Progress bars or dots
- Charts (Highcharts)

### webhook-api.md
Read when:
- Understanding payload format
- Using merge strategies (default, deep_merge, stream)
- Handling rate limits (12/hour free, 360/hour TRMNL+)
- Optimizing payload size (2KB limit)
- Troubleshooting errors

## Example Assets

See `assets/good-examples/` for reference implementations:
- `simple-message.html` - Centered text with divider
- `two-column-image.html` - Grid with text and image
- `task-list.html` - Item components with index
- `stats-dashboard.html` - Grid with progress bar
- `table-data.html` - Table with overflow handling

See `assets/anti-patterns.md` for common mistakes to avoid.

## Key Guidelines

### HTML Structure
- Use TRMNL framework classes over inline styles
- Wrap content in semantic containers (`layout`, `grid`, `item`)
- Use proper typography elements (`title`, `value`, `label`, `description`)
- Table cells must wrap text: `<th><span class="title">...</span></th>`

### E-ink Optimization
- Keep content concise (limited screen space)
- Use `image-dither` class for images
- Avoid animations, transformations, filters
- Use high contrast (black/white preferred)
- Apply `data-clamp="N"` to limit text lines

### Payload Management
- Minify HTML (remove whitespace): `{"merge_variables":{"content":"<div class=\"layout\">...</div>"}}`
- Keep under 2KB (free tier) or 5KB (TRMNL+)
- Use framework classes (shorter than inline styles)
- Compress large payloads if needed (see webhook-api.md)

### Responsive Design
- Mobile-first approach (styles cascade upward)
- Use breakpoint prefixes: `sm:`, `md:`, `lg:`
- Use orientation: `portrait:`, `landscape:`
- Use bit-depth variants: `1bit:`, `2bit:`, `4bit:`
- Combined: `md:portrait:4bit:gap--large`

### Images
- Must be publicly accessible URLs (https://)
- Use `image-dither` for grayscale optimization
- Consider `image--contain` or `image--cover` for sizing
- Add `rounded--large` for softer edges

### Layout Engines
- **Overflow:** Distribute items across columns with height limit
  - `data-overflow="true" data-overflow-max-height="400"`
- **Clamp:** Truncate text to N lines
  - `data-clamp="2"`
- **Content Limiter:** Auto-adjust text size when overflow
  - `data-content-limiter="true"`
- **Table Limit:** Show "and X more" for long tables
  - `data-table-limit="true"`

## Common Patterns

### Centered Message
```html
<div class="layout layout--col layout--center gap--large" style="height: 100%; padding: 40px;">
  <span class="value value--xxlarge text--center">Title</span>
  <span class="description text--center">Message</span>
</div>
```

### Two-Column with Image
```html
<div class="grid grid--cols-2 gap--xlarge" style="padding: 32px; height: 100%;">
  <div class="col col--center">
    <span class="title">Text Content</span>
  </div>
  <div class="col col--center row--end">
    <img src="https://example.com/image.png" class="image-dither rounded--large" style="max-width: 100%;" />
  </div>
</div>
```

### Stats Grid
```html
<div class="grid grid--cols-2 gap--large">
  <div class="item item--emphasis-1">
    <div class="content">
      <span class="value value--xlarge">1,247</span>
      <span class="label">Metric Name</span>
    </div>
  </div>
  <!-- Repeat for more stats -->
</div>
```

### List with Items
```html
<div class="layout layout--col gap--medium">
  <div class="item">
    <div class="meta">
      <span class="index">1</span>
    </div>
    <div class="content">
      <span class="label">Item Title</span>
      <span class="description" data-clamp="1">Description</span>
    </div>
  </div>
  <!-- More items -->
</div>
```

## Response Handling

### Success
```json
{"message": null, "merge_variables": {"content": "..."}}
```
Confirm to user that content was sent.

### Error
```json
{"message": "Error description", "merge_variables": null}
```
Inform user of the error and suggest fixes.

## Best Practices Summary

1. **Framework classes first** - Avoid inline styles when framework classes exist
2. **Read docs as needed** - Don't load all references upfront, read when relevant
3. **Test assumptions** - Confirm device type if layout relies on specific capabilities
4. **Optimize payloads** - Minify HTML, use framework classes
5. **E-ink aware** - High contrast, static content, dithered images
6. **Use layout engines** - Overflow, Clamp, Content Limiter for adaptive layouts
7. **Responsive patterns** - Mobile-first with breakpoint prefixes
8. **Check ENV first** - Look for `$TRMNL_WEBHOOK` before prompting user

## Troubleshooting

**Webhook fails:** Verify URL format, check rate limits (see webhook-api.md)
**Content doesn't display:** Check payload size (<2KB), validate JSON syntax
**Layout breaks:** Review anti-patterns.md, ensure proper framework class usage
**Images missing:** Verify public URLs, add `image-dither` class
**Text overflow:** Use `data-clamp` or Overflow engine with max-height
