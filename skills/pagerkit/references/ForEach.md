# ForEach in PagerKit

`ForEach` in PagerKit is a component for iterating over a collection to generate `PKPage` views dynamically.

## Usage

Use `ForEach` inside a `PKPagesView` to create pages from a data source. It works similarly to SwiftUI's `ForEach`.

### With Identifiable Data

If your data model conforms to `Identifiable`, you can use the simpler initializer.

```swift
import SwiftUI
import PagerKit

struct Item: Identifiable {
    let id = UUID()
    let title: String
}

struct ContentView: View {
    let items = [Item(title: "Home"), Item(title: "Profile"), Item(title: "Settings")]
    
    var body: some View {
        PKPagesView {
            ForEach(items) { item in
                PKPage {
                    Text(item.title)
                }
            }
        }
    }
}
```

### With a Custom ID Key Path

If your data is not `Identifiable`, you can provide a key path to a unique `Hashable` property.

```swift
import SwiftUI
import PagerKit

struct Item {
    let name: String
    let uniqueId: Int
}

struct ContentView: View {
    let items = [Item(name: "Home", uniqueId: 1), Item(name: "Profile", uniqueId: 2), Item(name: "Settings", uniqueId: 3)]
    
    var body: some View {
        PKPagesView {
            ForEach(items, id: \.uniqueId) { item in
                PKPage {
                    Text(item.name)
                }
            }
        }
    }
}
```

## Initializers

- `init(_:content:)`: For collections of `Identifiable` elements.
- `init(_:id:content:)`: For collections where you specify a custom identifier key path.

## Key Concepts

- **Data-driven pages**: `ForEach` allows you to create a pager whose content is driven by your app's data.
- **Dynamic content**: The pager will update automatically if the data collection changes.
- **Result Builder Integration**: `ForEach` works seamlessly within the `PKPageBuilder` result builder used by `PKPagesView`.

## Best Practices

1.  **Prefer `Identifiable`**: Whenever possible, make your data models conform to `Identifiable` for cleaner code.
2.  **Use a stable and unique ID**: The identifier you provide should be unique for each element and stable across data updates to avoid unexpected UI behavior.
3.  **Combine with static pages**: You can mix `ForEach` with static `PKPage` views inside the same `PKPagesView`.
