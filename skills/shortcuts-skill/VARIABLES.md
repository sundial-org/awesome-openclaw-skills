# Variable Reference System

How to pass data between actions in Shortcuts.

## Overview

Shortcuts uses a UUID-based system for referencing output from previous actions:

1. **Source action** has a `UUID` parameter identifying its output
2. **Consuming action** references that UUID via `OutputUUID` in `attachmentsByRange`
3. The placeholder character `￼` (U+FFFC) marks where variables are inserted in text

## UUID Format

UUIDs must be:
- **Uppercase** letters
- Standard UUID format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

Example: `A1B2C3D4-E5F6-7890-ABCD-EF1234567890`

Generate with any UUID generator, just ensure uppercase.

---

## WFSerializationType Values

The `WFSerializationType` key indicates the type of value:

| Type | Description | Usage |
|------|-------------|-------|
| `WFTextTokenString` | Text with embedded variable references | Most common for text params |
| `WFTextTokenAttachment` | Single variable reference (no text) | When param is just a variable |
| `WFContentPredicateTableTemplate` | Filter/predicate definition | For filter actions |
| `WFDictionaryFieldValueItems` | Dictionary entries | For dictionary creation |

---

## attachmentsByRange Format

The `attachmentsByRange` dictionary maps character positions to variable references:

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{position, length}</key>
    <dict>
        <key>OutputUUID</key>
        <string>SOURCE-ACTION-UUID</string>
        <key>OutputName</key>
        <string>Display Name</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
</dict>
```

### Range Key Format

`{position, length}` where:
- **position**: Character index in the string (0-based)
- **length**: Always `1` (the placeholder is 1 character)

Examples:
- `{0, 1}` - Variable at start of string
- `{5, 1}` - Variable at position 5
- `{10, 1}` - Variable at position 10

---

## The Placeholder Character

The Object Replacement Character `￼` (U+FFFC, Unicode code point 65532) serves as a placeholder in the `string` value where variables are inserted.

In XML, represent it as:
- Direct character: `￼`
- Or escaped: `&#xFFFC;` or `&#65532;`

Example string with two variables:
```xml
<key>string</key>
<string>Hello ￼, the weather is ￼</string>
```

With attachments at positions 6 and 24.

---

## Complete Variable Reference Structure

### WFTextTokenString (Text with Variables)

Use when the parameter is text that may contain variable references:

```xml
<key>ParameterName</key>
<dict>
    <key>Value</key>
    <dict>
        <key>string</key>
        <string>The result is: ￼</string>
        <key>attachmentsByRange</key>
        <dict>
            <key>{16, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
                <key>OutputName</key>
                <string>Result</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

### WFTextTokenAttachment (Single Variable)

Use when the parameter is just a variable reference with no surrounding text:

```xml
<key>ParameterName</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputUUID</key>
        <string>11111111-1111-1111-1111-111111111111</string>
        <key>OutputName</key>
        <string>Text</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

---

## Type Values

The `Type` key in attachment dictionaries indicates the variable source:

| Type | Description |
|------|-------------|
| `ActionOutput` | Output from a previous action |
| `Variable` | Named variable (from Set Variable) |
| `CurrentDate` | Current date/time |
| `Clipboard` | Clipboard contents |
| `Ask` | Ask When Run |
| `ExtensionInput` | Shortcut input |
| `DeviceDetails` | Device information |

Example with CurrentDate:
```xml
<dict>
    <key>Type</key>
    <string>CurrentDate</string>
</dict>
```

---

## Aggrandizements (Property Access)

Aggrandizements modify how a variable is accessed, like getting a property or coercing type:

```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>PropertyName</key>
        <string>Name</string>
        <key>Type</key>
        <string>WFPropertyVariableAggrandizement</string>
    </dict>
</array>
```

### Common Aggrandizement Types

#### Property Access
```xml
<dict>
    <key>PropertyName</key>
    <string>Name</string>
    <key>Type</key>
    <string>WFPropertyVariableAggrandizement</string>
</dict>
```

#### Dictionary Key Access
```xml
<dict>
    <key>DictionaryKey</key>
    <string>keyName</string>
    <key>Type</key>
    <string>WFDictionaryValueVariableAggrandizement</string>
</dict>
```

#### Type Coercion
```xml
<dict>
    <key>CoercionItemClass</key>
    <string>WFStringContentItem</string>
    <key>Type</key>
    <string>WFCoercionVariableAggrandizement</string>
</dict>
```

---

## Common Output Names

When referencing action outputs, use these common `OutputName` values:

| Action | OutputName |
|--------|------------|
| Text (gettext) | `Text` |
| Ask for Input | `Provided Input` |
| Ask LLM | `Response` |
| Get Weather | `Weather Conditions` |
| Get Current Location | `Current Location` |
| URL | `URL` |
| Get Contents of URL | `Contents of URL` |
| Number | `Number` |
| Date | `Date` |
| List | `List` |
| Dictionary | `Dictionary` |
| Repeat Each | `Repeat Item` |
| Repeat Count | `Repeat Index` |

---

## Example: Chaining Three Actions

```xml
<!-- Action 1: Get Text -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.gettext</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>11111111-1111-1111-1111-111111111111</string>
        <key>WFTextActionText</key>
        <string>Hello World</string>
    </dict>
</dict>

<!-- Action 2: Ask LLM (references Action 1) -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.askllm</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>22222222-2222-2222-2222-222222222222</string>
        <key>WFLLMPrompt</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>string</key>
                <string>Translate this to French: ￼</string>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{26, 1}</key>
                    <dict>
                        <key>OutputUUID</key>
                        <string>11111111-1111-1111-1111-111111111111</string>
                        <key>OutputName</key>
                        <string>Text</string>
                        <key>Type</key>
                        <string>ActionOutput</string>
                    </dict>
                </dict>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenString</string>
        </dict>
    </dict>
</dict>

<!-- Action 3: Show Result (references Action 2) -->
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
                        <key>OutputUUID</key>
                        <string>22222222-2222-2222-2222-222222222222</string>
                        <key>OutputName</key>
                        <string>Response</string>
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

---

## Multiple Variables in One Parameter

When a parameter contains multiple variable references:

```xml
<key>Text</key>
<dict>
    <key>Value</key>
    <dict>
        <key>string</key>
        <string>Name: ￼, Age: ￼</string>
        <key>attachmentsByRange</key>
        <dict>
            <key>{6, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>UUID-FOR-NAME</string>
                <key>OutputName</key>
                <string>Name</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>{14, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>UUID-FOR-AGE</string>
                <key>OutputName</key>
                <string>Age</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

Note: Position counting includes all characters including the placeholder `￼`.
