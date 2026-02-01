# PagerKit Reference Index

Quick navigation for all PagerKit topics.

## Overview

This index provides a comprehensive guide to the reference files for the PagerKit library. Use the tables and links below to quickly find the information you need.

## File Index

| File | Lines | Description |
|------|-------|-------------|
| `PagerKit.md` | 117 | The main overview of the PagerKit library, including setup and basic concepts. |
| `PKPagesView.md` | 69 | The core container view for creating a pager, with details on its many modifiers. |
| `PKPage.md` | 91 | The component for creating a single page, with its specific modifiers. |
| `ForEach.md` | 80 | How to dynamically generate pages from a data collection. |
| `PKPageBuilder.md` | 73 | The result builder that powers the declarative syntax of `PKPagesView`. |
| `PKPageControlBackgroundStyle.md` | 54 | Enum for customizing the indicator's background appearance. |
| `PKPageControlDirection.md` | 58 | Enum for controlling the layout direction of the indicator dots. |
| `PKPageDirection.md` | 49 | Enum that represents the direction of a page transition. |

## Core Components

| Topic | Description | See Also |
|-------|-------------|----------|
| **PagerKit** | The main entry point. Learn how to install and get started. | `PagerKit.md` |
| **PKPagesView** | The container that holds all your pages. This is where most customization is done. | `PKPagesView.md` |
| **PKPage** | Represents a single page within your `PKPagesView`. | `PKPage.md`|
| **ForEach** | Use this to create pages dynamically from a list of data. | `ForEach.md` |
| **PKPageBuilder** | The "magic" behind the scenes that lets you use `if` statements and `ForEach`. | `PKPageBuilder.md`|

## Customization Topics

| Topic | Description | See Also |
|-------|-------------|----------|
| **Indicator Background** | Change the visual style of the page indicator's background. | `PKPageControlBackgroundStyle.md` |
| **Indicator Direction** | Change the layout of the indicator dots (e.g., from horizontal to vertical). | `PKPageControlDirection.md` |
| **Transition Direction**| Understand the direction of a page change in event callbacks. | `PKPageDirection.md` |

## Quick Links by Problem

### "I need to..."

- **Get started with PagerKit** → `PagerKit.md`
- **Create a simple pager with a few pages** → `PKPagesView.md`, `PKPage.md`
- **Create pages from an array of data** → `ForEach.md`
- **Use `if` statements to conditionally show pages** → `PKPageBuilder.md`
- **Bind the current page to a `@State` variable** → `PKPagesView.md`
- **Handle page change events** → `PKPagesView.md`
- **Change the scroll direction (e.g., to vertical)** → `PKPagesView.md`
- **Customize the look of the indicator dots** (color, position, background) → `PKPagesView.md`, `PKPageControlBackgroundStyle.md`
- **Change the layout of the indicator dots to be vertical** → `PKPageControlDirection.md`
- **Customize a single page** (e.g., set a timer, or a custom dot image) → `PKPage.md`

### "I want to understand..."

- **The overall architecture of PagerKit** → `PagerKit.md`
- **The difference between `PKPage` and `PKPagesView`** → `PagerKit.md`, `PKPage.md`, `PKPagesView.md`
- **How the declarative syntax (`if`, `ForEach`) works** → `PKPageBuilder.md`
- **What the `PKPageDirection` in the callback means** → `PKPageDirection.md`