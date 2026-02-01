#!/bin/bash
# bags-claim-all.sh - Claim fees from all position types
#
# Usage: ./bags-claim-all.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be claimed without executing transactions
#
# This wrapper script:
# 1. Fetches all claimable positions
# 2. Identifies each position type (Standard, V1, V2)
# 3. Builds appropriate claim requests for each
# 4. Signs and submits all transactions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false

# Program ID constants
FEE_SHARE_V1_PROGRAM="FEEhPbKVKnco9EXnaY3i4R5rQVUx91wgVfu8qokixywi"
FEE_SHARE_V2_PROGRAM="FEE2tBhCKAt7shrod19QttSVREUYPiyMzoku1mL1gqVK"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Load credentials
if [ ! -f ~/.config/bags/credentials.json ]; then
  echo "Error: ~/.config/bags/credentials.json not found"
  echo "Run authentication first. See AUTH.md"
  exit 1
fi

BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
BAGS_WALLET=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')

if [ -z "$BAGS_API_KEY" ] || [ "$BAGS_API_KEY" = "null" ]; then
  echo "Error: API key not found in credentials"
  exit 1
fi

if [ -z "$BAGS_WALLET" ] || [ "$BAGS_WALLET" = "null" ]; then
  echo "Error: Wallet not found in credentials"
  exit 1
fi

echo "Bags Universal Fee Claimer"
echo "==========================="
echo "Wallet: $BAGS_WALLET"
if [ "$DRY_RUN" = true ]; then
  echo "Mode: DRY RUN (no transactions will be executed)"
fi
echo ""

# Fetch all claimable positions
echo "Fetching all claimable positions..."
BAGS_POSITIONS=$(curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/claimable-positions?wallet=$BAGS_WALLET" \
  -H "x-api-key: $BAGS_API_KEY")

if ! echo "$BAGS_POSITIONS" | jq -e '.success == true' > /dev/null 2>&1; then
  ERROR_MSG=$(echo "$BAGS_POSITIONS" | jq -r '.error // .message // "Unknown error"')
  echo "Error: Failed to fetch positions: $ERROR_MSG"
  exit 1
fi

POSITION_COUNT=$(echo "$BAGS_POSITIONS" | jq '.response | length')

if [ "$POSITION_COUNT" = "0" ]; then
  echo "No claimable positions found."
  exit 0
fi

# Categorize positions
STANDARD_POSITIONS=$(echo "$BAGS_POSITIONS" | jq '[.response[] | select(.isCustomFeeVault == false)]')
V1_POSITIONS=$(echo "$BAGS_POSITIONS" | jq --arg pid "$FEE_SHARE_V1_PROGRAM" '[.response[] | select(.isCustomFeeVault == true and .programId == $pid)]')
V2_POSITIONS=$(echo "$BAGS_POSITIONS" | jq --arg pid "$FEE_SHARE_V2_PROGRAM" '[.response[] | select(.isCustomFeeVault == true and .programId == $pid)]')

STANDARD_COUNT=$(echo "$STANDARD_POSITIONS" | jq 'length')
V1_COUNT=$(echo "$V1_POSITIONS" | jq 'length')
V2_COUNT=$(echo "$V2_POSITIONS" | jq 'length')

echo "Found positions:"
echo "  Standard: $STANDARD_COUNT"
echo "  V1: $V1_COUNT"
echo "  V2: $V2_COUNT"
echo ""

# Calculate totals
TOTAL_STANDARD=$(echo "$STANDARD_POSITIONS" | jq '[.[] | ((.virtualPoolClaimableAmount // 0) + (.dammPoolClaimableAmount // 0))] | add // 0')
TOTAL_V1=$(echo "$V1_POSITIONS" | jq '[.[] | ((.virtualPoolClaimableAmount // 0) + (.dammPoolClaimableAmount // 0))] | add // 0')
TOTAL_V2=$(echo "$V2_POSITIONS" | jq '[.[] | (.totalClaimableLamportsUserShare // 0)] | add // 0')
GRAND_TOTAL=$((TOTAL_STANDARD + TOTAL_V1 + TOTAL_V2))

# Check minimum threshold (0.001 SOL to cover tx fees)
if [ "$GRAND_TOTAL" -lt 1000000 ]; then
  GRAND_TOTAL_SOL=$(echo "scale=6; $GRAND_TOTAL / 1000000000" | bc)
  echo "Total claimable: $GRAND_TOTAL_SOL SOL"
  echo "Amount too small to claim (< 0.001 SOL). Waiting for more fees to accumulate."
  exit 0
fi

GRAND_TOTAL_SOL=$(echo "scale=6; $GRAND_TOTAL / 1000000000" | bc)
echo "Total claimable: $GRAND_TOTAL_SOL SOL"
echo ""

# Export private key once for all claims
echo "Exporting private key..."
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
  | jq -r '.response.privateKey')

