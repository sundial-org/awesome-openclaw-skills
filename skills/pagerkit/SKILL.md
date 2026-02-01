---
name: PagerKit
description: 'Expert guidance on PagerKit, a SwiftUI library for advanced, customizable page-based navigation. Use when developers mention: (1) PagerKit, PKPagesView, PKPage, (2) custom page controls, indicators, or paging behavior, (3) cross-platform SwiftUI paging, (4) dynamic page generation, (5) integrating page views into custom layouts, (6) specific PagerKit modifiers or enums, (7) page view controller options, (8) event handling for page changes.'
---
# PagerKit Skill

## Overview

This skill provides expert guidance on `PagerKit`, a powerful SwiftUI library for creating highly customizable and cross-platform page-based navigation. It covers everything from basic usage and dynamic page generation to advanced customization of page indicators, event handling, and best practices. Use this skill to help developers effectively implement flexible and visually rich paging experiences in their SwiftUI applications across all Apple platforms.

## Agent Behavior (Follow These Rules)

1.  **Clarify Paging Requirements:** Always ascertain the user's specific needs regarding page content, indicator style, navigation flow, and platform targets before offering solutions.
2.  **Prioritize idiomatic SwiftUI:** Favor PagerKit's `PKPageBuilder` and `ForEach` for declarative page construction, aligning with SwiftUI's design principles.
3.  **Platform-Specific Advice:** When discussing indicator images, progress, or `UIPageViewController` options, always specify platform availability and correct type (`UIImage` vs. `Image`, `UIPageControlProgress`).
4.  **Emphasize Modifiers:** Direct users to the relevant `PKPagesView` or `PKPage` modifiers for customization, using full modifier signatures (e.g., `.pkPageNavigationOrientation(_:)`).
5.  **Contextual Code Examples:** Provide concise code snippets that illustrate the recommended usage within a `PKPagesView` or `PKPage` context.
6.  **Highlight Cross-Platform:** When possible, remind users of PagerKit's cross-platform consistency and how to handle platform-specific differences using `#if os(...)` directives.

## Project Settings

PagerKit's behavior is influenced by the project's deployment targets and Swift version.

-   **Deployment Targets:** PagerKit supports iOS 14.0+, iPadOS 14.0+, macOS 14.0+, tvOS 14.0+, visionOS 1.0+, and watchOS 10.0+. Some features (e.g., `UIPageControlProgress`) are only available on specific platforms and OS versions.
-   **Swift Version:** Requires Swift 5.9+.

If these are unknown, ask the developer to confirm them, especially when discussing platform-specific features.

## Quick Decision Tree

When a developer needs PagerKit guidance, follow this decision tree:

1.  **Setting up a new pager?**
    *   For basic installation and concepts → `references/PagerKit.md`
    *   To define the overall pager structure → `references/PKPagesView.md`
    *   To create individual page content → `references/PKPage.md`

2.  **Generating pages dynamically from data?**
    *   Using a collection of items → `references/ForEach.md`

3.  **Controlling page flow or structure?**
    *   Adding conditional pages (if/else) → `references/PKPageBuilder.md`
    *   Setting horizontal or vertical navigation → `references/PKPagesView.md` (`.pkPageNavigationOrientation`)

4.  **Customizing the page indicator (dots)?**
    *   Changing color (active/inactive) → `references/PKPagesView.md` (`.pkPageControlIndicatorTintColor`, `.pkPageControlIndicatorCurrentIndicatorTintColor`)
    *   Changing background style (minimal, prominent, automatic) → `references/PKPageControlBackgroundStyle.md`
    *   Adjusting position or spacing → `references/PKPagesView.md` (`.pkPageControlIndicatorAlignment`, `.pkPageControlPadding`)
    *   Setting layout direction (e.g., vertical alignment) → `references/PKPageControlDirection.md`
    *   Using custom images (global or per-page) → `references/PKPagesView.md`, `references/PKPage.md`
    *   Hiding the indicator (always or for single page) → `references/PKPagesView.md`

5.  **Handling page change events or state?**
    *   Binding to the current page index → `references/PKPagesView.md` (`.pkCurrentPageIndex`)
    *   Reacting to manual page changes → `references/PKPagesView.md` (`.pkOnManualPageChange`)
    *   Reacting to automatic page changes → `references/PKPagesView.md` (`.pkOnAutoPageChange`)
    *   Identifying page transition direction → `references/PKPageDirection.md`
    *   Actions on transition start/end → `references/PKPagesView.md`

6.  **Customizing individual page behavior?**
    *   Setting automatic transition duration → `references/PKPage.md` (`.pkPageDuration`)
    *   Adding a custom footer to a page → `references/PKPage.md` (`.pkPageFooter`)

## Triage-First Playbook 

-   **"My pages are not showing or look incorrect."**
    *   Verify `PKPagesView` contains valid `PKPage` instances. Refer to `references/PKPagesView.md`, `references/PKPage.md`.
    *   If using dynamic content, check `ForEach` implementation. Refer to `references/ForEach.md`.
-   **"The page indicator is not positioned or styled correctly."**
    *   Examine `.pkPageControlIndicatorAlignment`, `.pkPageControlIndicatorBackgroundStyle`, `.pkPageControlIndicatorDirection` modifiers on `PKPagesView`. Refer to `references/PKPagesView.md`, `references/PKPageControlBackgroundStyle.md`, `references/PKPageControlDirection.md`.
