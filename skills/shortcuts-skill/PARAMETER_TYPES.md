# Parameter Types Reference

Complete documentation of all parameter value types used in iOS Shortcuts.

Based on analysis of 200 real-world shortcuts containing 338 unique actions and 543 parameter keys.

---

## Serialization Types

These are the `WFSerializationType` values that indicate how complex values are encoded:

| Serialization Type | Description | Use Case |
|--------------------|-------------|----------|
| `WFTextTokenString` | Text with embedded variable references | Text fields that can contain variables |
| `WFTextTokenAttachment` | Single variable reference | Input parameters referencing other actions |
| `WFDictionaryFieldValue` | Dictionary with key-value pairs | HTTP headers, JSON bodies |
| `WFContentPredicateTableTemplate` | Filter conditions | Find/Filter actions |
| `WFQuantityFieldValue` | Measurement with unit | Duration, file size, etc. |
| `WFContactFieldValue` | Contact field reference | Contact properties |
| `WFTimeOffsetValue` | Time offset/duration | Time adjustments |

---

## Basic Value Types

### String
Simple text value:
```xml
<key>WFMenuPrompt</key>
<string>Choose an option</string>
```

### Integer
Whole number:
```xml
<key>WFControlFlowMode</key>
<integer>0</integer>
```

### Number (Float)
Decimal number:
```xml
<key>WFNumberActionNumber</key>
<real>30.0</real>
```

### Boolean
True/false:
```xml
<key>WFShowWorkflow</key>
<true/>
```

### Array
List of values:
```xml
<key>WFMenuItems</key>
<array>
    <string>Option 1</string>
    <string>Option 2</string>
</array>
```

### Data
Binary data (base64 in XML):
```xml
<key>WFData</key>
<data>BASE64_ENCODED_DATA</data>
```

---

## Variable Reference Types

### WFTextTokenAttachment (Single Variable Reference)

Used when a parameter accepts a single variable/output reference:

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputName</key>
        <string>Photos</string>
        <key>OutputUUID</key>
        <string>F2BEAE11-3F38-40C3-AD1F-FD48D90F9FE2</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### WFTextTokenString (Text with Variables)

Used for text fields that can contain embedded variables:

```xml
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
```

Key points:
- `￼` (U+FFFC) is the placeholder character
- `{0, 1}` means "at position 0, length 1"
- Multiple variables: `"Hello ￼, you have ￼ messages"` with `{6, 1}` and `{22, 1}`

---

## Dictionary Field Value

Used for HTTP headers, JSON bodies, and form data:

```xml
<key>WFHTTPHeaders</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFDictionaryFieldValueItems</key>
        <array>
            <dict>
                <key>WFItemType</key>
                <integer>0</integer>
                <key>WFKey</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>Content-Type</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
                <key>WFValue</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>application/json</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFDictionaryFieldValue</string>
</dict>
```

### WFItemType Values

| Value | Type |
|-------|------|
| 0 | Text/String |
| 1 | Number |
| 2 | Array |
| 3 | Dictionary |
| 4 | Boolean |

---

## Content Filter (WFContentPredicateTableTemplate)

Used by all Find/Filter actions. See [FILTERS.md](./FILTERS.md) for complete documentation.

Actions that use content filters:
- `is.workflow.actions.filter.photos`
- `is.workflow.actions.filter.files`
- `is.workflow.actions.filter.reminders`
- `is.workflow.actions.filter.calendarevents`
- `is.workflow.actions.filter.contacts`
- `is.workflow.actions.filter.notes`
- `is.workflow.actions.filter.music`
- `is.workflow.actions.filter.articles`
- `is.workflow.actions.filter.apps`
- `is.workflow.actions.conditional` (via `WFConditions`)

---

## Quantity Field Value

Used for measurements with units (duration, file size, etc.):