if [ -z "$BAGS_PRIVATE_KEY" ] || [ "$BAGS_PRIVATE_KEY" = "null" ]; then
  echo "Error: Failed to export private key"
  exit 1
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_CLAIMED=0

# Function to process a single position
process_position() {
  local pos="$1"
  local position_type="$2"
  
  local BASE_MINT=$(echo "$pos" | jq -r '.baseMint')
  local IS_MIGRATED=$(echo "$pos" | jq -r '.isMigrated')
  local CLAIM_REQUEST=""
  local CLAIMABLE=0
  
  case $position_type in
    "standard")
      local VIRTUAL_POOL=$(echo "$pos" | jq -r '.virtualPoolAddress')
      local VIRTUAL_AMOUNT=$(echo "$pos" | jq -r '.virtualPoolClaimableAmount // 0')
      local DAMM_AMOUNT=$(echo "$pos" | jq -r '.dammPoolClaimableAmount // 0')
      CLAIMABLE=$((VIRTUAL_AMOUNT + DAMM_AMOUNT))
      
      CLAIM_REQUEST=$(jq -n \
        --arg feeClaimer "$BAGS_WALLET" \
        --arg tokenMint "$BASE_MINT" \
        '{feeClaimer: $feeClaimer, tokenMint: $tokenMint, isCustomFeeVault: false}')
      
      if [ "$VIRTUAL_AMOUNT" -gt 0 ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq --arg vp "$VIRTUAL_POOL" \
          '. + {claimVirtualPoolFees: true, virtualPoolAddress: $vp}')
      fi
      
      if [ "$DAMM_AMOUNT" -gt 0 ] && [ "$IS_MIGRATED" = "true" ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq \
          --arg p "$(echo "$pos" | jq -r '.dammPositionInfo.position')" \
          --arg pool "$(echo "$pos" | jq -r '.dammPositionInfo.pool')" \
          --arg nft "$(echo "$pos" | jq -r '.dammPositionInfo.positionNftAccount')" \
          --arg ta "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAMint')" \
          --arg tb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBMint')" \
          --arg va "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAVault')" \
          --arg vb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBVault')" \
          '. + {claimDammV2Fees: true, dammV2Position: $p, dammV2Pool: $pool, dammV2PositionNftAccount: $nft, tokenAMint: $ta, tokenBMint: $tb, tokenAVault: $va, tokenBVault: $vb}')
      fi
      ;;
      
    "v1")
      local VIRTUAL_POOL=$(echo "$pos" | jq -r '.virtualPoolAddress')
      local VIRTUAL_AMOUNT=$(echo "$pos" | jq -r '.virtualPoolClaimableAmount // 0')
      local DAMM_AMOUNT=$(echo "$pos" | jq -r '.dammPoolClaimableAmount // 0')
      local CLAIMER_A=$(echo "$pos" | jq -r '.customFeeVaultClaimerA')
      local CLAIMER_B=$(echo "$pos" | jq -r '.customFeeVaultClaimerB')
      local CLAIMER_SIDE=$(echo "$pos" | jq -r '.customFeeVaultClaimerSide')
      CLAIMABLE=$((VIRTUAL_AMOUNT + DAMM_AMOUNT))
      
      CLAIM_REQUEST=$(jq -n \
        --arg feeClaimer "$BAGS_WALLET" \
        --arg tokenMint "$BASE_MINT" \
        --arg pid "$FEE_SHARE_V1_PROGRAM" \
        --arg ca "$CLAIMER_A" \
        --arg cb "$CLAIMER_B" \
        --arg side "$CLAIMER_SIDE" \
        '{feeClaimer: $feeClaimer, tokenMint: $tokenMint, isCustomFeeVault: true, feeShareProgramId: $pid, customFeeVaultClaimerA: $ca, customFeeVaultClaimerB: $cb, customFeeVaultClaimerSide: $side}')
      
      if [ "$VIRTUAL_AMOUNT" -gt 0 ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq --arg vp "$VIRTUAL_POOL" \
          '. + {claimVirtualPoolFees: true, virtualPoolAddress: $vp}')
      fi
      
      if [ "$DAMM_AMOUNT" -gt 0 ] && [ "$IS_MIGRATED" = "true" ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq \
          --arg p "$(echo "$pos" | jq -r '.dammPositionInfo.position')" \
          --arg pool "$(echo "$pos" | jq -r '.dammPositionInfo.pool')" \
          --arg nft "$(echo "$pos" | jq -r '.dammPositionInfo.positionNftAccount')" \
          --arg ta "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAMint')" \
          --arg tb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBMint')" \
          --arg va "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAVault')" \
          --arg vb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBVault')" \
          '. + {claimDammV2Fees: true, dammV2Position: $p, dammV2Pool: $pool, dammV2PositionNftAccount: $nft, tokenAMint: $ta, tokenBMint: $tb, tokenAVault: $va, tokenBVault: $vb}')
      fi
      ;;
      
    "v2")
      local VIRTUAL_POOL=$(echo "$pos" | jq -r '.virtualPool')
      local QUOTE_MINT=$(echo "$pos" | jq -r '.quoteMint')
      local VIRTUAL_SHARE=$(echo "$pos" | jq -r '.virtualPoolClaimableLamportsUserShare // 0')
      local DAMM_SHARE=$(echo "$pos" | jq -r '.dammPoolClaimableLamportsUserShare // 0')
      CLAIMABLE=$(echo "$pos" | jq -r '.totalClaimableLamportsUserShare // 0')
      
      CLAIM_REQUEST=$(jq -n \
        --arg feeClaimer "$BAGS_WALLET" \
        --arg tokenMint "$BASE_MINT" \
        --arg pid "$FEE_SHARE_V2_PROGRAM" \
        --arg ta "$BASE_MINT" \
        --arg tb "$QUOTE_MINT" \
        '{feeClaimer: $feeClaimer, tokenMint: $tokenMint, isCustomFeeVault: true, feeShareProgramId: $pid, tokenAMint: $ta, tokenBMint: $tb}')
      
      if [ "$VIRTUAL_SHARE" -gt 0 ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq --arg vp "$VIRTUAL_POOL" \
          '. + {claimVirtualPoolFees: true, virtualPoolAddress: $vp}')
      fi
      
      if [ "$DAMM_SHARE" -gt 0 ] && [ "$IS_MIGRATED" = "true" ]; then
        CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq \
          --arg p "$(echo "$pos" | jq -r '.dammPositionInfo.position')" \
          --arg pool "$(echo "$pos" | jq -r '.dammPositionInfo.pool')" \
          --arg nft "$(echo "$pos" | jq -r '.dammPositionInfo.positionNftAccount')" \
          --arg ta "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAMint')" \
          --arg tb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBMint')" \
          --arg va "$(echo "$pos" | jq -r '.dammPositionInfo.tokenAVault')" \
          --arg vb "$(echo "$pos" | jq -r '.dammPositionInfo.tokenBVault')" \
          '. + {claimDammV2Fees: true, dammV2Position: $p, dammV2Pool: $pool, dammV2PositionNftAccount: $nft, tokenAMint: $ta, tokenBMint: $tb, tokenAVault: $va, tokenBVault: $vb}')
      fi
      ;;
  esac
  
  if [ "$CLAIMABLE" -eq 0 ]; then
    return 0
  fi
  
  local CLAIMABLE_SOL=$(echo "scale=6; $CLAIMABLE / 1000000000" | bc)
  echo "[$position_type] $BASE_MINT: $CLAIMABLE_SOL SOL"
  
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would claim"
    return 0
  fi
  
  # Request claim transaction
  local CLAIM_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/claim-txs/v2" \
    -H "x-api-key: $BAGS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$CLAIM_REQUEST")
  
  if ! echo "$CLAIM_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    local ERROR_MSG=$(echo "$CLAIM_RESPONSE" | jq -r '.error // .message // "Unknown error"')
    echo "  Error: $ERROR_MSG"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
  
  # Sign and submit transactions
  echo "$CLAIM_RESPONSE" | jq -c '.response[]' | while read -r tx_obj; do
    local TX_BASE58=$(echo "$tx_obj" | jq -r '.tx')
    
    local SIGNED_TX=$(node "$SCRIPT_DIR/sign-transaction.js" "$BAGS_PRIVATE_KEY" "$TX_BASE58")
    
    if [ -z "$SIGNED_TX" ]; then
      echo "  Error: Failed to sign"
      continue
    fi
    
    local RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
      -H "Content-Type: application/json" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"id\": 1,
        \"method\": \"sendTransaction\",
        \"params\": [\"$SIGNED_TX\", {\"encoding\": \"base64\", \"skipPreflight\": false}]
      }")
    
    local SIGNATURE=$(echo "$RESULT" | jq -r '.result // empty')
    local ERROR=$(echo "$RESULT" | jq -r '.error.message // empty')
    
    if [ -n "$SIGNATURE" ]; then
      echo "  Success: https://solscan.io/tx/$SIGNATURE"
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
      TOTAL_CLAIMED=$((TOTAL_CLAIMED + CLAIMABLE))
    else
      echo "  Error: $ERROR"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
  done
}

