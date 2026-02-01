#!/bin/bash
#
# Apple Music CLI - Search, library, and playlist management
#
# Usage: apple-music <command> [options]
#

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"

# Colors (only if terminal supports it)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    DIM='\033[2m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' DIM='' BOLD='' NC=''
fi

# API Base URL
API_BASE="https://api.music.apple.com/v1"

#─────────────────────────────────────────────────────────────────────────────
# Utility Functions
#─────────────────────────────────────────────────────────────────────────────

error() {
    echo -e "${RED}Error:${NC} $1" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}Warning:${NC} $1" >&2
}

info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Load configuration
load_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error "Not configured. Run: $SKILL_DIR/setup.sh"
    fi
    
    DEVELOPER_TOKEN=$(jq -r '.developer_token // empty' "$CONFIG_FILE" 2>/dev/null)
    MUSIC_USER_TOKEN=$(jq -r '.music_user_token // empty' "$CONFIG_FILE" 2>/dev/null)
    STOREFRONT=$(jq -r '.storefront // "us"' "$CONFIG_FILE" 2>/dev/null)
    
    if [[ -z "$DEVELOPER_TOKEN" ]] || [[ -z "$MUSIC_USER_TOKEN" ]]; then
        error "Invalid configuration. Run: $SKILL_DIR/setup.sh"
    fi
}

# Make API request
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    local url="$API_BASE$endpoint"
    local args=(-s --compressed -w "\n%{http_code}")
    
    args+=(-H "Authorization: Bearer $DEVELOPER_TOKEN")
    args+=(-H "Music-User-Token: $MUSIC_USER_TOKEN")
    args+=(-H "Content-Type: application/json")
    
    if [[ "$method" == "POST" ]]; then
        args+=(-X POST)
        if [[ -n "$data" ]]; then
            args+=(-d "$data")
        else
            # POST without body requires Content-Length: 0
            args+=(-H "Content-Length: 0")
        fi
    fi
    
    local response
    response=$(curl "${args[@]}" "$url" 2>&1)
    
    local http_code
    http_code=$(echo "$response" | tail -n1)
    local body
    body=$(echo "$response" | sed '$d')
    
    # Handle HTTP errors
    case "$http_code" in
        200|201|202|204)
            echo "$body"
            ;;
        401)
            error "Authentication failed. Your tokens may have expired.\nRun: $SKILL_DIR/setup.sh"
            ;;
        403)
            error "Forbidden. Check your Apple Music subscription status."
            ;;
        404)
            error "Resource not found. The ID may be incorrect or region-locked."
            ;;
        429)
            error "Rate limited. Please wait a moment and try again."
            ;;
        *)
            local error_msg
            error_msg=$(echo "$body" | jq -r '.errors[0].detail // .errors[0].title // "Unknown error"' 2>/dev/null || echo "HTTP $http_code")
            error "$error_msg"
            ;;
    esac
}

#─────────────────────────────────────────────────────────────────────────────
# Search Command
#─────────────────────────────────────────────────────────────────────────────

