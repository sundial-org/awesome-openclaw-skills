#!/bin/bash
# ============================================================================
# Home Music - Whole-house music scenes via Spotify + Airfoil
# Author: Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)
# License: MIT
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPOTIFY_CMD="/Users/asteinberger/clawd/skills/spotify-applescript/spotify.sh"

# === PLAYLIST CONFIGURATION ===
# Edit these URIs to customize your music scenes
# Find URIs: Right-click playlist in Spotify → Share → Copy Spotify URI
PLAYLIST_MORNING="spotify:playlist:19n65kQ5NEKgkvSAla5IF6"  # Morning vibes
PLAYLIST_PARTY="spotify:playlist:37i9dQZF1DXaXB8fQg7xif"   # Rock Party
PLAYLIST_CHILL="spotify:playlist:37i9dQZF1DWTwnEm1IYyoj"   # Chill Lounge

# === SPEAKER CONFIGURATION ===
# All available AirPlay speakers in your home
# Names must match exactly as they appear in Airfoil (case-sensitive!)
ALL_SPEAKERS=("Computer" "Andy's M5 Macbook" "Sonos Move" "Living Room TV")

# ============================================================================
# AIRFOIL FUNCTIONS
# These functions control speaker connections and volume via AppleScript
# ============================================================================

# Connect a single speaker by name
airfoil_connect() {
    local speaker="$1"
    osascript -e "tell application \"Airfoil\" to connect to (first speaker whose name is \"$speaker\")" 2>/dev/null || true
}

# Disconnect a single speaker by name
airfoil_disconnect() {
    local speaker="$1"
    osascript -e "tell application \"Airfoil\" to disconnect from (first speaker whose name is \"$speaker\")" 2>/dev/null || true
}

# Set volume for a speaker (0.0 to 1.0)
airfoil_volume() {
    local speaker="$1"
    local volume="$2"
    osascript -e "tell application \"Airfoil\" to set (volume of (first speaker whose name is \"$speaker\")) to $volume" 2>/dev/null || true
}

# Disconnect all speakers in the ALL_SPEAKERS list
airfoil_disconnect_all() {
    for speaker in "${ALL_SPEAKERS[@]}"; do
        airfoil_disconnect "$speaker"
    done
}

# Set Airfoil's audio source to Spotify
# This ensures the right app's audio is being routed
airfoil_set_source_spotify() {
    osascript -e 'tell application "Airfoil"
        set theSource to (first application source whose name contains "Spotify")
        set current audio source to theSource
    end tell' 2>/dev/null || true
}

# Get a list of currently connected speakers
airfoil_connected_speakers() {
    osascript -e 'tell application "Airfoil" to get name of every speaker whose connected is true' 2>/dev/null || echo "None"
}

# ============================================================================
# SCENE FUNCTIONS
# Each scene configures speakers and starts a playlist
# ============================================================================

# Morning scene: Gentle start to the day
# - Sonos Move only at 40% volume
# - Morning playlist for a calm wake-up
scene_morning() {
    echo "🌅 Starting Morning scene..."
    
    # Set Airfoil source to Spotify
    airfoil_set_source_spotify
    
    # Connect Sonos Move at 40%
    airfoil_connect "Sonos Move"
    sleep 0.5
    airfoil_volume "Sonos Move" 0.4
    
    # Start playlist
    "$SPOTIFY_CMD" play "$PLAYLIST_MORNING"
    "$SPOTIFY_CMD" volume 100
    
    echo "✅ Morning: Sonos Move @ 40%, Morning Playlist"
}

# Party scene: All speakers, maximum fun
# - Every speaker in the house at 70%
# - Rock party playlist for maximum energy
scene_party() {
    echo "🎉 Starting Party scene..."
    
    # Set Airfoil source to Spotify
    airfoil_set_source_spotify
    
    # Connect all speakers at 70%
    for speaker in "${ALL_SPEAKERS[@]}"; do
        airfoil_connect "$speaker"
        sleep 0.3
        airfoil_volume "$speaker" 0.7
    done
    
    # Start playlist at full Spotify volume
    "$SPOTIFY_CMD" play "$PLAYLIST_PARTY"
    "$SPOTIFY_CMD" volume 100
    
    echo "✅ Party: All speakers @ 70%, Party Mix"
}

# Chill scene: Relaxation mode
# - Sonos Move only at 30% volume
# - Chill lounge playlist for unwinding
scene_chill() {
    echo "😌 Starting Chill scene..."
    
    # Set Airfoil source to Spotify
    airfoil_set_source_spotify
    
    # Connect Sonos Move at 30%
    airfoil_connect "Sonos Move"
    sleep 0.5
    airfoil_volume "Sonos Move" 0.3
    
    # Start playlist
    "$SPOTIFY_CMD" play "$PLAYLIST_CHILL"
    "$SPOTIFY_CMD" volume 100
    
    echo "✅ Chill: Sonos Move @ 30%, Chill Lounge"
}

# Off scene: Stop everything
# - Pause Spotify
# - Disconnect all speakers
scene_off() {
    echo "🔇 Stopping music..."
    
    # Pause Spotify
    "$SPOTIFY_CMD" pause 2>/dev/null || true
    
    # Disconnect all speakers
    airfoil_disconnect_all
    
    echo "✅ Music stopped, all speakers disconnected"
}

# Show current status: what's playing, which speakers are connected
show_status() {
    echo "🏠 Home Music Status"
    echo "===================="
    echo ""
    echo "Spotify:"
    "$SPOTIFY_CMD" status 2>/dev/null || echo "  Not playing"
    echo ""
    echo "Connected Speakers:"
    local connected
    connected=$(airfoil_connected_speakers)
    if [[ "$connected" == "None" || -z "$connected" ]]; then
        echo "  None"
    else
        echo "  $connected"
    fi
}

# ============================================================================
# MAIN - Command dispatcher
# ============================================================================
case "${1:-}" in
    morning)
        scene_morning
        ;;
    party)
        scene_party
        ;;
    chill)
        scene_chill
        ;;
    off|stop)
        scene_off
        ;;
    status)
        show_status
        ;;
    *)
        cat <<EOF
🏠 Home Music - Whole-house music scenes

Usage: home-music <scene>

Scenes:
  morning    Morning Playlist on Sonos Move (40% volume)
  party      Party Mode - all speakers at 70%
  chill      Chill Playlist on Sonos Move (30% volume)
  off        Stop music, disconnect all speakers
  status     Show current state

Examples:
  home-music morning
  home-music party
  home-music off
EOF
        exit 1
        ;;
esac
