# AppIntents Reference

Complete catalog of all 728 AppIntent actions available in macOS/iOS.

## AppIntents vs WF*Actions

| Aspect | WF*Actions | AppIntents |
|--------|-----------|------------|
| Identifier format | `is.workflow.actions.*` | Various (e.g., `OpenAboutSettingsStaticDeepLinks`) |
| Origin | Legacy Shortcuts (pre-iOS 16) | App Intents framework (iOS 16+) |
| Invocation | Direct identifier in action | Via `WFAppIntentExecutionAction` wrapper |
| Scope | Core shortcut actions | System integrations, deep links, app extensions |

## How to Invoke AppIntents

AppIntents are invoked using the `WFAppIntentExecutionAction` wrapper:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.appintentexecution</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>AppIntentDescriptor</key>
        <dict>
            <key>BundleIdentifier</key>
            <string>com.apple.AccessibilityUtilities.AXSettingsShortcuts</string>
            <key>Name</key>
            <string>Open VoiceOver</string>
            <key>TeamIdentifier</key>
            <string>0000000000</string>
            <key>AppIntentIdentifier</key>
            <string>OpenAccessibilityVoiceOverStaticDeepLinks</string>
        </dict>
    </dict>
</dict>
```

---

## AppIntents by Category

### Settings Deep Links (34 actions)

Open specific Settings panes:

| Identifier | Title |
|------------|-------|
| `OpenAboutSettingsStaticDeepLinks` | Open About |
| `OpenAirDropSettingsStaticDeepLinks` | Open AirDrop |
| `OpenAppleIDSettingsStaticDeepLinks` | Open Apple ID |
| `OpenBatterySettingsStaticDeepLinks` | Open Battery |
| `OpenBluetoothSettingsStaticDeepLinks` | Open Bluetooth |
| `OpenDisplaySettingsStaticDeepLinks` | Open Display |
| `OpenFamilySettingsStaticDeepLinks` | Open Family |
| `OpenFocusSettingsStaticDeepLinks` | Open Focus |
| `OpenGeneralSettingsStaticDeepLinks` | Open General |
| `OpenInternetAccountsSettingsStaticDeepLinks` | Open Internet Accounts |
| `OpenKeyboardSettingsStaticDeepLinks` | Open Keyboard |
| `OpenLanguageSettingsStaticDeepLinks` | Open Language |
| `OpenNetworkSettingsStaticDeepLinks` | Open Network |
| `OpenNotificationSettingsStaticDeepLinks` | Open Notifications |
| `OpenPasswordsSettingsStaticDeepLinks` | Open Passwords |
| `OpenPrivacySettingsStaticDeepLinks` | Open Privacy |
| `OpenScreenTimeSettingsStaticDeepLinks` | Open Screen Time |
| `OpenSecuritySettingsStaticDeepLinks` | Open Security |
| `OpenSiriSettingsStaticDeepLinks` | Open Siri |
| `OpenSoftwareUpdateSettingsStaticDeepLinks` | Open Software Update |
| `OpenSoundSettingsStaticDeepLinks` | Open Sound |
| `OpenStorageSettingsStaticDeepLinks` | Open Storage |
| `OpenTrackpadSettingsStaticDeepLinks` | Open Trackpad |
| `OpenWalletSettingsStaticDeepLinks` | Open Wallet |
| `OpenWiFiSettingsStaticDeepLinks` | Open WiFi |

### Accessibility (164 actions)

Accessibility settings and controls:

| Identifier Pattern | Description |
|-------------------|-------------|
| `OpenAccessibility*StaticDeepLinks` | Open specific accessibility pane |
| `UpdateAx*EntityValueIntent` | Update accessibility setting value |
| `ToggleAx*` | Toggle accessibility feature |

Examples:
- `OpenAccessibilityVoiceOverStaticDeepLinks` - Open VoiceOver
- `OpenAccessibilityZoomStaticDeepLinks` - Open Zoom
- `OpenAccessibilitySwitchControlStaticDeepLinks` - Open Switch Control
- `UpdateAxVoiceOverSpeakingRateEntityValueIntent` - Update VoiceOver rate
- `ToggleAxVoiceOverIntent` - Toggle VoiceOver

### Clock & Alarms (23 actions)

| Identifier | Description |
|------------|-------------|
| `CreateAlarmIntent` | Create new alarm |
| `DeleteAlarmIntent` | Delete alarm |
| `ToggleAlarmIntent` | Toggle alarm on/off |
| `CreateTimerIntent` | Create timer |
| `PauseTimerIntent` | Pause timer |
| `ResumeTimerIntent` | Resume timer |
| `CancelTimerIntent` | Cancel timer |
| `StartStopwatchIntent` | Start stopwatch |
| `ResetStopwatchIntent` | Reset stopwatch |

### Calendar (5 actions)

| Identifier | Description |
|------------|-------------|
| `CreateCalendarIntent` | Create calendar |
| `DeleteCalendarIntent` | Delete calendar |
| `OpenCalendarScreenIntent` | Open calendar view |
| `CloseCalendarScreenIntent` | Close calendar |

### Reminders (12 actions)

| Identifier | Description |
|------------|-------------|
| `CreateReminderListIntent` | Create reminder list |
| `DeleteReminderListIntent` | Delete reminder list |
| `OpenReminderListIntent` | Open reminder list |
| `OpenSmartReminderListIntent` | Open smart list |
| `CompleteReminderIntent` | Complete reminder |

### Notes (8 actions)

| Identifier | Description |
|------------|-------------|
| `CreateNoteFolderIntent` | Create folder |
| `DeleteNoteFolderIntent` | Delete folder |
| `CreateNoteTagIntent` | Create tag |
| `DeleteNoteTagIntent` | Delete tag |
| `AddTagsToNotesIntent` | Add tags to notes |
| `RemoveTagsFromNotesIntent` | Remove tags |
| `PinNotesIntent` | Pin notes |
| `FindNotesIntent` | Find notes |

### Safari (18 actions)

| Identifier | Description |
|------------|-------------|
| `CreateTabIntent` | Create new tab |
| `CreatePrivateTabIntent` | Create private tab |
| `CloseTabIntent` | Close tab |
| `CreateTabGroupIntent` | Create tab group |
| `OpenTabIntent` | Open tab |
| `OpenTabGroupIntent` | Open tab group |
| `FindBookmarksIntent` | Find bookmarks |
| `FindReadingListItemsIntent` | Find reading list |
| `FindTabsIntent` | Find tabs |
| `FindTabGroupsIntent` | Find tab groups |
| `ChangeReaderModeStateIntent` | Toggle reader mode |

### Home (4 actions)

| Identifier | Description |
|------------|-------------|
| `FindHomeIntent` | Find home |
| `FindHomeDeviceIntent` | Find device |
| `FindHomeSceneIntent` | Find scene |
| `ToggleHomeAccessoryIntent` | Toggle accessory |

### Photos (24 actions)

| Identifier | Description |
|------------|-------------|
| `CreateMemoryIntent` | Create memory |
| `OpenCameraIntent` | Open camera |
| `FindPhotosIntent` | Find photos |
| `FindAlbumsIntent` | Find albums |
| `CreateAlbumIntent` | Create album |

### Music (2 actions)

| Identifier | Description |
|------------|-------------|
| `RecognizeMusicIntent` | Shazam recognition |
| `PlayMusicIntent` | Play music |

### Writing Tools (3 actions)

| Identifier | Description |
|------------|-------------|
| `ProofreadIntent` | Proofread text |
| `RewriteIntent` | Rewrite text |
| `SummarizeIntent` | Summarize text |

### Voice Memos (10 actions)

| Identifier | Description |
|------------|-------------|
| `CreateVoiceMemoFolderIntent` | Create folder |
| `DeleteVoiceMemoFolderIntent` | Delete folder |
| `OpenVoiceMemoFolderIntent` | Open folder |
| `FindVoiceMemosIntent` | Find recordings |
| `PlayVoiceMemoIntent` | Play recording |
| `DeleteVoiceMemosIntent` | Delete recordings |

### Shortcuts (8 actions)

| Identifier | Description |
|------------|-------------|
| `CreateWorkflowIntent` | Create shortcut |
| `DeleteWorkflowIntent` | Delete shortcut |
| `CreateiCloudLinkIntent` | Create iCloud link |
| `SearchShortcutsIntent` | Search shortcuts |
| `RunShortcutIntent` | Run shortcut |

### System Controls (154 actions)

Toggle and set system settings:

| Pattern | Description |
|---------|-------------|
| `Set*ModeIntent` | Set mode (silent, low power, etc.) |
| `Toggle*Intent` | Toggle setting |
| `Update*EntityValueIntent` | Update setting value |
| `Set*SettingIntent` | Set specific setting |

Examples:
- `SetLowPowerModeIntent` - Set low power mode
- `SetAirplaneModeIntent` - Set airplane mode
- `ToggleBluetoothIntent` - Toggle Bluetooth
- `SetBrightnessIntent` - Set brightness
- `SetVolumeIntent` - Set volume

### Data & Search (21 actions)

| Pattern | Description |
|---------|-------------|
| `Find*Intent` | Find/search items |
| `Get*Intent` | Get data |
| `Search*Intent` | Search for content |

Examples:
- `FindSportsEventsIntent` - Find sports events
- `GetPhysicalActivityIntent` - Get physical activity
- `SearchFilesIntent` - Search files

---

## Complete AppIntent Identifier List

All 728 AppIntent identifiers organized alphabetically by prefix:

### Open* (Settings Deep Links)
```
OpenAboutSettingsStaticDeepLinks, OpenAccessibilityAudioDescriptionsStaticDeepLinks,
OpenAccessibilityAudioStaticDeepLinks, OpenAccessibilityCaptionsStaticDeepLinks,
OpenAccessibilityDisplayStaticDeepLinks, OpenAccessibilityHearingDevicesStaticDeepLinks,
OpenAccessibilityHoverTextStaticDeepLinks, OpenAccessibilityKeyboardStaticDeepLinks,
OpenAccessibilityLiveCaptionsStaticDeepLinks, OpenAccessibilityLiveSpeechStaticDeepLinks,
OpenAccessibilityMotionStaticDeepLinks, OpenAccessibilityPersonalVoiceStaticDeepLinks,
OpenAccessibilityPointerControlStaticDeepLinks, OpenAccessibilityRootStaticDeepLinks,
OpenAccessibilityRTTStaticDeepLinks, OpenAccessibilityShortcutStaticDeepLinks,
OpenAccessibilitySiriStaticDeepLinks, OpenAccessibilitySpokenContentStaticDeepLinks,
OpenAccessibilitySwitchControlStaticDeepLinks, OpenAccessibilityVocalShortcutsStaticDeepLinks,
OpenAccessibilityVoiceControlStaticDeepLinks, OpenAccessibilityVoiceOverStaticDeepLinks,
OpenAccessibilityZoomStaticDeepLinks
```

### Create* (Creation Actions)
```
CreateAlarmIntent, CreateAlbumIntent, CreateCalendarIntent, CreateEventIntent,
CreateMemoryIntent, CreateNoteFolderIntent, CreateNoteTagIntent, CreateReminderIntent,
CreateReminderListIntent, CreateTabGroupIntent, CreateTabIntent, CreateTimerIntent,
CreateVoiceMemoFolderIntent, CreateWorkflowIntent
```

### Toggle* (Toggle Actions)
```
ToggleAlarmIntent, ToggleAxAssistiveTouchIntent, ToggleAxAudioDescriptionsIntent,
ToggleAxClosedCaptioningIntent, ToggleAxColorFiltersIntent, ToggleAxFullKeyboardAccessIntent,
ToggleAxGuidedAccessIntent, ToggleAxInvertColorsIntent, ToggleAxLiveListenIntent,
ToggleAxReduceMotionIntent, ToggleAxReduceTransparencyIntent, ToggleAxSpeakScreenIntent,
ToggleAxSwitchControlIntent, ToggleAxVoiceControlIntent, ToggleAxVoiceOverIntent,
ToggleAxZoomIntent, ToggleBluetoothIntent, ToggleCellularDataIntent,
ToggleDoNotDisturbIntent, ToggleFocusModeIntent, ToggleHomeAccessoryIntent,
ToggleLowPowerModeIntent, ToggleOrientationLockIntent, ToggleWiFiIntent
```

### Set* (Setting Actions)
```
SetAirplaneModeIntent, SetAlwaysOnDisplayIntent, SetAppearanceIntent,
SetBrightnessIntent, SetCellularDataIntent, SetFlashlightIntent,
SetListeningModeIntent, SetLowPowerModeIntent, SetNightShiftIntent,
SetOrientationLockIntent, SetPersonalHotspotIntent, SetStageManagerIntent,
SetTrueToneIntent, SetVolumeIntent, SetWiFiIntent
```

### Find* (Search Actions)
```
FindAlbumsIntent, FindBookmarksIntent, FindCalendarEventsIntent,
FindContactsIntent, FindFilesIntent, FindHomeDeviceIntent, FindHomeIntent,
FindHomeRoomIntent, FindHomeSceneIntent, FindNotesIntent, FindPhotosIntent,
FindReadingListItemsIntent, FindRemindersIntent, FindSportsEventsIntent,
FindTabGroupsIntent, FindTabsIntent, FindVoiceMemosIntent
```

---

## Invocation Template

To invoke any AppIntent:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.appintentexecution</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>AppIntentDescriptor</key>
        <dict>
            <key>BundleIdentifier</key>
            <string>BUNDLE_ID</string>
            <key>Name</key>
            <string>DISPLAY_NAME</string>
            <key>AppIntentIdentifier</key>
            <string>APPINTENT_IDENTIFIER</string>
        </dict>
        <!-- Additional parameters as needed -->
    </dict>
</dict>
```

Common Bundle Identifiers:
- `com.apple.AccessibilityUtilities.AXSettingsShortcuts` - Accessibility
- `com.apple.Preferences` - Settings
- `com.apple.clock` - Clock
- `com.apple.mobilenotes` - Notes
- `com.apple.reminders` - Reminders
- `com.apple.Safari` - Safari
- `com.apple.Home` - Home
- `com.apple.Photos` - Photos