```xml
<key>WFDuration</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <real>5.0</real>
        <key>Unit</key>
        <string>min</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

### Common Units

| Category | Units |
|----------|-------|
| Time | `sec`, `min`, `hr`, `days` |
| Data | `bytes`, `KB`, `MB`, `GB` |
| Length | `m`, `km`, `ft`, `mi` |

---

## Named Variable Reference

For accessing named variables (not action outputs):

```xml
<key>WFVariable</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>Variable</string>
        <key>VariableName</key>
        <string>myVariable</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

---

## Special Input Types

### Magic Variable (Shortcut Input)

Reference the shortcut's input:
```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>ExtensionInput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Current Date

```xml
<key>WFDate</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentDate</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Clipboard

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>Clipboard</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

---

## App Identifier

For actions that reference apps:

```xml
<key>WFAppIdentifier</key>
<string>com.apple.safari</string>
```

Or with full app info:
```xml
<key>WFApp</key>
<dict>
    <key>BundleIdentifier</key>
    <string>com.apple.mobilesafari</string>
    <key>Name</key>
    <string>Safari</string>
    <key>TeamIdentifier</key>
    <string>0000000000</string>
</dict>
```

---

## Parameter Patterns by Action Type

### Text Actions
| Parameter | Type |
|-----------|------|
| `WFTextActionText` | string or WFTextTokenString |
| `Text` | string or WFTextTokenString |

### Control Flow Actions
| Parameter | Type |
|-----------|------|
| `GroupingIdentifier` | string (UUID) |
| `WFControlFlowMode` | integer (0=start, 1=middle, 2=end) |

### Input Parameters
| Parameter | Type |
|-----------|------|
| `WFInput` | WFTextTokenAttachment |
| `WFVariable` | WFTextTokenAttachment (named variable) |

### Photo Actions
| Parameter | Type | Notes |
|-----------|------|-------|
| `WFContentItemFilter` | WFContentPredicateTableTemplate | Filter conditions |
| `photos` | WFTextTokenAttachment | **DeletePhotos uses lowercase `photos`!** |
| `WFPhotoCount` | integer | Number of photos |

### HTTP Actions
| Parameter | Type |
|-----------|------|
| `WFURL` | string or WFTextTokenAttachment |
| `WFHTTPMethod` | string (`GET`, `POST`, `PUT`, `DELETE`) |
| `WFHTTPBodyType` | string (`JSON`, `Form`, `File`) |
| `WFHTTPHeaders` | WFDictionaryFieldValue |
| `WFJSONValues` | WFDictionaryFieldValue |
| `WFFormValues` | WFDictionaryFieldValue |

---

## Common Parameter Keys Across Actions

These parameters appear in many different actions:

| Parameter | Count | Type | Description |
|-----------|-------|------|-------------|
| `UUID` | all | string | Action's unique identifier |
| `WFInput` | 306 | variable_ref | Input from previous action |
| `GroupingIdentifier` | ~100 | string | Links control flow actions |
| `WFControlFlowMode` | ~100 | integer | Control flow position |
| `CustomOutputName` | ~50 | string | Custom name for output |
| `WFShowWorkflow` | ~30 | boolean | Show in workflow view |

---

## Type Coercion (Aggrandizements)

When you need to access a property or coerce a type:

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Aggrandizements</key>
        <array>
            <dict>
                <key>CoercionItemClass</key>
                <string>WFStringContentItem</string>
                <key>Type</key>
                <string>WFCoercionVariableAggrandizement</string>
            </dict>
        </array>
        <key>OutputName</key>
        <string>Model Response</string>
        <key>OutputUUID</key>
        <string>LLM-UUID</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Common Coercion Classes

| Class | Description |
|-------|-------------|
| `WFStringContentItem` | Coerce to text |
| `WFNumberContentItem` | Coerce to number |
| `WFBooleanContentItem` | Coerce to boolean |
| `WFDictionaryContentItem` | Coerce to dictionary |
| `WFURLContentItem` | Coerce to URL |
| `WFImageContentItem` | Coerce to image |
| `WFFileContentItem` | Coerce to file |

### Property Access (Dictionary Values)

```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>DictionaryKey</key>
        <string>fieldName</string>
        <key>Type</key>
        <string>WFDictionaryValueVariableAggrandizement</string>
    </dict>
</array>
```
