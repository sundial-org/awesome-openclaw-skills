---
name: apple-media
description: Control Apple TV, HomePod, and AirPlay devices via pyatv (scan, stream, playback, volume, navigation).
homepage: https://github.com/aaronn/clawd-apple-media-skill
metadata: {"clawdbot":{"emoji":"🎛️","requires":{"bins":["atvremote"]},"install":[{"id":"pipx","kind":"shell","command":"pipx install pyatv --python python3.13","bins":["atvremote"],"label":"Install pyatv via pipx (Python 3.13)"}]}}
---

# Apple Media Remote

Control Apple TV, HomePod, and AirPlay devices from the command line using `atvremote`.

## Setup Notes

- pyatv has a compatibility issue with Python 3.14+. Use `--python python3.13` (or any version ≤3.13) when installing.
- If `~/.local/bin` isn't on your PATH after install, run: `pipx ensurepath`
- If your default Python is 3.14+, you can also call directly: `python3.13 -m pyatv.scripts.atvremote <command>`

## Scan for Devices

```bash
atvremote scan
atvremote --scan-hosts 10.0.0.50 scan          # Scan specific IP (faster)
atvremote --scan-hosts 10.0.0.50,10.0.0.51 scan  # Multiple IPs
```

Returns all discoverable Apple TV, HomePod, and AirPlay devices on the local network with their names, addresses, protocols, and pairing status.

## Target a Device

Use `-n <name>` (device name), `-s <ip>` (address), or `-i <id>` (identifier) to target:
```bash
atvremote -n "Kitchen" <command>
atvremote -s 10.0.0.50 <command>
atvremote -i AA:BB:CC:DD:EE:FF <command>
```

## Playback Control

```bash
atvremote -n "Kitchen" playing           # Now playing info (title, artist, album, position, etc.)
atvremote -n "Kitchen" play              # Resume playback
atvremote -n "Kitchen" pause             # Pause playback (resumable with play)
atvremote -n "Kitchen" play_pause        # Toggle play/pause
atvremote -n "Kitchen" stop              # Stop playback (ends session, cannot resume)
atvremote -n "Kitchen" next              # Next track
atvremote -n "Kitchen" previous          # Previous track
atvremote -n "Kitchen" skip_forward      # Skip forward (~10-30s, app-dependent)
atvremote -n "Kitchen" skip_backward     # Skip backward (~10-30s, app-dependent)
atvremote -n "Kitchen" skip_forward=30   # Skip forward specific seconds
atvremote -n "Kitchen" set_position=120  # Seek to position (seconds)
atvremote -n "Kitchen" set_shuffle=Songs # Shuffle: Off, Songs, Albums
atvremote -n "Kitchen" set_repeat=All    # Repeat: Off, Track, All
```

## Volume

```bash
atvremote -n "Kitchen" volume            # Get current volume (0-100)
atvremote -n "Kitchen" set_volume=50     # Set volume (0-100)
atvremote -n "Kitchen" volume_up         # Step up (~2.5%)
atvremote -n "Kitchen" volume_down       # Step down (~2.5%)
```

## Streaming

Stream local files or URLs to a device:
```bash
atvremote -n "Kitchen" stream_file=/path/to/audio.mp3   # Local file
atvremote -n "Kitchen" play_url=http://example.com/stream.mp3  # Remote URL
```

Supports common audio formats (MP3, WAV, AAC, FLAC, etc.).

## Power Management

```bash
atvremote -n "Apple TV" power_state      # Check power state
atvremote -n "Apple TV" turn_on          # Wake device
atvremote -n "Apple TV" turn_off         # Sleep device
```

## Navigation (Apple TV)

```bash
atvremote -n "Apple TV" up               # D-pad up
atvremote -n "Apple TV" down             # D-pad down
atvremote -n "Apple TV" left             # D-pad left
atvremote -n "Apple TV" right            # D-pad right
atvremote -n "Apple TV" select           # Press select/enter
atvremote -n "Apple TV" menu             # Back/menu button
atvremote -n "Apple TV" home             # Home button
atvremote -n "Apple TV" home_hold        # Long press home (app switcher)
atvremote -n "Apple TV" top_menu         # Go to main menu
atvremote -n "Apple TV" control_center   # Open control center
atvremote -n "Apple TV" guide            # Show EPG/guide
atvremote -n "Apple TV" channel_up       # Next channel
atvremote -n "Apple TV" channel_down     # Previous channel
atvremote -n "Apple TV" screensaver      # Activate screensaver
```

## Keyboard Input (Apple TV)

When a text field is focused:
```bash
atvremote -n "Apple TV" text_get                 # Get current text
atvremote -n "Apple TV" text_set="search query"  # Replace text
atvremote -n "Apple TV" text_append=" more"      # Append text
atvremote -n "Apple TV" text_clear               # Clear text
```

## App Control (Apple TV)

```bash
atvremote -n "Apple TV" app_list                          # List installed apps
atvremote -n "Apple TV" launch_app=com.apple.TVMusic      # Launch by bundle ID or URL
```

## Output Devices (Multi-room)

Manage connected audio outputs (e.g. grouping HomePods):
```bash
atvremote -n "Apple TV" output_devices                    # List current output device IDs
atvremote -n "Apple TV" add_output_devices=<device_id>    # Add speaker to group
atvremote -n "Apple TV" remove_output_devices=<device_id> # Remove from group
atvremote -n "Apple TV" set_output_devices=<device_id>    # Set specific output(s)
```

## Push Updates (Live Monitoring)

Watch for real-time playback changes:
```bash
atvremote -n "Kitchen" push_updates   # Prints updates as they occur (ENTER to stop)
```

## Pairing

Some devices (especially Apple TV) require pairing before control:
```bash
atvremote -n "Living Room" pair                   # Pair (follow PIN prompt)
atvremote -n "Living Room" --protocol airplay pair  # Pair specific protocol
atvremote wizard                                  # Interactive guided setup
```

Credentials are stored automatically in `~/.pyatv.conf` after pairing.

## Device Info

```bash
atvremote -n "Kitchen" device_info       # Model, OS version, MAC
atvremote -n "Kitchen" features          # List all supported features
atvremote -n "Kitchen" app               # Current app playing media
```

## Tips

- **Pause vs Stop:** Use `pause`/`play` to suspend and resume. `stop` ends the session entirely — playback must be restarted from the source (Siri, Home app, etc.)
- HomePods with "Pairing: NotNeeded" can be streamed to immediately
- Apple TVs typically require pairing first (all protocols the device supports)
- The `playing` command shows media type, title, artist, position, shuffle/repeat state
- For stereo HomePod pairs, target either unit by name
- Use `--scan-hosts` for faster targeting when you know the device IP
- Navigation and keyboard commands are primarily for Apple TV (not HomePod)
