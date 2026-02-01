# PKPage

`PKPage` is the core component for creating a single page within a `PKPagesView`.

## Creating a PKPage

You create a `PKPage` by providing its content as a `@ViewBuilder` closure.

```swift
PKPage {
    VStack {
        Text("Welcome to PagerKit")
            .font(.title)
        Button("Tap Me") {
            print("Button tapped")
        }
    }
}
```

## Modifiers

`PKPage` has several modifiers to customize its behavior and appearance within the pager.

### Automatic Page Transitions

- `.pkPageDuration(_:)`: Sets a duration in seconds for the page to automatically transition to the next one. This is useful for creating slideshows.

```swift
PKPage {
    Text("This page will show for 5 seconds")
}
.pkPageDuration(5.0)
```

### Progress Indicators (UIKit)

For iOS, iPadOS, tvOS, and visionOS, you can use `UIPageControlProgress` to show a progress indicator for a page.

- `.pkPageProgress(_:)`: Takes a `UIPageControlProgress` object or a closure that returns one.

```swift
import UIKit

// ...

PKPage {
    Text("Page with progress")
}
.pkPageProgress(UIPageControlProgress(currentProgress: 0.5))
```

### Custom Indicator Images

You can set custom images for the page indicator dot for a specific page.

- `.pkPageIndicatorImage(_:)`: Sets the image for the indicator when the page is *not* active.
- `.pkPageCurrentIndicatorImage(_:)`: Sets the image for the indicator when the page is *active*.

The image type is `UIImage` on UIKit platforms and `Image` on macOS and watchOS.

```swift
PKPage { Text("Favorites") }
    .pkPageIndicatorImage(Image(systemName: "star"))
    .pkPageCurrentIndicatorImage(Image(systemName: "star.fill"))
```

### Custom Footer

- `.pkPageFooter(_:)`: Adds a custom view that appears at the bottom of the page only when it's active.

```swift
PKPage {
    Text("Page 1")
}
.pkPageFooter {
    Text("This is a custom footer for Page 1")
}
```

## Key Concepts

- **Page Content**: The `content` of a `PKPage` is a standard SwiftUI view.
- **Page-specific Customization**: Modifiers on `PKPage` allow you to define behavior (like duration) and appearance (like indicator images) on a per-page basis.
- **Platform Differences**: Some modifiers, especially those related to progress and images, have different implementations or availability depending on the platform (UIKit vs. AppKit/SwiftUI-native).

## Best Practices

1.  **Compose Complex Views**: The content of a `PKPage` can be any SwiftUI view, so you can build complex layouts inside it.
2.  **Use Per-Page Modifiers for Variety**: Create more engaging pagers by varying the duration or indicator images for different pages.
3.  **Check Platform Availability**: Be mindful of which modifiers are available on your target platforms. Use `#if os(...)` checks where necessary.
