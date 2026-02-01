# Complete Working Examples

Copy-paste ready examples that can be signed and imported.

## Example 1: Hello World

The simplest shortcut - displays "Hello World!".

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.gettext</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
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
                                <string>11111111-1111-1111-1111-111111111111</string>
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
    <string>Hello World</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 2: Ask User for Input

Asks user for their name and displays a greeting.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.ask</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA</string>
                <key>WFAskActionPrompt</key>
                <string>What is your name?</string>
                <key>WFInputType</key>
                <string>Text</string>
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
                            <key>{7, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Provided Input</string>
                                <key>OutputUUID</key>
                                <string>AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>Hello, ￼!</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
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
    <string>Greeting</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 3: AI Query

Asks user for a question, sends it to Apple Intelligence, and displays the response.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.ask</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB</string>
                <key>WFAskActionPrompt</key>
                <string>What would you like to ask?</string>
                <key>WFInputType</key>
                <string>Text</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.askllm</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC</string>
                <key>WFLLMModel</key>
                <string>Apple Intelligence</string>
                <key>WFGenerativeResultType</key>
                <string>Text</string>
                <key>WFLLMPrompt</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Provided Input</string>
                                <key>OutputUUID</key>
                                <string>BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB</string>
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
                                <string>Response</string>
                                <key>OutputUUID</key>
                                <string>CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC</string>
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
    <string>Ask AI</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 4: Menu Demo

Presents a menu with three options, each displaying different text.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Menu Start -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>0</integer>
                <key>WFMenuPrompt</key>
                <string>What would you like to do?</string>
                <key>WFMenuItems</key>
                <array>
                    <string>Say Hello</string>
                    <string>Say Goodbye</string>
                    <string>Tell a Joke</string>
                </array>
            </dict>
        </dict>
        <!-- Case 1 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Say Hello</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Hello there! Nice to meet you.</string>
            </dict>
        </dict>
        <!-- Case 2 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Say Goodbye</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Goodbye! See you next time.</string>
            </dict>
        </dict>
        <!-- Case 3 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Tell a Joke</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Why do programmers prefer dark mode? Because light attracts bugs!</string>
            </dict>
        </dict>
        <!-- Menu End -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>2</integer>
            </dict>
        </dict>
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
    <string>Menu Demo</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 5: Weather + AI Report

Gets current weather and uses AI to generate a friendly report.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Get Weather -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.weather.currentconditions</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>EEEEEEEE-EEEE-EEEE-EEEE-EEEEEEEEEEEE</string>
            </dict>
        </dict>
        <!-- Build Prompt -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.gettext</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</string>
                <key>WFTextActionText</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{56, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Weather Conditions</string>
                                <key>OutputUUID</key>
                                <string>EEEEEEEE-EEEE-EEEE-EEEE-EEEEEEEEEEEE</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>Generate a friendly weather report based on this data:
￼

Keep it brief and include clothing recommendations.</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
        <!-- Ask AI -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.askllm</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG</string>
                <key>WFLLMModel</key>
                <string>Apple Intelligence</string>
                <key>WFGenerativeResultType</key>
                <string>Text</string>
                <key>WFLLMPrompt</key>
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
                                <string>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</string>
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
        <!-- Show Result -->
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
                                <string>Response</string>
                                <key>OutputUUID</key>
                                <string>GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG</string>
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
    <string>Weather Report</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## How to Use These Examples

1. **Copy** the XML content
2. **Save** to a file with `.shortcut` extension (e.g., `HelloWorld.shortcut`)
3. **Sign** using the shortcuts CLI:
   ```bash
   shortcuts sign --mode anyone --input HelloWorld.shortcut --output HelloWorld_signed.shortcut
   ```
4. **Import** by double-clicking the signed file or dragging to Shortcuts.app