-   **"I want to change the color of the active dot, but it's not working."**
    *   Ensure `.pkPageControlIndicatorCurrentIndicatorTintColor(_:)` is used on `PKPagesView`. Refer to `references/PKPagesView.md`.
-   **"Pages are not transitioning automatically."**
    *   Check if `.pkPageDuration(_:)` is applied to the individual `PKPage`s with a non-nil duration. Refer to `references/PKPage.md`.
-   **"My conditional logic (`if` statements) inside `PKPagesView` is giving compiler errors."**
    *   Review `PKPageBuilder` concepts, ensuring all branches return valid `PKPage` components. Refer to `references/PKPageBuilder.md`.
-   **"How can I tell if the user swiped forward or backward?"**
    *   Use the `PKPageDirection` parameter in `.pkOnManualPageChange`. Refer to `references/PKPagesView.md`, `references/PKPageDirection.md`.

## Core Patterns Reference

### Basic Pager Setup

```swift
PKPagesView {
    PKPage { Text("Page A").font(.title) }
    PKPage { Text("Page B").font(.title) }
    PKPage { Text("Page C").font(.title) }
}
.pkCurrentPageIndex($currentPage) // Bind to @State
.pkPageNavigationOrientation(.horizontal)
```

### Dynamic Pages with ForEach

```swift
struct Item: Identifiable {
    let id = UUID()
    let title: String
}

// ... inside a View
let items = [Item(title: "Item 1"), Item(title: "Item 2")]

PKPagesView {
    ForEach(items) { item in
        PKPage { Text(item.title) }
            .pkPageFooter { Text("Footer for \(item.title)") }
    }
}
```

### Custom Page Indicator Styling

```swift
.pkPageControlIndicatorAlignment(spacing: 10, alignment: .bottomTrailing)
.pkPageControlIndicatorBackgroundStyle(.prominent)
.pkPageControlIndicatorDirection(.topToBottom) // Vertical dots
.pkPageControlIndicatorTintColor(.gray)
.pkPageControlIndicatorCurrentIndicatorTintColor(.blue)
// Custom images
#if os(iOS)
.pkPageControlIndicatorPreferredCurrentPageIndicatorImage(UIImage(systemName: "star.fill"))
#else
.pkPageControlIndicatorPreferredCurrentPageIndicatorImage(Image(systemName: "star.fill"))
#endif
```

### Handling Page Change Events

```swift
.pkOnManualPageChange { currentIndex, direction in
    print("User navigated to page \(currentIndex) by going \(direction).")
}
.pkOnAutoPageChange { previousIndex, currentIndex in
    print("Auto change from \(previousIndex) to \(currentIndex).")
}
.pkOnTransitionEnd { previous, current in
    print("Transition ended. Was on \(previous), now on \(current).")
}
```

## Integration Quick Guide

PagerKit is integrated via Swift Package Manager.

1.  **Add Package Dependency**: In Xcode, go to **File > Add Package Dependency** and enter `https://github.com/SzpakKamil/PagerKit.git`.
2.  **Import**: `import PagerKit` in your Swift files.
3.  **Deployment Targets**: Ensure your project targets iOS 14.0+, iPadOS 14.0+, macOS 14.0+, tvOS 14.0+, visionOS 1.0+, or watchOS 10.0+ (Swift 5.9+).

For detailed setup, see `references/PagerKit.md`.

## Reference Files

Load these files as needed for specific topics:

-   **`PagerKit.md`** - General overview, setup, and core benefits.
-   **`PKPagesView.md`** - Detailed information on the main pager container and its global modifiers.
-   **`PKPage.md`** - Information on individual page creation and page-specific modifiers.
-   **`ForEach.md`** - How to generate pages from collections of data.
-   **`PKPageBuilder.md`** - Understanding the declarative content building for `PKPagesView`.
-   **`PKPageControlBackgroundStyle.md`** - Options for the background style of the page indicator.
-   **`PKPageControlDirection.md`** - Options for the layout direction of the page indicator dots.
-   **`PKPageDirection.md`** - Understanding the direction of page transitions.
-   **`_index.md`** - A comprehensive index for all PagerKit reference documentation.

## Best Practices Summary

1.  **Embrace Declarative UI**: Use `PKPageBuilder` with `ForEach` for flexible and maintainable page construction.
2.  **Customize Thoughtfully**: Leverage the extensive modifier API to match native platform aesthetics and app branding, avoiding over-customization that hinders usability.
3.  **Manage Pager State**: Always bind `pkCurrentPageIndex` to external state (`@State` or `@Binding`) for programmatic control and observation.
4.  **Implement Event Handling**: Utilize callbacks (e.g., `.pkOnManualPageChange`, `.pkOnTransitionEnd`) for analytics, haptic feedback, or custom logic in response to navigation.
5.  **Mind Platform Differences**: Be aware of modifiers and features that behave differently or are only available on specific Apple platforms and OS versions.
6.  **Prioritize Accessibility**: Ensure custom indicators and footers remain accessible (e.g., with VoiceOver support).


**Note**: This skill is based on the comprehensive documentation for PagerKit. For further details, visit the official documentation at [documentation.kamilszpak.com/documentation/pagerkit/](https://documentation.kamilszpak.com/documentation/pagerkit/) or the project website at [kamilszpak.com/pl/pagerkit](https://kamilszpak.com/pl/pagerkit).
