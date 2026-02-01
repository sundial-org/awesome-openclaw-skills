#!/bin/bash
###############################################################################
# Claw Conductor Setup Wizard
# Interactive configuration for intelligent multi-model orchestration
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$BASE_DIR/config"
DEFAULTS_DIR="$CONFIG_DIR/defaults"
REGISTRY_FILE="$CONFIG_DIR/agent-registry.json"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-n}"

    if [ "$default" = "y" ]; then
        read -p "$prompt [Y/n]: " response
        response=${response:-y}
    else
        read -p "$prompt [y/N]: " response
        response=${response:-n}
    fi

    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

###############################################################################
# Setup Functions
###############################################################################

show_welcome() {
    clear
    print_header "CLAW CONDUCTOR SETUP WIZARD"

    cat << 'EOF'
Welcome to Claw Conductor - Intelligent Multi-Model Orchestration!

This wizard will help you:
  • Configure your AI model agents
  • Set capability ratings and complexity limits
  • Track costs (optional)
  • Add models from our default profiles

Let's get started!

EOF
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        echo "Please install Python 3.7 or higher"
        exit 1
    fi

    print_success "Python 3 found: $(python3 --version)"

    # Check for jq (optional but helpful)
    if ! command -v jq &> /dev/null; then
        print_warning "jq not found - JSON editing will be limited"
        echo "  Install with: brew install jq (macOS) or apt-get install jq (Linux)"
    else
        print_success "jq found for JSON processing"
    fi
}

create_initial_registry() {
    print_info "Creating initial agent registry..."

    # Copy from example file
    local EXAMPLE_FILE="$CONFIG_DIR/agent-registry.example.json"

    if [ -f "$EXAMPLE_FILE" ]; then
        cp "$EXAMPLE_FILE" "$REGISTRY_FILE"
        print_success "Created agent registry from example"
    else
        # Fallback: create minimal registry
        cat > "$REGISTRY_FILE" << 'EOF'
{
  "version": "1.0.0",
  "created_at": null,
  "last_updated": null,
  "user_config": {
    "cost_tracking_enabled": false,
    "prefer_free_when_equal": true,
    "default_complexity_if_unknown": 3,
    "fallback": {
      "enabled": true,
      "retry_delay_seconds": 2,
      "track_failures": true,
      "penalize_failures": true,
      "failure_penalty_points": 5
    }
  },
  "agents": {}
}
EOF
        print_success "Created empty agent registry"
    fi

    # Update timestamps
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --arg now "$now" '.created_at = $now | .last_updated = $now' "$REGISTRY_FILE" > "$temp"
        mv "$temp" "$REGISTRY_FILE"
    fi
}

configure_preferences() {
    print_header "USER PREFERENCES"

    echo "Let's configure some global preferences:"
    echo ""

    # Cost tracking
    if ask_yes_no "Do you want to track model costs?" n; then
        COST_TRACKING="true"
        print_success "Cost tracking enabled"
    else
        COST_TRACKING="false"
        print_info "Cost tracking disabled"
    fi

    # Free model preference
    if ask_yes_no "When models score equally, prefer free models?" y; then
        PREFER_FREE="true"
        print_success "Will prefer free models when tied"
    else
        PREFER_FREE="false"
        print_info "Will use first matching model when tied"
    fi

    # Update registry
    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --argjson cost "$COST_TRACKING" \
           --argjson free "$PREFER_FREE" \
           '.user_config.cost_tracking_enabled = $cost | .user_config.prefer_free_when_equal = $free' \
           "$REGISTRY_FILE" > "$temp"
        mv "$temp" "$REGISTRY_FILE"
    fi
}

