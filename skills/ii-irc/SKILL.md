---
name: ii-irc
description: Persistent IRC presence using ii (minimalist file-based IRC client) with event-driven mention detection. Use when setting up an AI agent on IRC, monitoring IRC channels, sending IRC messages, or integrating OpenClaw with IRC via ii. Covers ii setup, mention watcher, systemd services, and message sending/reading.
metadata: {"openclaw":{"os":["linux"],"requires":{"bins":["ii"]},"install":[{"id":"pacman","kind":"shell","command":"sudo pacman -S ii","bins":["ii"],"label":"Install ii via pacman (Arch)"},{"id":"apt","kind":"apt","packages":["ii"],"bins":["ii"],"label":"Install ii via apt (Debian/Ubuntu)"},{"id":"source","kind":"shell","command":"git clone https://git.suckless.org/ii && cd ii && make && sudo make install","bins":["ii"],"label":"Build ii from source"}]}}
---

# ii-IRC: Event-Driven IRC for AI Agents

ii writes all channel activity to plain files. A watcher script monitors for mentions and triggers OpenClaw system events. Responses are sent by writing to a FIFO.

## Architecture

```
~/irc/
├── irc.sh              # Management script (start/stop/status/send)
├── watch-daemon.sh     # Mention watcher → openclaw system event
└── <server>/
    └── <channel>/
        ├── in          # FIFO - write here to send messages
        └── out         # Append-only log of all channel messages
```

## Quick Setup

### 1. Install ii

ii is in most package managers. On Arch: `pacman -S ii`. On Debian/Ubuntu: `apt install ii`. Or build from [suckless.org](https://tools.suckless.org/ii/).

### 2. Create scripts

Run the bundled setup script (creates `~/irc/irc.sh` and `~/irc/watch-daemon.sh`):

```bash
bash scripts/setup.sh --server irc.example.org --port 6667 --nick MyBot --channel "#mychannel"
```

Or create them manually — see `scripts/irc.sh.template` and `scripts/watch-daemon.sh.template`.

### 3. Create systemd user services (recommended)

For auto-start on boot:

```bash
mkdir -p ~/.config/systemd/user

# IRC connection service
cat > ~/.config/systemd/user/irc-bot.service << 'EOF'
[Unit]
Description=IRC connection (ii)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/ii -s SERVER -p PORT -n NICK -i %h/irc
ExecStartPost=/bin/bash -c 'sleep 3 && echo "/j CHANNEL" > %h/irc/SERVER/in'
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Mention watcher service
cat > ~/.config/systemd/user/irc-watcher.service << 'EOF'
[Unit]
Description=IRC mention watcher
After=irc-bot.service
Wants=irc-bot.service

[Service]
Type=simple
ExecStart=%h/irc/watch-daemon.sh
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Replace SERVER, PORT, NICK, CHANNEL in the service files, then:
systemctl --user daemon-reload
systemctl --user enable --now irc-bot.service irc-watcher.service
```

## Sending Messages

```bash
# Via the management script
~/irc/irc.sh send "Hello, world!"

# Or write directly to the FIFO
echo "Hello, world!" > ~/irc/<server>/<channel>/in
```

**Important:** ii splits long messages at byte boundaries, which can break mid-word or mid-UTF8 character. Keep messages under ~400 characters. For longer content, split into multiple messages with brief pauses between them.

## Reading Context

```bash
# Last N messages (token-efficient)
tail -n 20 ~/irc/<server>/<channel>/out

# Quick status (last 5 messages)
~/irc/irc.sh status
```

**Never** read the entire `out` file — it grows indefinitely. Always use `tail` with a limit.

## How Mention Detection Works

1. `watch-daemon.sh` runs `tail -F` on the channel's `out` file
2. Each new line is checked (case-insensitive) for the bot's nick
3. Own messages and join/part notices are skipped
4. On match → `openclaw system event --text "IRC mention: <message>" --mode now`
5. OpenClaw wakes and can respond via the `in` FIFO

This is event-driven — zero polling, instant response, minimal resource usage.

## Joining Multiple Channels

ii supports multiple channels on the same server. For each additional channel:

```bash
echo "/j #other-channel" > ~/irc/<server>/in
```

To watch multiple channels, either run separate watcher instances or modify `watch-daemon.sh` to monitor multiple `out` files.

## Troubleshooting

- **Not connecting:** Check `ii` is running (`pgrep -f "ii -s"`), verify server/port
- **Not joining channel:** The `in` FIFO must exist; check `ExecStartPost` timing (increase sleep if needed)
- **Mentions not triggering:** Verify watcher is running (`pgrep -f watch-daemon`), check nick matches
- **Messages splitting weirdly:** Shorten messages; ii has a ~512 byte IRC protocol limit
- **Reconnection:** systemd `Restart=always` handles this; ii exits on disconnect, systemd restarts it