cmd_search() {
    local query=""
    local types="songs"
    local limit=10
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --type|-t)
                types="$2"
                shift 2
                ;;
            --limit|-l)
                limit="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: apple-music search [options] <query>"
                echo ""
                echo "Search the Apple Music catalog."
                echo ""
                echo "Options:"
                echo "  --type, -t <type>    Type to search: songs, albums, artists, playlists"
                echo "                       (default: songs)"
                echo "  --limit, -l <n>      Number of results (default: 10, max: 25)"
                echo ""
                echo "Examples:"
                echo "  apple-music search \"Bohemian Rhapsody\""
                echo "  apple-music search --type albums \"Abbey Road\""
                echo "  apple-music search --type artists --limit 5 \"Beatles\""
                return 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                query="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$query" ]]; then
        error "Search query required. Usage: apple-music search <query>"
    fi
    
    # URL encode the query
    local encoded_query
    encoded_query=$(printf '%s' "$query" | jq -sRr @uri)
    
    info "Searching for: $query"
    echo ""
    
    local response
    response=$(api_request "GET" "/catalog/$STOREFRONT/search?term=$encoded_query&types=$types&limit=$limit")
    
    # Parse and display results based on type
    case "$types" in
        songs)
            echo "$response" | jq -r '
                .results.songs.data // [] | 
                to_entries | 
                .[] | 
                "\(.key + 1). \(.value.attributes.name)\n   Artist: \(.value.attributes.artistName)\n   Album: \(.value.attributes.albumName)\n   ID: \(.value.id)\n"
            '
            local count
            count=$(echo "$response" | jq '.results.songs.data // [] | length')
            echo -e "${DIM}Found $count song(s)${NC}"
            ;;
        albums)
            echo "$response" | jq -r '
                .results.albums.data // [] | 
                to_entries | 
                .[] | 
                "\(.key + 1). \(.value.attributes.name)\n   Artist: \(.value.attributes.artistName)\n   Year: \(.value.attributes.releaseDate[:4] // "N/A")\n   ID: \(.value.id)\n"
            '
            local count
            count=$(echo "$response" | jq '.results.albums.data // [] | length')
            echo -e "${DIM}Found $count album(s)${NC}"
            ;;
        artists)
            echo "$response" | jq -r '
                .results.artists.data // [] | 
                to_entries | 
                .[] | 
                "\(.key + 1). \(.value.attributes.name)\n   Genres: \(.value.attributes.genreNames | join(", "))\n   ID: \(.value.id)\n"
            '
            local count
            count=$(echo "$response" | jq '.results.artists.data // [] | length')
            echo -e "${DIM}Found $count artist(s)${NC}"
            ;;
        playlists)
            echo "$response" | jq -r '
                .results.playlists.data // [] | 
                to_entries | 
                .[] | 
                "\(.key + 1). \(.value.attributes.name)\n   Curator: \(.value.attributes.curatorName // "Apple Music")\n   ID: \(.value.id)\n"
            '
            local count
            count=$(echo "$response" | jq '.results.playlists.data // [] | length')
            echo -e "${DIM}Found $count playlist(s)${NC}"
            ;;
        *)
            echo "$response" | jq '.'
            ;;
    esac
}

#─────────────────────────────────────────────────────────────────────────────
# Library Command
#─────────────────────────────────────────────────────────────────────────────

cmd_library() {
    local action="$1"
    shift || true
    
    case "$action" in
        add)
            cmd_library_add "$@"
            ;;
        ""|--help|-h)
            echo "Usage: apple-music library <action>"
            echo ""
            echo "Actions:"
            echo "  add <song-id>    Add a song to your library"
            echo ""
            echo "Examples:"
            echo "  apple-music library add 1440833098"
            return 0
            ;;
        *)
            error "Unknown library action: $action"
            ;;
    esac
}

cmd_library_add() {
    local song_id=""
    local resource_type="songs"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --type|-t)
                resource_type="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: apple-music library add [options] <id>"
                echo ""
                echo "Add a song/album to your library."
                echo ""
                echo "Options:"
                echo "  --type, -t <type>    Resource type: songs, albums (default: songs)"
                echo ""
                echo "Examples:"
                echo "  apple-music library add 1440833098"
                echo "  apple-music library add --type albums 1441164495"
                return 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                song_id="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$song_id" ]]; then
        error "Song/Album ID required. Usage: apple-music library add <id>"
    fi
    
    info "Adding $resource_type ID $song_id to library..."
    
    local data
    data=$(jq -n --arg type "$resource_type" --arg id "$song_id" '{
        data: [{
            id: $id,
            type: $type
        }]
    }')
    
    # URL-encode the brackets in ids[type]=id
    api_request "POST" "/me/library?ids%5B${resource_type}%5D=$song_id" "" > /dev/null
    
    echo -e "${GREEN}✓${NC} Added to library successfully!"
}