list_default_models() {
    print_header "AVAILABLE DEFAULT MODELS"

    echo "The following pre-configured models are available:"
    echo ""

    local i=1
    for file in "$DEFAULTS_DIR"/*.json; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file" .json)
            local model_id=""
            local provider=""
            local cost_type=""

            if command -v jq &> /dev/null; then
                model_id=$(jq -r '.model_id' "$file")
                provider=$(jq -r '.provider' "$file")
                cost_type=$(jq -r '.user_cost.type' "$file")
            fi

            echo -e "  ${BLUE}$i)${NC} $filename"
            echo "     Model: $model_id"
            echo "     Provider: $provider | Cost: $cost_type"
            echo ""

            i=$((i+1))
        fi
    done
}

add_model_from_default() {
    local default_file="$1"
    local filename=$(basename "$default_file" .json)

    print_info "Adding model: $filename"

    if ! command -v jq &> /dev/null; then
        print_error "jq is required to add models. Please install jq first."
        return 1
    fi

    # Read default profile
    local model_data=$(cat "$default_file")
    local model_id=$(echo "$model_data" | jq -r '.model_id')
    local cost_type=$(echo "$model_data" | jq -r '.user_cost.type')

    echo ""
    echo "Model: $model_id"
    echo "Default cost type: $cost_type"
    echo ""

    # Ask about cost verification
    local actual_cost_type="$cost_type"
    if [ "$cost_type" = "free-tier" ] || [ "$cost_type" = "free" ]; then
        if ask_yes_no "Is this accurate for your account?" y; then
            print_success "Using free tier"
        else
            echo ""
            echo "Select your actual cost type:"
            echo "  1) pay-per-use (charged per token)"
            echo "  2) subscription (flat monthly fee)"
            echo "  3) free (completely free)"
            echo ""
            read -p "Choose [1-3]: " cost_choice

            case "$cost_choice" in
                1) actual_cost_type="pay-per-use" ;;
                2) actual_cost_type="subscription" ;;
                3) actual_cost_type="free" ;;
                *)
                    print_warning "Invalid choice, using default: $cost_type"
                    ;;
            esac
        fi
    fi

    # Update cost type and verification date
    local now=$(date -u +"%Y-%m-%d")
    model_data=$(echo "$model_data" | jq \
        --arg cost_type "$actual_cost_type" \
        --arg now "$now" \
        '.user_cost.type = $cost_type | .user_cost.verified_date = $now | .enabled = true')

    # Generate agent ID
    local agent_id=$(echo "$filename" | tr '[:upper:]' '[:lower:]' | tr '.' '-')

    # Add to registry
    local temp=$(mktemp)
    jq --arg id "$agent_id" \
       --argjson data "$model_data" \
       --arg now "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.agents[$id] = $data | .last_updated = $now' \
       "$REGISTRY_FILE" > "$temp"
    mv "$temp" "$REGISTRY_FILE"

    print_success "Added $filename to registry as '$agent_id'"
}

interactive_model_selection() {
    print_header "ADD MODELS FROM DEFAULTS"

    while true; do
        list_default_models

        echo "Enter the number of a model to add (or 'done' to finish):"
        read -p "> " choice

        if [ "$choice" = "done" ] || [ "$choice" = "q" ]; then
            break
        fi

        # Get the file corresponding to the number
        local files=("$DEFAULTS_DIR"/*.json)
        local index=$((choice - 1))

        if [ $index -ge 0 ] && [ $index -lt ${#files[@]} ]; then
            add_model_from_default "${files[$index]}"
            echo ""
            read -p "Press Enter to continue..."
        else
            print_error "Invalid selection"
        fi
    done
}

add_custom_model() {
    print_header "ADD CUSTOM MODEL"

    echo "Let's configure a custom model not in our defaults."
    echo ""

    read -p "Model ID (e.g., mistral/devstral-2512): " model_id
    read -p "Provider (e.g., mistral, openai, google): " provider
    read -p "Agent ID (short name, e.g., mistral-devstral): " agent_id

    echo ""
    echo "Cost type:"
    echo "  1) free"
    echo "  2) free-tier (limited free usage)"
    echo "  3) pay-per-use"
    echo "  4) subscription"
    echo ""
    read -p "Choose [1-4]: " cost_choice

    case "$cost_choice" in
        1) cost_type="free" ;;
        2) cost_type="free-tier" ;;
        3) cost_type="pay-per-use" ;;
        4) cost_type="subscription" ;;
        *) cost_type="unknown" ;;
    esac

    # Create basic agent structure
    local now=$(date -u +"%Y-%m-%d")
    local agent_data=$(cat << EOF
{
  "model_id": "$model_id",
  "provider": "$provider",
  "context_window": 128000,
  "enabled": true,
  "user_cost": {
    "type": "$cost_type",
    "input_cost_per_million": 0,
    "output_cost_per_million": 0,
    "notes": "User-configured custom model",
    "verified_date": "$now"
  },
  "capabilities": {}
}
EOF
)

    # Add to registry
    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --arg id "$agent_id" \
           --argjson data "$agent_data" \
           --arg now "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.agents[$id] = $data | .last_updated = $now' \
           "$REGISTRY_FILE" > "$temp"
        mv "$temp" "$REGISTRY_FILE"

        print_success "Added custom model: $agent_id"
        print_warning "You'll need to manually configure capabilities in: $REGISTRY_FILE"
    else
        print_error "jq is required to add custom models"
    fi
}

show_summary() {
    print_header "SETUP COMPLETE"

    local agent_count=0
    if command -v jq &> /dev/null; then
        agent_count=$(jq '.agents | length' "$REGISTRY_FILE")
    fi

    echo -e "${GREEN}✓ Configuration saved to:${NC} $REGISTRY_FILE"
    echo -e "${GREEN}✓ Agents configured:${NC} $agent_count"
    echo ""

    echo "Next steps:"
    echo ""
    echo "  1. Test routing:"
    echo "     ${CYAN}python3 scripts/router.py --test${NC}"
    echo ""
    echo "  2. Customize capability ratings (optional):"
    echo "     ${CYAN}python3 scripts/update-capability.py --help${NC}"
    echo ""
    echo "  3. Use in OpenClaw:"
    echo "     Load the 'claw-conductor' skill in your OpenClaw session"
    echo ""

    print_success "Setup complete! Happy orchestrating!"
}

###############################################################################
# Main Setup Flow
###############################################################################

main() {
    show_welcome

    check_prerequisites

    echo ""
    read -p "Press Enter to continue..."

    # Check if registry already exists
    if [ -f "$REGISTRY_FILE" ]; then
        print_warning "Agent registry already exists: $REGISTRY_FILE"

        if ask_yes_no "Do you want to start fresh (this will backup the existing file)?" n; then
            local backup="${REGISTRY_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
            mv "$REGISTRY_FILE" "$backup"
            print_success "Backed up to: $backup"
            create_initial_registry
        else
            print_info "Using existing registry"
        fi
    else
        create_initial_registry
    fi

    configure_preferences

    echo ""
    read -p "Press Enter to continue..."

    # Model selection menu
    while true; do
        clear
        print_header "ADD MODELS"

        echo "What would you like to do?"
        echo ""
        echo "  1) Add model from defaults (recommended)"
        echo "  2) Add custom model"
        echo "  3) Finish setup"
        echo ""
        read -p "Choose [1-3]: " choice

        case "$choice" in
            1) interactive_model_selection ;;
            2) add_custom_model ;;
            3) break ;;
            *) print_error "Invalid choice" ;;
        esac
    done

    show_summary
}

# Run setup
main
