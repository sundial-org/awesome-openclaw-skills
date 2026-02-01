# PKPageDirection

`PKPageDirection` is an enum that represents the direction of a page transition in a `PKPagesView`.

## Usage

You don't typically create `PKPageDirection` instances directly. Instead, you receive them as parameters in some of the `PKPagesView` event handling modifiers, such as `.pkOnManualPageChange`.

```swift
import SwiftUI
import PagerKit

struct ContentView: View {
    @State private var currentPage = 0
    
    var body: some View {
        PKPagesView(selection: $currentPage) {
            PKPage { Text("Page 1") }
            PKPage { Text("Page 2") }
            PKPage { Text("Page 3") }
        }
        .pkOnManualPageChange { index, direction in
            print("User navigated to page \(index) by going \(direction).")
        }
    }
}
```

## Cases

### `.forward`

Represents a transition to the next page in the sequence (e.g., from page 1 to page 2).

### `.reverse`

Represents a transition to the previous page in the sequence (e.g., from page 3 to page 2).

## Key Concepts

- **Event Handling**: `PKPageDirection` is primarily used for responding to page change events. You can use it to trigger different actions or animations depending on the direction of navigation.
- **UI Feedback**: You can use the direction to provide richer UI feedback, for example, by using a different animation for forward and reverse transitions.
- **Integration with UIKit**: On platforms where PagerKit uses `UIPageViewController` (iOS, iPadOS, tvOS, visionOS), `PKPageDirection` maps to `UIPageViewController.NavigationDirection`.

## Best Practices

1.  **Use in Callbacks**: The primary use case for `PKPageDirection` is within the `action` closures of the page change callback modifiers.
2.  **Logical Branching**: Use a `switch` statement or an `if` condition on the `direction` parameter to implement direction-specific logic.
3.  **Combine with Index**: Use the `direction` in combination with the new page `index` to get a complete picture of the navigation event.
