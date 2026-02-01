# PKPageControlIndicatorDirection

`PKPageControlIndicatorDirection` is an enum that specifies the layout direction for the page control indicator's dots in a `PKPagesView`.

## Usage

You apply the direction using the `.pkPageControlIndicatorDirection(_:)` modifier on a `PKPagesView`.

```swift
import SwiftUI
import PagerKit

struct ContentView: View {
    var body: some View {
        PKPagesView {
            PKPage { Text("Page 1") }
            PKPage { Text("Page 2") }
        }
        .pkPageControlIndicatorDirection(.topToBottom)
        .pkPageControlIndicatorAlignment(.leading) // Often used with vertical directions
    }
}
```

## Cases

### Horizontal Directions

- **`.natural`**: The default. Adapts to the system's layout direction (left-to-right or right-to-left).
- **`.leftToRight`**: Always lays out the dots from left to right.
- **`.rightToLeft`**: Always lays out the dots from right to left.

### Vertical Directions

- **`.topToBottom`**: Lays out the dots vertically from top to bottom.
- **`.bottomToTop`**: Lays out the dots vertically from bottom to top.

## Combining with Alignment

When using a vertical direction, you will likely want to change the alignment of the indicator to a vertical edge of the screen, such as `.leading` or `.trailing`.

```swift
// Example of a vertical indicator on the left side
.pkPageControlIndicatorDirection(.topToBottom)
.pkPageControlIndicatorAlignment(spacing: 20, alignment: .leading)
```

## Platform Availability

- The vertical directions (`.topToBottom`, `.bottomToTop`) are available on all platforms.
- On iOS 16.0+ and tvOS 16.0+, these directions map to the native `UIPageControl.Direction` properties.

## Best Practices

1.  **Use `.natural` for standard UIs**: It provides the most conventional and expected user experience.
2.  **Use vertical directions for custom layouts**: Vertical indicators are great for sidebars or other non-standard pager designs.
3.  **Adjust alignment for vertical directions**: Ensure the indicator is positioned correctly when using a vertical layout.
4.  **Consider Readability**: Ensure your chosen direction and alignment don't interfere with the content of your pages.
