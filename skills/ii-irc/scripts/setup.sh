#!/bin/bash
# ii-IRC setup script — creates management script and mention watcher
# Usage: bash setup.sh --server irc.example.org --port 6667 --nick MyBot --channel "#mychannel"

set -euo pipefail

# Defaults
SERVER=""
PORT="6667"
NICK=""
CHANNEL=""
IRC_DIR="$HOME/irc"

usage() {
    echo "Usage: $0 --server SERVER --nick NICK --channel CHANNEL [--port PORT] [--dir DIR]"
    echo ""
    echo "Options:"
    echo "  --server   IRC server hostname (required)"
    echo "  --nick     Bot nickname (required)"
    echo "  --channel  Channel to join, e.g. '#mychannel' (required)"
    echo "  --port     Server port (default: 6667)"
    echo "  --dir      IRC directory (default: ~/irc)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --server)  SERVER="$2"; shift 2 ;;
        --port)    PORT="$2"; shift 2 ;;
        --nick)    NICK="$2"; shift 2 ;;
        --channel) CHANNEL="$2"; shift 2 ;;
        --dir)     IRC_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

[[ -z "$SERVER" ]] && { echo "Error: --server is required"; usage; }
[[ -z "$NICK" ]] && { echo "Error: --nick is required"; usage; }
[[ -z "$CHANNEL" ]] && { echo "Error: --channel is required"; usage; }

# Check ii is installed
if ! command -v ii &>/dev/null; then
    echo "Error: ii is not installed. Install it first:"
    echo "  Arch: sudo pacman -S ii"
    echo "  Debian/Ubuntu: sudo apt install ii"
    echo "  Source: https://tools.suckless.org/ii/"
    exit 1
fi

mkdir -p "$IRC_DIR"

echo "Creating IRC scripts in $IRC_DIR..."

# --- irc.sh ---
cat > "$IRC_DIR/irc.sh" << SCRIPT
#!/bin/bash
# IRC manager — controls ii and the mention watcher
# Usage: ./irc.sh [start|stop|status|restart|send MESSAGE]

IRC_DIR="$IRC_DIR"
SERVER="$SERVER"
PORT="$PORT"
NICK="$NICK"
CHANNEL="$CHANNEL"
CHANNEL_IN="\$IRC_DIR/\$SERVER/\$CHANNEL/in"

case "\${1:-status}" in
    start)
        if ! pgrep -f "ii -s \$SERVER" > /dev/null; then
            echo "Starting ii..."
            nohup ii -s "\$SERVER" -p "\$PORT" -n "\$NICK" -i "\$IRC_DIR" > /dev/null 2>&1 &
            sleep 3
            echo "/j \$CHANNEL" > "\$IRC_DIR/\$SERVER/in"
            sleep 1
            echo "ii started and joined \$CHANNEL"
        else
            echo "ii already running"
        fi

        if ! pgrep -f "watch-daemon.sh" > /dev/null; then
            echo "Starting watcher..."
            nohup "\$IRC_DIR/watch-daemon.sh" > "\$IRC_DIR/watch.log" 2>&1 &
            echo "Watcher started"
        else
            echo "Watcher already running"
        fi
        ;;

    stop)
        echo "Stopping watcher..."
        pkill -f "watch-daemon.sh" 2>/dev/null
        echo "Stopping ii..."
        pkill -f "ii -s \$SERVER" 2>/dev/null
        echo "Stopped"
        ;;

    restart)
        \$0 stop
        sleep 2
        \$0 start
        ;;

    status)
        echo "=== IRC Status ==="
        if pgrep -f "ii -s \$SERVER" > /dev/null; then
            echo "ii: running (\$(pgrep -f "ii -s \$SERVER"))"
        else
            echo "ii: stopped"
        fi

        if pgrep -f "watch-daemon.sh" > /dev/null; then
            echo "watcher: running (\$(pgrep -f "watch-daemon.sh"))"
        else
            echo "watcher: stopped"
        fi

        if [[ -f "\$IRC_DIR/\$SERVER/\$CHANNEL/out" ]]; then
            LINES=\$(wc -l < "\$IRC_DIR/\$SERVER/\$CHANNEL/out")
            echo "channel log: \$LINES lines"
            echo ""
            echo "=== Last 5 messages ==="
            tail -5 "\$IRC_DIR/\$SERVER/\$CHANNEL/out" | sed 's/^[0-9]* //'
        fi
        ;;

    send)
        shift
        if [[ -z "\$*" ]]; then
            echo "Usage: \$0 send MESSAGE"
            exit 1
        fi
        echo "\$*" > "\$CHANNEL_IN"
        echo "Sent: \$*"
        ;;

    *)
        echo "Usage: \$0 [start|stop|status|restart|send MESSAGE]"
        exit 1
        ;;
esac
SCRIPT

chmod +x "$IRC_DIR/irc.sh"

# --- watch-daemon.sh ---
cat > "$IRC_DIR/watch-daemon.sh" << SCRIPT
#!/bin/bash
# Continuous IRC watcher for ii — triggers OpenClaw on mentions
# Usage: ./watch-daemon.sh (run in background or as a service)

IRC_DIR="$IRC_DIR"
CHANNEL_OUT="\$IRC_DIR/$SERVER/$CHANNEL/out"
NICK="$NICK"

echo "Starting IRC watcher for \$NICK mentions..."
echo "Watching: \$CHANNEL_OUT"

tail -n 0 -F "\$CHANNEL_OUT" 2>/dev/null | while read -r line; do
    # Skip own messages
    if echo "\$line" | grep -q "<\$NICK>"; then
        continue
    fi

    # Skip join/part/mode messages about ourselves
    if echo "\$line" | grep -qE "^[0-9]+ -!- \$NICK"; then
        continue
    fi

    # Check for mentions (case insensitive)
    if echo "\$line" | grep -qi "\$NICK"; then
        MSG=\$(echo "\$line" | sed 's/^[0-9]* //')
        echo "[\$(date '+%H:%M:%S')] Mention detected: \$MSG"
        openclaw system event --text "IRC mention: \$MSG" --mode now
    fi
done
SCRIPT

chmod +x "$IRC_DIR/watch-daemon.sh"

echo ""
echo "✅ Created:"
echo "  $IRC_DIR/irc.sh          (management script)"
echo "  $IRC_DIR/watch-daemon.sh (mention watcher)"
echo ""
echo "Quick start:"
echo "  $IRC_DIR/irc.sh start    # Start ii + watcher"
echo "  $IRC_DIR/irc.sh status   # Check status"
echo "  $IRC_DIR/irc.sh send 'Hello!'  # Send a message"
echo ""
echo "For auto-start on boot, create systemd user services."
echo "See SKILL.md for service file templates."