#─────────────────────────────────────────────────────────────────────────────
# Playlists Command
#─────────────────────────────────────────────────────────────────────────────

cmd_playlists() {
    local action="$1"
    shift || true
    
    case "$action" in
        list|ls)
            cmd_playlists_list "$@"
            ;;
        create|new)
            cmd_playlists_create "$@"
            ;;
        add)
            cmd_playlists_add "$@"
            ;;
        ""|--help|-h)
            echo "Usage: apple-music playlists <action>"
            echo ""
            echo "Actions:"
            echo "  list               List your playlists"
            echo "  create <name>      Create a new playlist"
            echo "  add <pid> <sid>    Add a song to a playlist"
            echo ""
            echo "Examples:"
            echo "  apple-music playlists list"
            echo "  apple-music playlists create \"Road Trip\""
            echo "  apple-music playlists add p.ABC123 1440833098"
            return 0
            ;;
        *)
            error "Unknown playlists action: $action"
            ;;
    esac
}

cmd_playlists_list() {
    local limit=25
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit|-l)
                limit="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: apple-music playlists list [options]"
                echo ""
                echo "List your Apple Music library playlists."
                echo ""
                echo "Options:"
                echo "  --limit, -l <n>    Number of results (default: 25)"
                return 0
                ;;
            *)
                shift
                ;;
        esac
    done
    
    info "Fetching your playlists..."
    echo ""
    
    local response
    response=$(api_request "GET" "/me/library/playlists?limit=$limit")
    
    echo "$response" | jq -r '
        .data // [] | 
        to_entries | 
        .[] | 
        "\(.key + 1). \(.value.attributes.name)\n   Tracks: \(.value.attributes.trackCount // "?")\n   ID: \(.value.id)\n"
    '
    
    local count
    count=$(echo "$response" | jq '.data // [] | length')
    echo -e "${DIM}Showing $count playlist(s)${NC}"
}

cmd_playlists_create() {
    local name=""
    local description=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --description|-d)
                description="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: apple-music playlists create [options] <name>"
                echo ""
                echo "Create a new playlist in your library."
                echo ""
                echo "Options:"
                echo "  --description, -d <text>    Playlist description"
                echo ""
                echo "Examples:"
                echo "  apple-music playlists create \"Road Trip\""
                echo "  apple-music playlists create \"Workout\" -d \"High energy songs\""
                return 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                name="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$name" ]]; then
        error "Playlist name required. Usage: apple-music playlists create <name>"
    fi
    
    info "Creating playlist: $name"
    
    local data
    if [[ -n "$description" ]]; then
        data=$(jq -n --arg name "$name" --arg desc "$description" '{
            attributes: {
                name: $name,
                description: $desc
            }
        }')
    else
        data=$(jq -n --arg name "$name" '{
            attributes: {
                name: $name
            }
        }')
    fi
    
    local response
    response=$(api_request "POST" "/me/library/playlists" "$data")
    
    local playlist_id
    playlist_id=$(echo "$response" | jq -r '.data[0].id // empty')
    
    if [[ -n "$playlist_id" ]]; then
        echo -e "${GREEN}✓${NC} Playlist created!"
        echo "   Name: $name"
        echo "   ID: $playlist_id"
    else
        echo -e "${GREEN}✓${NC} Playlist created: $name"
    fi
}

