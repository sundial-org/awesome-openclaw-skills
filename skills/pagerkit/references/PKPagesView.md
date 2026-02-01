# PKPagesView

`PKPagesView` is the main container view for creating a page-based navigation interface in PagerKit.

## Creating a PKPagesView

You create a `PKPagesView` and provide its content using a `@PKPageBuilder` closure, where you can list your `PKPage` instances.

```swift
import SwiftUI
import PagerKit

struct ContentView: View {
    @State private var currentPage = 0
    
    var body: some View {
        PKPagesView {
            PKPage { Text("Page 1") }
            PKPage { Text("Page 2") }
            PKPage { Text("Page 3") }
        }
        .pkCurrentPageIndex($currentPage)
    }
}
```

## Key Modifiers

`PKPagesView` offers a wide range of modifiers to customize its appearance and behavior.

### Pager Behavior

- `.pkPageNavigationOrientation(_:)`: Sets the scroll direction to `.horizontal` or `.vertical`.
- `.pkPageOptions(_:)`: Provides a dictionary of `UIPageViewController.OptionsKey` for fine-tuning behavior on UIKit platforms (e.g., `[.interPageSpacing: 20]`).

### Page Indicator Customization

- **Visibility**:
    - `.pkPageControlIndicatorHidden(_:)`: Hides the indicator entirely.
    - `.pkPageControlIndicatorHidesForSignlePage(_:)`: Hides the indicator if there's only one page.
- **Positioning**:
    - `.pkPageControlIndicatorAlignment(_:)`: Sets the alignment of the indicator (e.g., `.top`, `.bottom`, `.leading`).
    - `.pkPageControlIndicatorAlignment(spacing:alignment:)`: Sets alignment with custom spacing from the edge.
- **Styling**:
    - `.pkPageControlIndicatorBackgroundStyle(_:)`: Sets the indicator's background style (`.automatic`, `.minimal`, `.prominent`).
    - `.pkPageControlIndicatorDirection(_:)`: Sets the layout direction of the dots (`.natural`, `.topToBottom`, etc.).
- **Color**:
    - `.pkPageControlIndicatorTintColor(_:)`: Sets the color for inactive dots.
    - `.pkPageControlIndicatorCurrentIndicatorTintColor(_:)`: Sets the color for the active dot.
- **Custom Images**:
    - `.pkPageControlIndicatorPreferredIndicatorImage(image:)`: Sets a default custom image for all inactive dots.
    - `.pkPageControlIndicatorPreferredCurrentPageIndicatorImage(image:)`: Sets a default custom image for the active dot.
    - `.pkPageControlIndicator(_:forPage:)`: Sets a custom image for the inactive dot of a *specific* page.
    - `.pkPageControlIndicatorCurrentIndicator(_:forPage:)`: Sets a custom image for the active dot of a *specific* page.

### Event Handling & State Binding

- `.pkCurrentPageIndex(index:)`: Creates a two-way binding to a `@State` variable that holds the current page index.
- `.pkOnManualPageChange(action:)`: A callback for when the user manually swipes or taps to change the page.
- `.pkOnAutoPageChange(action:)`: A callback for when the page changes automatically (e.g., using the `.pkPageDuration` modifier on a `PKPage`).
- `.pkOnTransitionStart(action:)`: A callback fired when a page transition begins.
- `.pkOnTransitionEnd(action:)`: A callback fired when a page transition completes.

## Best Practices

1.  **Use `@State` for the current page**: Bind the pager to a `@State` variable to control it programmatically or react to changes.
2.  **Combine modifiers**: Chain multiple modifiers to achieve the exact look and feel you want.
3.  **Use platform-specific modifiers**: Use `#if os(...)` to apply modifiers that are only available on certain platforms (like `pkPageOptions`).
4.  **Leverage event callbacks**: Use the `pkOn...` modifiers to add analytics, trigger haptic feedback, or perform other actions in response to navigation.
