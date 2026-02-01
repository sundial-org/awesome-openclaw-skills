# PKPageControlIndicatorBackgroundStyle

`PKPageControlIndicatorBackgroundStyle` is an enum that defines the background appearance for the page control indicator in a `PKPagesView`.

## Usage

You apply the background style using the `.pkPageControlIndicatorBackgroundStyle(_:)` modifier on a `PKPagesView`.

```swift
import SwiftUI
import PagerKit

struct ContentView: View {
    var body: some View {
        PKPagesView {
            PKPage { Text("Page 1") }
            PKPage { Text("Page 2") }
        }
        .pkPageControlIndicatorBackgroundStyle(.prominent)
    }
}
```

## Cases

### `.prominent`

Displays a light grey background behind the page control dots. This makes the indicator more prominent.

### `.minimal`

Displays only the page control dots without any background.

### `.automatic`

The behavior of `.automatic` depends on the platform and user interaction:

- **iOS/iPadOS**: Shows a background only when the user is dragging the indicator.
- **macOS/watchOS/visionOS**: Behaves like `.minimal`.
- **tvOS**: Behaves like `.prominent`.

## Platform Differences

The visual representation of each style can vary across different platforms to match the native look and feel.

- On **iOS and iPadOS**, the `automatic` style provides a more interactive feel by showing the background only during a drag.
- On **macOS, watchOS, and visionOS**, where the interaction model is different, `automatic` defaults to the cleaner `minimal` look.
- on **tvOS**, `automatic` defaults to `prominent` for better visibility on a television screen.

## Best Practices

1.  **Use `.automatic` for most cases**: This provides a good default behavior that adapts to each platform's conventions.
2.  **Use `.prominent` for better visibility**: If the page control is over a complex or visually busy background, `.prominent` can improve its readability.
3.  **Use `.minimal` for a clean look**: If you want a less intrusive page control, `.minimal` is a good choice.