cmd_playlists_add() {
    local playlist_id=""
    local song_id=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                echo "Usage: apple-music playlists add <playlist-id> <song-id>"
                echo ""
                echo "Add a song to a playlist."
                echo ""
                echo "Arguments:"
                echo "  playlist-id    Your library playlist ID (e.g., p.ABC123)"
                echo "  song-id        Catalog song ID (e.g., 1440833098)"
                echo ""
                echo "Examples:"
                echo "  apple-music playlists add p.ABC123 1440833098"
                return 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                if [[ -z "$playlist_id" ]]; then
                    playlist_id="$1"
                elif [[ -z "$song_id" ]]; then
                    song_id="$1"
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$playlist_id" ]] || [[ -z "$song_id" ]]; then
        error "Both playlist ID and song ID required.\nUsage: apple-music playlists add <playlist-id> <song-id>"
    fi
    
    info "Adding song $song_id to playlist $playlist_id..."
    
    local data
    data=$(jq -n --arg id "$song_id" '{
        data: [{
            id: $id,
            type: "songs"
        }]
    }')
    
    api_request "POST" "/me/library/playlists/$playlist_id/tracks" "$data" > /dev/null
    
    echo -e "${GREEN}✓${NC} Song added to playlist!"
}

#─────────────────────────────────────────────────────────────────────────────
# Playback Control (AppleScript - no API setup required)
#─────────────────────────────────────────────────────────────────────────────

