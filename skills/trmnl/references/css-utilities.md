# CSS Utilities Reference

## Color System

### Background Colors (16 Shades)
Uses dither patterns on 1-bit displays:
- `bg--black` - Pure black
- `bg--gray-10` through `bg--gray-75` (5-point increments)
- `bg--white` - Pure white

### Text Colors (17 Shades)
- `text--black`
- `text--gray-10` through `text--gray-75`
- `text--white`

**Note:** Dark mode inverts entire screen except images.

## Typography

### Title Element
- `.title` or `.title--base` - Default heading
- `.title--small` - Compact variant

Example: `<span class="title">Heading</span>`

### Value Element (8 Sizes)
- `value--xxsmall` - Smallest
- `value--xsmall` - Secondary info
- `value--small` - Body text
- `value` or `value--base` - Standard
- `value--large` - Emphasized
- `value--xlarge` - Section headers
- `value--xxlarge` - Major headings
- `value--xxxlarge` - Hero text

**Special:** `value--tnums` - Tabular numbers (consistent width)

Example: `<span class="value value--large">$1,234.56</span>`

### Label Element
- Default - Standard size
- `label--small` - Compact
- `label--outline` - Outline style
- `label--underline` - Underline style
- `label--gray` - Gray variant
- `label--inverted` - Inverted style

Supports `data-clamp="N"` for line limiting.

### Description Element
- `.description` - Standardized descriptive text

### Text Alignment
- `text--left` (default)
- `text--center`
- `text--right`
- `text--justify`

## Sizing Utilities

### Fixed Sizes
Values: 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 80, 96

Pixel equivalents: 0px - 384px (multiply by 4)

**Width/Height**
- `w--{size}`, `h--{size}`
- Example: `w--48` = 192px width

### Arbitrary Sizes
Custom 0-800px (no responsive support):
- `w--[150px]`, `h--[225px]`

### Min/Max Dimensions
- `w--min-{size}`, `w--max-{size}`
- `h--min-{size}`, `h--max-{size}`
- Arbitrary: `w--min-[100px]`, `w--max-[400px]`

### Dynamic Sizing
- `w--full`, `h--full` - 100% width/height
- `w--auto`, `h--auto` - Automatic

## Spacing Utilities

### Margin Classes
- `m--{size}` - All sides
- `mt--{size}`, `mr--{size}`, `mb--{size}`, `ml--{size}` - Individual sides
- `mx--{size}`, `my--{size}` - Horizontal/vertical

### Padding Classes
- `p--{size}` - All sides
- `pt--{size}`, `pr--{size}`, `pb--{size}`, `pl--{size}` - Individual sides
- `px--{size}`, `py--{size}` - Horizontal/vertical

**Responsive:** All support `sm:`, `md:`, `lg:`, `portrait:` prefixes.

Example: `<div class="p--4 md:p--8 lg:p--12">`

## Gap Utilities

### Predefined Gaps
- `gap--none` - No spacing
- `gap--xsmall`, `gap--small`, `gap` or `gap--base`, `gap--medium`, `gap--large`, `gap--xlarge`, `gap--xxlarge`
- `gap--auto` - Distributes space evenly

### Arbitrary Gaps
- `gap--[10px]` - Custom 0-50px (no responsive support)

Works with `grid` and `flex` containers.

## Border Utilities

Uses grayscale dithering (1=black, 7=white, 2-6=dithered grays):
- `border--h-1` through `border--h-7` - Horizontal
- `border--v-1` through `border--v-7` - Vertical

**Note:** v2 borders NOT backward compatible with v1.

## Rounded Corners

### Base Sizes
- `rounded--none` (0px)
- `rounded--xsmall` (5px)
- `rounded--small` (7px)
- `rounded` or `rounded--base` (10px)
- `rounded--medium` (15px)
- `rounded--large` (20px)
- `rounded--xlarge` (25px)
- `rounded--xxlarge` (30px)
- `rounded--full` (9999px - pill shape)

### Arbitrary Values
- `rounded--[15px]` - Custom 0-50px (no responsive support)

### Corner-Specific
- `rounded-tl--{size}` (top-left)
- `rounded-tr--{size}` (top-right)
- `rounded-br--{size}` (bottom-right)
- `rounded-bl--{size}` (bottom-left)

### Side-Specific
- `rounded-t--{size}` (top corners)
- `rounded-r--{size}` (right corners)
- `rounded-b--{size}` (bottom corners)
- `rounded-l--{size}` (left corners)

## Visibility Utilities

### Display Classes
- `hidden` - display: none
- `visible` - display: block
- `block`, `inline`, `inline-block`
- `flex`, `inline-flex`
- `grid`
- `table`, `table-row`

**Responsive:** All support `sm:`, `md:`, `lg:` breakpoints.
**Bit-depth:** Support `1bit:`, `2bit:`, `4bit:` variants.

Example: `<div class="hidden md:block 1bit:hidden 4bit:flex">`

## Aspect Ratio (Beta)

- `aspect--auto` - No constraints
- `aspect--1/1` - Square
- `aspect--4/3`, `aspect--3/2`, `aspect--16/9`, `aspect--21/9`
- `aspect--3/4`, `aspect--2/3`, `aspect--9/16`, `aspect--9/21`

## Image Utilities

### Dithering
- `image-dither` - Grayscale illusion on 1-bit displays

### Object Fit
- `image--fill` - Stretch to fill
- `image--contain` - Maintain aspect, fit within
- `image--cover` - Maintain aspect, fill space (clips)

### Image Stroke
Widths: `image-stroke` (default 1.5px), `image-stroke--small` (1px), `image-stroke--base` (1.5px), `image-stroke--medium` (2px), `image-stroke--large` (2.5px), XL (3px)

Colors: White (default), `image-stroke--black`

## Text Stroke

**Limitation:** Works ONLY on pure black or white text.

### Width Modifiers
- `text-stroke` - Default 3.5px white
- `text-stroke--small` (2px)
- `text-stroke--base` (3.5px)
- `text-stroke--medium` (4.5px)
- `text-stroke--large` (6px)
- `text-stroke--xlarge` (7.5px)

### Colors
16 shades: black, gray-10 through gray-75, white.

## Outline Utility

- `outline` - Pixel-perfect rounded border
  - 1-bit: Dithered 9-slice PNG
  - 2-bit/4-bit: 1px solid border with 10px radius

- `screen--backdrop` - Alternative for patterned backgrounds

## Scale Utilities (Beta)

Applied to `screen` element via `--ui-scale` CSS variable:

- `screen--scale-xsmall` (0.75) - Maximum density
- `screen--scale-small` (0.875) - Increased density
- `screen--scale-regular` (1.0) - Default
- `screen--scale-large` (1.125) - Enhanced readability
- `screen--scale-xlarge` (1.25) - Large scale
- `screen--scale-xxlarge` (1.5) - Accessibility-focused

**Scales:** Font sizes, line heights, component dimensions, spacing.
**Doesn't scale:** Fixed pixel values, screen dimensions.
