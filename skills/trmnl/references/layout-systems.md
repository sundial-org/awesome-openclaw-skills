# Layout Systems Reference

## Flexbox Utilities

### Direction
- `flex flex--row` - Horizontal layout (default)
- `flex flex--col` - Vertical layout
- `flex flex--row-reverse` - Reversed horizontal
- `flex flex--col-reverse` - Reversed vertical

### Horizontal Alignment (X-axis)
- `flex--left` - Align left
- `flex--center-x` - Center horizontally
- `flex--right` - Align right

### Vertical Alignment (Y-axis)
- `flex--top` - Align top
- `flex--center-y` - Center vertically
- `flex--bottom` - Align bottom

### Container Stretch
- `flex--stretch` - All children fill container
- `flex--stretch-x` - Horizontal stretch
- `flex--stretch-y` - Vertical stretch

### Item-Level Controls
- `stretch` - Stretch in cross-axis
- `stretch-x` - Horizontal stretch
- `stretch-y` - Vertical stretch
- `no-shrink` - Prevent shrinking
- `grow` - Grow to fill space
- `shrink-0` - Prevent shrinking
- `flex-none` / `flex-initial` - Flex behavior
- `basis--[value]` - Set flex basis
- `order--[value]` - Control visual order

### Wrapping
- `flex--wrap` - Items wrap to multiple lines
- `flex--nowrap` - Single line (default)
- `flex--wrap-reverse` - Reverse wrap direction

### Main Axis Distribution
- `flex--between` - Space between items
- `flex--around` - Space around items
- `flex--evenly` - Even spacing

### Multi-Line Alignment
- `flex--content-start` - Pack to start
- `flex--content-center` - Pack to center
- `flex--content-end` - Pack to end
- `flex--content-between` - Distribute with space between
- `flex--content-around` - Distribute with space around
- `flex--content-evenly` - Distribute evenly
- `flex--content-stretch` - Stretch to fill

### Item Alignment
- `self--start` - Align item to start
- `self--center` - Center item
- `self--end` - Align item to end
- `self--stretch` - Stretch item

### Example
```html
<div class="flex flex--col flex--center-x gap--large">
  <span class="value value--xlarge">Title</span>
  <span class="description">Subtitle</span>
</div>
```

## Grid Utilities

### Column Count
- `grid--cols-{number}` - Equal-width columns
- Example: `grid--cols-2`, `grid--cols-3`, `grid--cols-4`

### Column Span
- `col--span-{number}` - Individual column width
- Example: `col--span-2` spans 2 columns

### Layout Base
- `grid` - Grid container
- `col` - Vertical layout
- `row` - Horizontal layout

### Column Positioning
- `col--start` - Align to top
- `col--center` - Center vertically
- `col--end` - Align to bottom

### Row Positioning
- `row--start` - Align to left
- `row--center` - Center horizontally
- `row--end` - Align to right

### Responsive Wrapping
- `grid--wrap` - Enable responsive wrapping
- `grid--min-{size}` - Minimum track size
  - Example: `grid--min-32`, `grid--min-56`

### Example
```html
<div class="grid grid--cols-2 gap--large">
  <div class="col col--start">
    <span class="title">Left Column</span>
  </div>
  <div class="col col--center">
    <span class="value">Right Column</span>
  </div>
</div>
```

## Columns Component

Simple balanced column layouts:

```html
<div class="columns">
  <div class="column">Content 1</div>
  <div class="column">Content 2</div>
</div>
```

Automatically distributes space evenly across columns.

## Layout Component

Flexible container using Flexbox with semantic naming:

### Base Structure
```html
<div class="layout layout--row">
  {{ Content }}
</div>
```

### Direction
- `layout--row` - Horizontal arrangement (default)
- `layout--col` - Vertical arrangement

### Alignment
- `layout--left` - Align left
- `layout--center-x` - Center horizontally
- `layout--right` - Align right
- `layout--top` - Align top
- `layout--center-y` - Center vertically
- `layout--bottom` - Align bottom
- `layout--center` - Center both axes

### Stretch
- `layout--stretch` - Stretch both axes
- `layout--stretch-x` - Horizontal stretch
- `layout--stretch-y` - Vertical stretch

### Child Utilities
- `stretch-x` - Child stretches horizontally
- `stretch-y` - Child stretches vertically

### Example
```html
<div class="layout layout--col layout--center gap--xlarge" style="height: 100%;">
  <span class="value value--xxlarge">Centered Content</span>
  <span class="label">Vertically and horizontally centered</span>
</div>
```

## Dynamic Engines

### Overflow Engine

Automatically distributes items across columns while respecting height constraints.

**Attributes:**
- `data-overflow="true"` - Activate engine
- `data-overflow-max-height="400"` - Pixel height budget
- `data-overflow-counter="true"` - Show "and X more" label
- `data-overflow-max-cols="3"` - Maximum columns
- `data-overflow-cols="2"` - Force exact column count

**Features:**
- Smart column distribution
- Group header handling (never orphaned)
- Works with Clamp engine

**Example:**
```html
<div data-overflow="true"
     data-overflow-max-height="400"
     data-overflow-max-cols="3"
     data-overflow-counter="true">
  <div class="item">Item 1</div>
  <div class="item">Item 2</div>
  <!-- More items... -->
</div>
```

### Clamp Engine

Limits text to specified lines with word-based ellipsis.

**Usage:**
- `data-clamp="N"` - Where N = line count

**Example:**
```html
<span class="description" data-clamp="2">
  Long text that will be truncated to 2 lines with ellipsis...
</span>
```

**Legacy Support:**
- `clamp--none` - Disable clamping
- `clamp--1` through `clamp--50` - Line limits

### Content Limiter

Automatically restricts content height, applies smaller typography and truncation when exceeded.

**Attributes:**
- `data-content-limiter="true"` - Enable limiting
- `data-content-max-height="[pixels]"` - Custom max height

**Behavior:**
1. Adds `content--small` class to reduce typography
2. Truncates first overflowing block using Clamp
3. Hides subsequent blocks

**Example:**
```html
<div class="richtext" data-content-limiter="true" data-content-max-height="300">
  <div class="content">
    <!-- Content that might overflow -->
  </div>
</div>
```

### Table Overflow

Limits table rows with "and X more" indicator.

**Usage:**
- `data-table-limit="true"` - Activate height constraints

**Example:**
```html
<table class="table" data-table-limit="true">
  <thead>
    <tr><th><span class="title">Header</span></th></tr>
  </thead>
  <tbody>
    <!-- Rows will be limited with overflow indicator -->
  </tbody>
</table>
```

## Responsive Patterns

### Mobile-First Approach
Styles cascade upward:
```html
<div class="flex flex--col md:flex--row lg:gap--xlarge">
  <!-- Vertical on small, horizontal on medium+ -->
</div>
```

### Orientation-Specific
```html
<div class="gap--small portrait:gap--large">
  <!-- Different gap for portrait orientation -->
</div>
```

### Bit-Depth Variants
```html
<div class="hidden 4bit:grid">
  <!-- Only show on 4-bit displays -->
</div>
```

### Combined Modifiers
```html
<div class="p--4 md:p--8 lg:p--12 portrait:p--6">
  <!-- Responsive padding with orientation variant -->
</div>
```