cmd_player() {
    local subcommand="${1:-}"
    shift || true
    
    case "$subcommand" in
        play)
            if [[ $# -gt 0 ]]; then
                # Play specific playlist or search term
                local target="$*"
                osascript -e "tell application \"Music\" to play playlist \"$target\"" 2>/dev/null || \
                osascript -e "tell application \"Music\" to play" 2>/dev/null || \
                error "Could not play: $target"
            else
                osascript -e 'tell application "Music" to play'
            fi
            echo -e "${GREEN}▶${NC} Playing"
            ;;
        song)
            # Search library and play a specific song
            if [[ $# -eq 0 ]]; then
                error "Specify a song name. Example: apple-music player song Blinding Lights"
            fi
            local query="$*"
            local result
            result=$(osascript -e "tell application \"Music\"
                set searchResults to (search library playlist 1 for \"$query\" only songs)
                if (count of searchResults) > 0 then
                    play item 1 of searchResults
                    set t to item 1 of searchResults
                    return name of t & \" - \" & artist of t
                else
                    return \"NOT_FOUND\"
                end if
            end tell" 2>/dev/null)
            if [[ "$result" == "NOT_FOUND" ]]; then
                error "Song not found in library: $query"
            else
                echo -e "${GREEN}▶${NC} Now playing: $result"
            fi
            ;;
        id|catalog)
            # Play a song by Apple Music catalog ID (adds to library first, then plays)
            if [[ $# -eq 0 ]]; then
                error "Specify a song ID. Example: apple-music player id 1581102728"
            fi
            local song_id="$1"
            
            # Check if config exists for API call
            if [[ ! -f "$CONFIG_FILE" ]]; then
                error "API not configured. Run setup.sh first to play by catalog ID."
            fi
            
            # Load config for API
            load_config
            
            # First, get song info from catalog
            info "Fetching song info..."
            local song_info
            song_info=$(api_request "GET" "/catalog/$STOREFRONT/songs/$song_id" "" 2>/dev/null) || {
                error "Could not find song with ID: $song_id"
            }
            
            local song_name artist_name
            song_name=$(echo "$song_info" | jq -r '.data[0].attributes.name // empty' 2>/dev/null)
            artist_name=$(echo "$song_info" | jq -r '.data[0].attributes.artistName // empty' 2>/dev/null)
            
            if [[ -z "$song_name" ]]; then
                error "Could not get song details for ID: $song_id"
            fi
            
            info "Adding \"$song_name\" by $artist_name to library..."
            
            # Add to library using the API directly
            local encoded_ids
            encoded_ids=$(printf '%s' "ids[songs]=${song_id}" | sed 's/\[/%5B/g; s/\]/%5D/g')
            api_request "POST" "/me/library?${encoded_ids}" "" > /dev/null 2>&1 || true
            
            # Wait for library sync (Apple Music needs time to index)
            info "Waiting for library sync..."
            sleep 3
            
            # Search library by song name and play
            local result
            result=$(osascript -e "tell application \"Music\"
                set searchResults to (search library playlist 1 for \"$song_name\" only songs)
                if (count of searchResults) > 0 then
                    play item 1 of searchResults
                    set t to item 1 of searchResults
                    return name of t & \" - \" & artist of t
                else
                    return \"NOT_FOUND\"
                end if
            end tell" 2>/dev/null)
            
            if [[ "$result" == "NOT_FOUND" ]]; then
                warn "Song added but couldn't auto-play. Try: apple-music player song \"$song_name\""
            else
                echo -e "${GREEN}▶${NC} Now playing: $result"
            fi
            ;;
        pause)
            osascript -e 'tell application "Music" to pause'
            echo -e "${YELLOW}⏸${NC} Paused"
            ;;
        toggle)
            osascript -e 'tell application "Music" to playpause'
            echo -e "${CYAN}⏯${NC} Toggled play/pause"
            ;;
        next|skip)
            osascript -e 'tell application "Music" to next track'
            sleep 0.5
            cmd_player now
            ;;
        prev|previous|back)
            osascript -e 'tell application "Music" to previous track'
            sleep 0.5
            cmd_player now
            ;;
        shuffle)
            local current
            current=$(osascript -e 'tell application "Music" to get shuffle enabled')
            if [[ "$current" == "true" ]]; then
                osascript -e 'tell application "Music" to set shuffle enabled to false'
                echo -e "${CYAN}🔀${NC} Shuffle: OFF"
            else
                osascript -e 'tell application "Music" to set shuffle enabled to true'
                echo -e "${CYAN}🔀${NC} Shuffle: ON"
            fi
            ;;
        repeat)
            local current
            current=$(osascript -e 'tell application "Music" to get song repeat')
            case "$current" in
                off)
                    osascript -e 'tell application "Music" to set song repeat to all'
                    echo -e "${CYAN}🔁${NC} Repeat: ALL"
                    ;;
                all)
                    osascript -e 'tell application "Music" to set song repeat to one'
                    echo -e "${CYAN}🔂${NC} Repeat: ONE"
                    ;;
                one)
                    osascript -e 'tell application "Music" to set song repeat to off'
                    echo -e "${CYAN}➡️${NC} Repeat: OFF"
                    ;;
            esac
            ;;
        now|status|current)
            local info
            info=$(osascript -e 'tell application "Music"
                if player state is playing then
                    set trackName to name of current track
                    set artistName to artist of current track
                    set albumName to album of current track
                    set shuffleState to shuffle enabled
                    set repeatState to song repeat as string
                    set statusLine to "▶ " & trackName & " - " & artistName & " (" & albumName & ")"
                    if shuffleState then
                        set statusLine to statusLine & " 🔀"
                    end if
                    if repeatState is not "off" then
                        if repeatState is "one" then
                            set statusLine to statusLine & " 🔂"
                        else
                            set statusLine to statusLine & " 🔁"
                        end if
                    end if
                    return statusLine
                else if player state is paused then
                    set trackName to name of current track
                    set artistName to artist of current track
                    set albumName to album of current track
                    return "⏸ " & trackName & " - " & artistName & " (" & albumName & ")"
                else
                    return "⏹ Not playing"
                end if
            end tell' 2>/dev/null) || info="⏹ Music app not running"
            echo "$info"
            ;;
        vol|volume)
            if [[ $# -gt 0 ]]; then
                local vol="$1"
                # Validate and clamp volume to 0-100
                if ! [[ "$vol" =~ ^[0-9]+$ ]]; then
                    error "Volume must be a number between 0 and 100"
                fi
                if [[ $vol -lt 0 ]]; then
                    vol=0
                elif [[ $vol -gt 100 ]]; then
                    vol=100
                fi
                
                # Set Apple Music app volume (existing behavior)
                osascript -e "tell application \"Music\" to set sound volume to $vol"
                
                # Set macOS system output volume and unmute
                osascript -e "set volume output volume $vol"
                osascript -e "set volume without output muted"
                
                echo -e "${CYAN}🔊${NC} Volume set to $vol (app + system)"
            else
                local vol
                vol=$(osascript -e 'tell application "Music" to get sound volume')
                echo -e "${CYAN}🔊${NC} Volume: $vol"
            fi
            ;;
        --help|-h|"")
            echo "Player Control"
            echo ""
            echo "Usage: apple-music player <command>"
            echo ""
            echo "Commands (no setup required):"
            echo "  play [playlist]   Start playback (optionally specify playlist)"
            echo "  song <name>       Search library and play a specific song"
            echo "  pause             Pause playback"
            echo "  toggle            Toggle play/pause"
            echo "  next              Skip to next track"
            echo "  prev              Go to previous track"
            echo "  shuffle           Toggle shuffle on/off"
            echo "  repeat            Cycle repeat: off → all → one → off"
            echo "  now               Show current track"
            echo "  volume [0-100]    Get or set volume"
            echo ""
            echo "Commands (requires API setup):"
            echo "  id <song-id>      Play a song by Apple Music catalog ID (adds to library first)"
            ;;
        *)
            error "Unknown player command: $subcommand"
            ;;
    esac
}

