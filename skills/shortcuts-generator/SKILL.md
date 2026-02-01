---
name: shortcuts-generator
description: Generate macOS/iOS Shortcuts by creating plist files. Use when asked to create shortcuts, automate workflows, build .shortcut files, or generate Shortcuts plists. Covers 1,155 actions (427 WF*Actions + 728 AppIntents), variable references, and control flow.
allowed-tools: Write, Bash
---

# macOS Shortcuts Generator

Generate valid `.shortcut` files that can be signed and imported into Apple's Shortcuts app.

## Quick Start

A shortcut is a binary plist with this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Actions go here -->
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>My Shortcut</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

### Minimal Hello World

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.gettext</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</string>
        <key>WFTextActionText</key>
        <string>Hello World!</string>
    </dict>
</dict>
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.showresult</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>Text</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{0, 1}</key>
                    <dict>
                        <key>OutputName</key>
                        <string>Text</string>
                        <key>OutputUUID</key>
                        <string>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</string>
                        <key>Type</key>
                        <string>ActionOutput</string>
                    </dict>
                </dict>
                <key>string</key>
                <string>￼</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenString</string>
        </dict>
    </dict>
</dict>
```

## Core Concepts

### 1. Actions
Every action has:
- **Identifier**: `is.workflow.actions.<name>` (e.g., `is.workflow.actions.showresult`)
- **Parameters**: Action-specific configuration in `WFWorkflowActionParameters`
- **UUID**: Unique identifier for referencing this action's output

### 2. Variable References
To use output from a previous action:
1. The source action needs a `UUID` parameter
2. Reference it using `OutputUUID` in an `attachmentsByRange` dictionary
3. Use `￼` (U+FFFC) as placeholder in the string where the variable goes
4. Set `WFSerializationType` to `WFTextTokenString`

### 3. Control Flow
Control flow actions (repeat, conditional, menu) use:
- `GroupingIdentifier`: UUID linking start/middle/end actions
- `WFControlFlowMode`: 0=start, 1=middle (else/case), 2=end

## Common Actions Quick Reference

| Action | Identifier | Key Parameters |
|--------|------------|----------------|
| Text | `is.workflow.actions.gettext` | `WFTextActionText` |
| Show Result | `is.workflow.actions.showresult` | `Text` |
| Ask for Input | `is.workflow.actions.ask` | `WFAskActionPrompt`, `WFInputType` |
| Use AI Model | `is.workflow.actions.askllm` | `WFLLMPrompt`, `WFLLMModel`, `WFGenerativeResultType` |
| Comment | `is.workflow.actions.comment` | `WFCommentActionText` |
| URL | `is.workflow.actions.url` | `WFURLActionURL` |
| Get Contents of URL | `is.workflow.actions.downloadurl` | `WFURL`, `WFHTTPMethod` |
| Get Weather | `is.workflow.actions.weather.currentconditions` | (none required) |
| Open App | `is.workflow.actions.openapp` | `WFAppIdentifier` |
| Open URL | `is.workflow.actions.openurl` | `WFInput` |
| Alert | `is.workflow.actions.alert` | `WFAlertActionTitle`, `WFAlertActionMessage` |
| Notification | `is.workflow.actions.notification` | `WFNotificationActionTitle`, `WFNotificationActionBody` |
| Set Variable | `is.workflow.actions.setvariable` | `WFVariableName`, `WFInput` |
| Get Variable | `is.workflow.actions.getvariable` | `WFVariable` |
| Number | `is.workflow.actions.number` | `WFNumberActionNumber` |
| List | `is.workflow.actions.list` | `WFItems` |
| Dictionary | `is.workflow.actions.dictionary` | `WFItems` |
| Repeat (count) | `is.workflow.actions.repeat.count` | `WFRepeatCount`, `GroupingIdentifier`, `WFControlFlowMode` |
| Repeat (each) | `is.workflow.actions.repeat.each` | `WFInput`, `GroupingIdentifier`, `WFControlFlowMode` |
| If/Otherwise | `is.workflow.actions.conditional` | `WFInput`, `WFCondition`, `GroupingIdentifier`, `WFControlFlowMode` |
| Choose from Menu | `is.workflow.actions.choosefrommenu` | `WFMenuPrompt`, `WFMenuItems`, `GroupingIdentifier`, `WFControlFlowMode` |
| Find Photos | `is.workflow.actions.filter.photos` | `WFContentItemFilter` (see FILTERS.md) |
| Delete Photos | `is.workflow.actions.deletephotos` | `photos` (**NOT** `WFInput`!) |

## Detailed Reference Files

For complete documentation, see:
- [PLIST_FORMAT.md](PLIST_FORMAT.md) - Complete plist structure
- [ACTIONS.md](ACTIONS.md) - All 427 WF*Action identifiers and parameters
- [APPINTENTS.md](APPINTENTS.md) - All 728 AppIntent actions
- [PARAMETER_TYPES.md](PARAMETER_TYPES.md) - All parameter value types and serialization formats
- [VARIABLES.md](VARIABLES.md) - Variable reference system
- [CONTROL_FLOW.md](CONTROL_FLOW.md) - Repeat, Conditional, Menu patterns
- [FILTERS.md](FILTERS.md) - Content filters for Find/Filter actions (photos, files, etc.)
- [EXAMPLES.md](EXAMPLES.md) - Complete working examples

## Signing Shortcuts

Shortcuts MUST be signed before they can be imported. Use the macOS `shortcuts` CLI:

```bash
# Sign for anyone to use
shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut_signed.shortcut

# Sign for people who know you
shortcuts sign --mode people-who-know-me --input MyShortcut.shortcut --output MyShortcut_signed.shortcut
```

The signing process:
1. Write your plist as XML to a `.shortcut` file
2. Run `shortcuts sign` to add cryptographic signature (~19KB added)
3. The signed file can be opened/imported into Shortcuts.app

## Workflow for Creating Shortcuts

1. **Define actions** - List what the shortcut should do
2. **Generate UUIDs** - Each action that produces output needs a unique UUID
3. **Build action array** - Create each action dictionary with identifier and parameters
4. **Wire variable references** - Connect outputs to inputs using `OutputUUID`
5. **Wrap in plist** - Add the root structure with icon, name, version
6. **Write to file** - Save as `.shortcut` (XML plist format is fine)
7. **Sign** - Run `shortcuts sign` to make it importable

## Key Rules

1. **UUIDs must be uppercase**: `A1B2C3D4-E5F6-7890-ABCD-EF1234567890`
2. **WFControlFlowMode is an integer**: Use `<integer>0</integer>` not `<string>0</string>`
3. **Range keys use format**: `{position, length}` - e.g., `{0, 1}` for first character
4. **The placeholder character**: `￼` (U+FFFC) marks where variables are inserted
5. **Control flow needs matching ends**: Every repeat/if/menu start needs an end action with same `GroupingIdentifier`
