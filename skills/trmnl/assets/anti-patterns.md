# Anti-Patterns to Avoid

## 1. Excessive Inline Styles

**BAD:**
```html
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; padding: 40px; height: 480px; width: 800px;">
  <span style="font-size: 48px; font-weight: bold; text-align: center;">Title</span>
</div>
```

**GOOD:**
```html
<div class="layout layout--col layout--center gap--large" style="height: 100%; padding: 40px;">
  <span class="value value--xxlarge text--center">Title</span>
</div>
```

**Why:** Framework classes are optimized for e-ink, responsive, and token-efficient.

## 2. Hard-Coded Pixel Dimensions

**BAD:**
```html
<div style="width: 800px; height: 480px;">
  <div style="width: 400px;">Left Column</div>
  <div style="width: 400px;">Right Column</div>
</div>
```

**GOOD:**
```html
<div class="grid grid--cols-2 gap--large" style="height: 100%;">
  <div class="col">Left Column</div>
  <div class="col">Right Column</div>
</div>
```

**Why:** Different devices have different resolutions. Use responsive utilities and percentage-based sizing.

## 3. Missing Text Wrappers in Tables

**BAD:**
```html
<table class="table">
  <thead>
    <tr>
      <th>Header</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data</td>
    </tr>
  </tbody>
</table>
```

**GOOD:**
```html
<table class="table">
  <thead>
    <tr>
      <th><span class="title">Header</span></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="label">Data</span></td>
    </tr>
  </tbody>
</table>
```

**Why:** Framework expects text wrapped in semantic span elements for proper styling.

## 4. Color Values Instead of Framework Classes

**BAD:**
```html
<div style="background-color: #CCCCCC; color: #000000;">
  <span style="color: #666666;">Subtitle</span>
</div>
```

**GOOD:**
```html
<div class="bg--gray-50">
  <span class="text--black">Title</span>
  <span class="text--gray-40">Subtitle</span>
</div>
```

**Why:** Framework colors use dithering patterns optimized for e-ink displays.

## 5. Ignoring E-ink Constraints

**BAD:**
```html
<img src="color-photo.jpg" style="filter: blur(5px); transform: rotate(15deg);">
<div style="animation: pulse 2s infinite;">Animated content</div>
```

**GOOD:**
```html
<img src="photo.jpg" class="image-dither rounded--large">
<div>Static content optimized for e-ink</div>
```

**Why:** E-ink displays don't support animations, transformations, or color. Use `image-dither` for grayscale optimization.

## 6. Unescaped Quotes in cURL

**BAD:**
```bash
curl "URL" -d '{"merge_variables": {"content": "<div class="layout">Text</div>"}}'
```

**GOOD:**
```bash
curl "URL" -d '{"merge_variables": {"content": "<div class=\"layout\">Text</div>"}}'
```

**Why:** Unescaped quotes break JSON syntax.

## 7. Oversized Payloads

**BAD:**
```json
{
  "merge_variables": {
    "content": "<div class=\"layout layout--col layout--center gap--large\">\n    <span class=\"value value--xxlarge text--center\">Very long title with lots of text that makes the payload huge</span>\n    <span class=\"description text--center\">And even more verbose description text that could be much more concise</span>\n    <!-- Hundreds more lines of verbose HTML -->\n  </div>"
}
```

**GOOD:**
```json
{"merge_variables":{"content":"<div class=\"layout layout--col layout--center gap--large\"><span class=\"value value--xxlarge text--center\">Concise Title</span><span class=\"description text--center\">Brief description</span></div>"}}
```

**Why:** 2KB payload limit. Remove whitespace, keep content concise.

## 8. Missing data-clamp on Long Text

**BAD:**
```html
<span class="description">This is a very long description that will wrap to many lines and potentially break the layout or overflow the available space on the e-ink display making it unreadable.</span>
```

**GOOD:**
```html
<span class="description" data-clamp="2">This is a very long description that will wrap to many lines and potentially break the layout or overflow the available space on the e-ink display making it unreadable.</span>
```

**Why:** E-ink displays have limited space. Use `data-clamp` to truncate with ellipsis.

## 9. Generic Semantic HTML Without Framework Classes

**BAD:**
```html
<div>
  <h1>Title</h1>
  <p>Description text</p>
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</div>
```

**GOOD:**
```html
<div class="layout layout--col gap--medium">
  <span class="title">Title</span>
  <span class="description">Description text</span>
  <div class="layout layout--col gap--small">
    <div class="item">
      <span class="label">Item 1</span>
    </div>
    <div class="item">
      <span class="label">Item 2</span>
    </div>
  </div>
</div>
```

**Why:** Framework components are styled specifically for e-ink displays. Generic HTML tags may not render as expected.

## 10. Forgetting Image URLs Must Be Public

**BAD:**
```html
<img src="/local/path/image.png">
<img src="file:///Users/name/image.png">
<img src="relative/path/image.png">
```

**GOOD:**
```html
<img src="https://example.com/image.png" class="image-dither">
```

**Why:** TRMNL device needs publicly accessible URLs to fetch images. Local/relative paths won't work.

## 11. Not Using Layout Engines

**BAD:**
```html
<div>
  <div>Item 1</div>
  <div>Item 2</div>
  <!-- 50 more items that overflow the screen -->
</div>
```

**GOOD:**
```html
<div data-overflow="true"
     data-overflow-max-height="400"
     data-overflow-max-cols="3"
     data-overflow-counter="true">
  <div class="item">Item 1</div>
  <div class="item">Item 2</div>
  <!-- Items automatically distributed across columns with overflow indicator -->
</div>
```

**Why:** Overflow engine handles space constraints gracefully with "and X more" indicators.

## 12. Mixing Framework Classes with Conflicting Inline Styles

**BAD:**
```html
<div class="layout layout--center" style="display: block; text-align: left;">
  Content
</div>
```

**GOOD:**
```html
<div class="layout layout--center">
  Content
</div>
```

OR

```html
<div style="display: flex; align-items: center; justify-content: center;">
  Content
</div>
```

**Why:** Choose framework classes OR inline styles, don't mix conflicting properties. Framework classes are preferred.