#─────────────────────────────────────────────────────────────────────────────
# AirPlay Control (AppleScript - no API setup required)
#─────────────────────────────────────────────────────────────────────────────

cmd_airplay() {
    local subcommand="${1:-}"
    shift || true
    
    case "$subcommand" in
        list|devices)
            echo -e "${CYAN}ℹ${NC} AirPlay Devices:"
            echo ""
            osascript -e '
                tell application "Music"
                    set deviceList to ""
                    set deviceNum to 1
                    repeat with d in AirPlay devices
                        set deviceName to name of d
                        set isSelected to selected of d
                        if isSelected then
                            set deviceList to deviceList & deviceNum & ". " & deviceName & " ✓" & "\n"
                        else
                            set deviceList to deviceList & deviceNum & ". " & deviceName & "\n"
                        end if
                        set deviceNum to deviceNum + 1
                    end repeat
                    return deviceList
                end tell
            ' 2>/dev/null | sed '/^$/d'
            ;;
        select|set)
            if [[ $# -eq 0 ]]; then
                error "Specify device number(s) or name(s). Example: apple-music airplay select 1 2"
            fi
            # First deselect all
            osascript -e '
                tell application "Music"
                    repeat with d in AirPlay devices
                        set selected of d to false
                    end repeat
                end tell
            ' 2>/dev/null
            # Select specified devices
            for arg in "$@"; do
                if [[ "$arg" =~ ^[0-9]+$ ]]; then
                    # Select by number
                    osascript -e "tell application \"Music\" to set selected of AirPlay device $arg to true" 2>/dev/null || \
                    warn "Could not select device $arg"
                else
                    # Select by name
                    osascript -e "tell application \"Music\"
                        repeat with d in AirPlay devices
                            if name of d is \"$arg\" then
                                set selected of d to true
                            end if
                        end repeat
                    end tell" 2>/dev/null || warn "Could not select device: $arg"
                fi
            done
            echo -e "${GREEN}✓${NC} AirPlay devices updated"
            cmd_airplay list
            ;;
        add)
            if [[ $# -eq 0 ]]; then
                error "Specify device number(s) or name(s) to add"
            fi
            for arg in "$@"; do
                if [[ "$arg" =~ ^[0-9]+$ ]]; then
                    osascript -e "tell application \"Music\" to set selected of AirPlay device $arg to true" 2>/dev/null || \
                    warn "Could not add device $arg"
                else
                    osascript -e "tell application \"Music\"
                        repeat with d in AirPlay devices
                            if name of d is \"$arg\" then
                                set selected of d to true
                            end if
                        end repeat
                    end tell" 2>/dev/null || warn "Could not add device: $arg"
                fi
            done
            echo -e "${GREEN}✓${NC} Added to AirPlay"
            cmd_airplay list
            ;;
        remove)
            if [[ $# -eq 0 ]]; then
                error "Specify device number(s) or name(s) to remove"
            fi
            for arg in "$@"; do
                if [[ "$arg" =~ ^[0-9]+$ ]]; then
                    osascript -e "tell application \"Music\" to set selected of AirPlay device $arg to false" 2>/dev/null || \
                    warn "Could not remove device $arg"
                else
                    osascript -e "tell application \"Music\"
                        repeat with d in AirPlay devices
                            if name of d is \"$arg\" then
                                set selected of d to false
                            end if
                        end repeat
                    end tell" 2>/dev/null || warn "Could not remove device: $arg"
                fi
            done
            echo -e "${GREEN}✓${NC} Removed from AirPlay"
            cmd_airplay list
            ;;
        --help|-h|"")
            echo "AirPlay Control (no API setup required)"
            echo ""
            echo "Usage: apple-music airplay <command>"
            echo ""
            echo "Commands:"
            echo "  list              List AirPlay devices (✓ = active)"
            echo "  select <1> <2>    Select devices (deselects others)"
            echo "  add <1> <2>       Add devices to current selection"
            echo "  remove <1> <2>    Remove devices from selection"
            echo ""
            echo "Devices can be specified by number or name."
            ;;
        *)
            error "Unknown airplay command: $subcommand"
            ;;
    esac
}

#─────────────────────────────────────────────────────────────────────────────
# Main
#─────────────────────────────────────────────────────────────────────────────

show_help() {
    echo "Apple Music CLI"
    echo ""
    echo "Usage: apple-music <command> [options]"
    echo ""
    echo "Commands (API - requires setup):"
    echo "  search <query>          Search the Apple Music catalog"
    echo "  library add <id>        Add a song to your library"
    echo "  playlists list          List your playlists"
    echo "  playlists create <name> Create a new playlist"
    echo "  playlists add <p> <s>   Add a song to a playlist"
    echo ""
    echo "Commands (Local - no setup required):"
    echo "  player play|pause|next  Control playback"
    echo "  player now              Show current track"
    echo "  airplay list            List AirPlay devices"
    echo "  airplay select <1> <2>  Select AirPlay outputs"
    echo ""
    echo "Options:"
    echo "  --help, -h              Show help for a command"
    echo ""
    echo "Examples:"
    echo "  apple-music search \"Bohemian Rhapsody\""
    echo "  apple-music player now"
    echo "  apple-music airplay select 1 2"
    echo ""
    echo "Setup:"
    echo "  Run $SKILL_DIR/setup.sh to configure your Apple Developer credentials."
}

main() {
    local command="${1:-}"
    shift || true
    
    # Handle help and version first (no config needed)
    case "$command" in
        --help|-h|help|"")
            show_help
            exit 0
            ;;
        --version|-v)
            echo "apple-music 1.0.0"
            exit 0
            ;;
    esac
    
    # Local commands (no API config needed)
    case "$command" in
        player|play)
            if [[ "$command" == "play" ]]; then
                # Shortcut: "apple-music play" = "apple-music player play"
                cmd_player play "$@"
            else
                cmd_player "$@"
            fi
            exit 0
            ;;
        airplay)
            cmd_airplay "$@"
            exit 0
            ;;
    esac
    
    # Check if help is requested for subcommands (no config needed)
    local needs_config=true
    for arg in "$@"; do
        if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
            needs_config=false
            break
        fi
    done
    
    # Also check for empty subcommands that show help
    case "$command" in
        library|playlists|playlist)
            if [[ $# -eq 0 ]]; then
                needs_config=false
            fi
            ;;
    esac
    
    # Load config only if needed
    if [[ "$needs_config" == "true" ]]; then
        load_config
    fi
    
    case "$command" in
        search)
            cmd_search "$@"
            ;;
        library)
            cmd_library "$@"
            ;;
        playlists|playlist)
            cmd_playlists "$@"
            ;;
        *)
            error "Unknown command: $command\nRun 'apple-music --help' for usage."
            ;;
    esac
}

main "$@"
