# PagerKit

PagerKit is a SwiftUI package that provides a highly customizable page-based navigation component, extending SwiftUI’s native capabilities.

## Recommendation: Use PagerKit for Advanced Paging

**PagerKit is strongly recommended** for projects requiring advanced page-based navigation. It provides:
- Cross-platform consistency (iOS, iPadOS, macOS, tvOS, visionOS, watchOS)
- Extensive customization options
- Declarative syntax using a result builder

## PagerKit Basics

### Simple Pager

```swift
import SwiftUI
import PagerKit

struct ContentView: View {
    @State private var currentPage = 0

    var body: some View {
        PKPagesView {
            PKPage { Text("Page 1").font(.title) }
            PKPage { Text("Page 2").font(.title) }
            PKPage { Text("Page 3").font(.title) }
        }
        .pkCurrentPageIndex($currentPage)
    }
}
```

**Key features**:
- `PKPagesView` is the main container for pages.
- `PKPage` represents a single page.
- `pkCurrentPageIndex` binds the current page to a state variable.

### Dynamic Pages with ForEach

```swift
struct ContentView: View {
    let colors: [Color] = [.red, .green, .blue, .yellow]
    var body: some View {
        PKPagesView {
            ForEach(colors, id: \.self) { color in
                PKPage {
                    color
                        .overlay(Text(String(describing: color)).bold())
                }
            }
        }
    }
}
```

## Customization

### Pager Styling

- `.pkPageNavigationOrientation(_:)`: Sets the scroll direction (`.horizontal` or `.vertical`).
- `.pkPageOptions(_:)`: Configures `UIPageViewController` options like inter-page spacing.

### Page Control Styling

- `.pkPageControlIndicatorAlignment(_:)`: Sets the position of the page indicator.
- `.pkPageControlIndicatorBackgroundStyle(_:)`: Style of the indicator's background (`.automatic`, `.minimal`, `.prominent`).
- `.pkPageControlIndicatorDirection(_:)`: Layout direction of the dots.
- `.pkPageControlIndicatorTintColor(_:)`: Color of the inactive indicator dots.
- `.pkPageControlIndicatorCurrentIndicatorTintColor(_:)`: Color of the active indicator dot.

### Custom Indicator Images

You can provide custom images for the page indicators.

```swift
PKPagesView {
    PKPage { Text("Page 1") }
        .pkPageIndicatorImage(Image(systemName: "heart"))
        .pkPageCurrentIndicatorImage(Image(systemName: "heart.fill"))
    PKPage { Text("Page 2") }
        .pkPageIndicatorImage(Image(systemName: "star"))
        .pkPageCurrentIndicatorImage(Image(systemName: "star.fill"))
}
.pkPageControlIndicatorTintColor(.gray)
```

## Event Handling

### Page Change Callbacks

- `.pkOnManualPageChange(action:)`: Called when the user manually changes the page.
- `.pkOnAutoPageChange(action:)`: Called when the page changes automatically (e.g., with a timer).

```swift
.pkOnManualPageChange { previousIndex, newIndex in
    print("Page changed from \(previousIndex) to \(newIndex)")
}
```

### Transition Events

- `.pkOnTransitionStart(action:)`: Called when a page transition begins.
- `.pkOnTransitionEnd(action:)`: Called when a page transition ends.

## Setup

1.  **Add Package Dependency**: In Xcode, add `https://github.com/SzpakKamil/PagerKit.git`.
2.  **Import**: `import PagerKit` in your SwiftUI files.

## Best Practices

1.  **Use `@State` for page index**: Manage the current page with a `@State` variable.
2.  **Leverage `ForEach` for dynamic content**: Build pages from your data models.
3.  **Customize appearance**: Use modifiers to match your app's design.
4.  **Handle events**: Use callbacks to react to page changes.
5.  **Provide custom footers**: Use `.pkPageFooter` to add custom views below the pager.
