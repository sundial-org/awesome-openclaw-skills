# PKPageBuilder

`PKPageBuilder` is a result builder that allows you to declaratively construct a list of `PKPage` components for a `PKPagesView`.

## Overview

You don't use `PKPageBuilder` directly. Instead, it's the technology that powers the closure-based syntax of `PKPagesView`. It allows you to mix and match different ways of creating pages in a natural, SwiftUI-like way.

## Features

`PKPageBuilder` supports:

- **Multiple pages**: Simply list your `PKPage` views.
- **Conditional pages**: Use `if` and `if-else` statements.
- **Optional pages**: Use `if let` to include pages based on optional data.
- **Platform-specific pages**: Use `#if` or `if #available`.
- **Pages from arrays**: `ForEach` is also supported through the builder.

## Examples

### Mixing Static and Conditional Pages

```swift
struct ContentView: View {
    @State private var showExtraPage = true

    var body: some View {
        PKPagesView {
            PKPage { Text("Welcome") }

            if showExtraPage {
                PKPage { Text("An Extra Page") }
            }

            if #available(iOS 16.0, *) {
                PKPage { Text("This page is only for iOS 16+") }
            } else {
                PKPage { Text("This is a fallback for older iOS versions") }
            }
        }
    }
}
```

### Pages from a `ForEach`

`PKPageBuilder` works with `ForEach` to dynamically generate pages from a collection.

```swift
struct ContentView: View {
    let items = ["First", "Second", "Third"]

    var body: some View {
        PKPagesView {
            ForEach(items, id: \.self) { item in
                PKPage { Text("Page: \(item)") }
            }
        }
    }
}
```

## How It Works

`PKPageBuilder` has a set of static methods that the Swift compiler uses to transform the declarative code inside the `PKPagesView` closure into a single array of `PKPage` objects. These methods include:

- `buildBlock(...)`: Combines multiple pages into one list.
- `buildEither(first:)` and `buildEither(second:)`: Handles `if-else` statements.
- `buildOptional(_:)`: Handles `if let`.
- `buildLimitedAvailability(_:)`: Handles `#available` checks.
- `buildExpression(_:)`: Handles a single page expression.

You don't need to call these methods yourself; the compiler does it for you.