# Process Standard positions
if [ "$STANDARD_COUNT" -gt 0 ]; then
  echo "=== Processing Standard Positions ==="
  echo "$STANDARD_POSITIONS" | jq -c '.[]' | while read -r pos; do
    process_position "$pos" "standard"
  done
  echo ""
fi

# Process V1 positions
if [ "$V1_COUNT" -gt 0 ]; then
  echo "=== Processing V1 Positions ==="
  echo "$V1_POSITIONS" | jq -c '.[]' | while read -r pos; do
    process_position "$pos" "v1"
  done
  echo ""
fi

# Process V2 positions
if [ "$V2_COUNT" -gt 0 ]; then
  echo "=== Processing V2 Positions ==="
  echo "$V2_POSITIONS" | jq -c '.[]' | while read -r pos; do
    process_position "$pos" "v2"
  done
  echo ""
fi

# Clear private key
unset BAGS_PRIVATE_KEY

# Summary
echo "=== FINAL SUMMARY ==="
echo "Total positions processed: $POSITION_COUNT"
echo "Successful claims: $SUCCESS_COUNT"
echo "Failed claims: $FAIL_COUNT"
if [ "$TOTAL_CLAIMED" -gt 0 ]; then
  TOTAL_SOL=$(echo "scale=6; $TOTAL_CLAIMED / 1000000000" | bc)
  echo "Total claimed: $TOTAL_SOL SOL"
fi
