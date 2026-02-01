# Control Flow Patterns

How to implement loops, conditionals, and menus in Shortcuts.

## Overview

Control flow actions use two key parameters:
- **GroupingIdentifier**: A UUID that links related actions (start, middle, end)
- **WFControlFlowMode**: An integer indicating the action's role
  - `0` = Start (begin block)
  - `1` = Middle (else, case)
  - `2` = End (close block)

**Important**: `WFControlFlowMode` must be an `<integer>`, not a `<string>`.

---

## Repeat Count

Repeat a block of actions a specific number of times.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Start | Begin repeat, set count |
| 2 | End | Close repeat block |

### Template

```xml
<!-- Repeat Start -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>REPEAT-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFRepeatCount</key>
        <integer>5</integer>
    </dict>
</dict>

<!-- Actions inside the loop go here -->

<!-- Repeat End -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>END-ACTION-UUID</string>
        <key>GroupingIdentifier</key>
        <string>REPEAT-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Accessing Repeat Index

Inside the loop, reference the current index using the End action's UUID:

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{0, 1}</key>
    <dict>
        <key>OutputUUID</key>
        <string>END-ACTION-UUID</string>
        <key>OutputName</key>
        <string>Repeat Index</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
</dict>
```

---

## Repeat with Each (For Each)

Iterate over each item in a list.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Start | Begin loop, specify input list |
| 2 | End | Close loop |

### Template

```xml
<!-- Repeat Each Start -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.each</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>FOREACH-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>LIST-SOURCE-UUID</string>
                <key>OutputName</key>
                <string>List</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>

<!-- Actions inside the loop go here -->

<!-- Repeat Each End -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.each</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>END-ACTION-UUID</string>
        <key>GroupingIdentifier</key>
        <string>FOREACH-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Accessing Current Item

Reference the current item using the Start action's UUID with OutputName "Repeat Item":

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{0, 1}</key>
    <dict>
        <key>OutputUUID</key>
        <string>START-ACTION-UUID</string>
        <key>OutputName</key>
        <string>Repeat Item</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
</dict>
```

---

## Conditional (If/Otherwise)

Execute different actions based on a condition.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | If | Start conditional, define condition |
| 1 | Otherwise | Else branch |
| 2 | End If | Close conditional |

### Template

```xml
<!-- If -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFCondition</key>
        <string>Equals</string>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>VALUE-TO-TEST-UUID</string>
                <key>OutputName</key>
                <string>Text</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
        <key>WFConditionalActionString</key>
        <string>expected value</string>
    </dict>
</dict>

<!-- Actions for "If" branch go here -->

<!-- Otherwise -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
    </dict>
</dict>

<!-- Actions for "Otherwise" branch go here -->

<!-- End If -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Condition Types

| WFCondition Value | Description |
|-------------------|-------------|
| `Equals` | Value equals comparison |
| `Does Not Equal` | Value does not equal |
| `Contains` | String contains substring |
| `Does Not Contain` | String does not contain |
| `Begins With` | String starts with |
| `Ends With` | String ends with |
| `Is Greater Than` | Number comparison |
| `Is Less Than` | Number comparison |
| `Is Between` | Number in range |
| `Has Any Value` | Not empty |
| `Does Not Have Any Value` | Is empty |

---

## Choose from Menu

Present a menu of options and execute different actions based on the user's choice.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Menu | Define menu with items |
| 1 | Case | One case per menu item |
| 2 | End Menu | Close menu |

### Template

```xml
<!-- Menu Definition -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFMenuPrompt</key>
        <string>Choose an option:</string>
        <key>WFMenuItems</key>
        <array>
            <string>Option 1</string>
            <string>Option 2</string>
            <string>Option 3</string>
        </array>
    </dict>
</dict>

<!-- Case 1: Option 1 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 1</string>
    </dict>
</dict>

<!-- Actions for Option 1 go here -->

<!-- Case 2: Option 2 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 2</string>
    </dict>
</dict>

<!-- Actions for Option 2 go here -->

<!-- Case 3: Option 3 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 3</string>
    </dict>
</dict>

<!-- Actions for Option 3 go here -->

<!-- End Menu -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Important Notes

1. **Case order must match WFMenuItems order** - Each case (mode 1) must appear in the same order as the items in WFMenuItems array
2. **WFMenuItemTitle must exactly match** - The case title must exactly match the corresponding item in WFMenuItems
3. **One case per item** - You need exactly one case action for each menu item

---

## Nesting Control Flow

Control flow blocks can be nested. Each nested block needs its own unique GroupingIdentifier:

```xml
<!-- Outer Repeat -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>OUTER-LOOP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFRepeatCount</key>
        <integer>3</integer>
    </dict>
</dict>

    <!-- Inner Conditional -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>0</integer>
            <!-- condition params -->
        </dict>
    </dict>

    <!-- Inner Otherwise -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>1</integer>
        </dict>
    </dict>

    <!-- Inner End If -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>2</integer>
        </dict>
    </dict>

<!-- Outer End Repeat -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>OUTER-LOOP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

---

## Common Mistakes

1. **Using string instead of integer for WFControlFlowMode**
   - Wrong: `<string>0</string>`
   - Right: `<integer>0</integer>`

2. **Mismatched GroupingIdentifier**
   - All parts of a control flow block must share the same GroupingIdentifier

3. **Missing End action**
   - Every start (mode 0) must have a corresponding end (mode 2)

4. **Wrong order in menu cases**
   - Cases must appear in the same order as WFMenuItems

5. **Referencing wrong UUID for loop items**
   - Repeat Item uses the **start** action's UUID
   - Repeat Index uses the **end** action's UUID
