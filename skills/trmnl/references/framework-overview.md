# TRMNL Framework Overview

## What is TRMNL?

TRMNL (pronounced "terminal") is an open-source e-ink adaptive front-end framework for e-paper displays. Automatically adapts across 1-bit (2 shades), 2-bit (4 shades), and 4-bit (16 shades) color depths with graceful degradation.

## Device Specifications

### TRMNL OG (Original 7.5")
- **Display:** 7.5" e-ink
- **Resolution:** 800x480px (landscape default)
- **Bit depth:** 2-bit (4 grayscale levels)
- **Battery:** 1800-2500mAh (2-6 months life)
- **Weight:** 170g

### TRMNL X (10.3")
- **Display:** 10.3" high-density e-ink
- **Resolution:** 1872x1404px
- **Bit depth:** 4-bit (16 grayscale levels)
- **Refresh:** ≤1.2s full, ≤200ms partial
- **Battery:** 6000-12000mAh (2-6 months)
- **Features:** Waterproof, accelerometer, gesture controls

## Bit Depth Support

**1-bit (Monochrome)**
- 2 shades (black/white only)
- Uses dithering patterns for grayscale illusion
- Variant prefix: `1bit:`

**2-bit (Grayscale)**
- 4 levels of gray
- TRMNL OG default
- Variant prefix: `2bit:`

**4-bit (High-fidelity)**
- 16 levels of grayscale
- TRMNL X, Kindle 2024, some Kobo devices
- Variant prefix: `4bit:`

## E-ink Constraints

**Refresh Characteristics**
- Slower than LCD/OLED
- Full refresh prevents ghosting
- Partial refresh faster but can ghost
- Recommendation: Full refresh every 5 partial refreshes

**Ghosting Management**
- Traces of previous images linger without full refresh
- Store with white pattern when not in use
- Different refresh modes balance speed vs quality

**Performance Considerations**
- Low power design prioritizes battery over speed
- Device wakes periodically (configurable minutes)
- Server generates 1-bit or 2-bit PNG images
- Device renders then sleeps

## Responsive Breakpoints

Mobile-first approach, styles cascade upward:

| Prefix | Min Width | Example Device |
|--------|-----------|----------------|
| `sm:` | 600px | Kindle 2024 |
| `md:` | 800px | TRMNL OG |
| `lg:` | 1024px | TRMNL V2 |

**Orientation**
- `portrait:` prefix for portrait-specific styles
- Landscape is default
- `screen--portrait` swaps width/height (480x800)

**Combined Pattern**
```
size:orientation:bit-depth:utility
```
Example: `md:portrait:4bit:gap--large`

## Best Practices

**For E-ink Displays**
- Use dithering for images (`image-dither` class)
- Avoid animations (disable in charts)
- Keep content concise
- Use clear typography with good contrast
- Prefer black/white, limit mid-grays

**Optimization**
- Framework calculates space dynamically
- Avoid hard-coded pixel values where possible
- Use utility classes over inline styles
- Leverage Overflow/Clamp engines for adaptive layouts

**Size Limits**
- JSON payload: 2KB (free), 5KB (TRMNL+)
- Rate limit: 12 requests/hour (free), 360/hour (TRMNL+)

## CSS Variables

Available for custom styling:
- `--screen-w`, `--screen-h` - Screen dimensions
- `--full-w`, `--full-h` - Dimensions minus padding
- `--ui-scale` - UI scaling factor (0.75-1.5)
- `--color-depth` - Display bit depth
- `--gap` - Base gap value
