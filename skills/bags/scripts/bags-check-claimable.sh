#!/bin/bash
# bags-check-claimable.sh - Fetch and display all claimable positions by type
#
# Usage: ./bags-check-claimable.sh
#
# This script fetches all claimable positions for your wallet and categorizes them
# by position type (Standard, V1, V2) for easy identification.

set -e

# Program ID constants
FEE_SHARE_V1_PROGRAM="FEEhPbKVKnco9EXnaY3i4R5rQVUx91wgVfu8qokixywi"
FEE_SHARE_V2_PROGRAM="FEE2tBhCKAt7shrod19QttSVREUYPiyMzoku1mL1gqVK"

# Load credentials
if [ ! -f ~/.config/bags/credentials.json ]; then
  echo "Error: ~/.config/bags/credentials.json not found"
  echo "Run authentication first. See AUTH.md"
  exit 1
fi

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

echo "Bags Fee Position Checker"
echo "========================="
echo "Wallet: $BAGS_WALLET"
echo ""

# Fetch claimable positions
echo "Fetching claimable positions..."
BAGS_POSITIONS=$(curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/claimable-positions?wallet=$BAGS_WALLET" \
  -H "x-api-key: $BAGS_API_KEY")

# Check for API errors
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

echo "Found $POSITION_COUNT position(s)"
echo ""

# Categorize positions
STANDARD_POSITIONS=$(echo "$BAGS_POSITIONS" | jq '[.response[] | select(.isCustomFeeVault == false)]')
V1_POSITIONS=$(echo "$BAGS_POSITIONS" | jq --arg pid "$FEE_SHARE_V1_PROGRAM" '[.response[] | select(.isCustomFeeVault == true and .programId == $pid)]')
V2_POSITIONS=$(echo "$BAGS_POSITIONS" | jq --arg pid "$FEE_SHARE_V2_PROGRAM" '[.response[] | select(.isCustomFeeVault == true and .programId == $pid)]')

STANDARD_COUNT=$(echo "$STANDARD_POSITIONS" | jq 'length')
V1_COUNT=$(echo "$V1_POSITIONS" | jq 'length')
V2_COUNT=$(echo "$V2_POSITIONS" | jq 'length')

# Display Standard Positions
if [ "$STANDARD_COUNT" -gt 0 ]; then
  echo "=== STANDARD POSITIONS ($STANDARD_COUNT) ==="
  echo "Script: ./scripts/bags-claim-standard.sh"
  echo ""
  
  echo "$STANDARD_POSITIONS" | jq -c '.[]' | while read -r pos; do
    BASE_MINT=$(echo "$pos" | jq -r '.baseMint')
    VIRTUAL_AMOUNT=$(echo "$pos" | jq -r '.virtualPoolClaimableAmount // 0')
    DAMM_AMOUNT=$(echo "$pos" | jq -r '.dammPoolClaimableAmount // 0')
    IS_MIGRATED=$(echo "$pos" | jq -r '.isMigrated')
    
    TOTAL_LAMPORTS=$((VIRTUAL_AMOUNT + DAMM_AMOUNT))
    TOTAL_SOL=$(echo "scale=6; $TOTAL_LAMPORTS / 1000000000" | bc)
    
    echo "  Token: $BASE_MINT"
    echo "    Virtual Pool: $VIRTUAL_AMOUNT lamports"
    echo "    DAMM Pool: $DAMM_AMOUNT lamports"
    echo "    Migrated: $IS_MIGRATED"
    echo "    Total: $TOTAL_SOL SOL"
    echo ""
  done
fi

# Display V1 Positions
if [ "$V1_COUNT" -gt 0 ]; then
  echo "=== CUSTOM FEE VAULT V1 POSITIONS ($V1_COUNT) ==="
  echo "Program: $FEE_SHARE_V1_PROGRAM"
  echo "Script: ./scripts/bags-claim-v1.sh"
  echo ""
  
  echo "$V1_POSITIONS" | jq -c '.[]' | while read -r pos; do
    BASE_MINT=$(echo "$pos" | jq -r '.baseMint')
    CLAIMER_SIDE=$(echo "$pos" | jq -r '.customFeeVaultClaimerSide')
    BPS=$(echo "$pos" | jq -r '.customFeeVaultBps // 0')
    VIRTUAL_AMOUNT=$(echo "$pos" | jq -r '.virtualPoolClaimableAmount // 0')
    DAMM_AMOUNT=$(echo "$pos" | jq -r '.dammPoolClaimableAmount // 0')
    IS_MIGRATED=$(echo "$pos" | jq -r '.isMigrated')
    
    TOTAL_LAMPORTS=$((VIRTUAL_AMOUNT + DAMM_AMOUNT))
    TOTAL_SOL=$(echo "scale=6; $TOTAL_LAMPORTS / 1000000000" | bc)
    SHARE_PERCENT=$(echo "scale=2; $BPS / 100" | bc)
    
    echo "  Token: $BASE_MINT"
    echo "    Your Side: Claimer $CLAIMER_SIDE"
    echo "    Your Share: ${SHARE_PERCENT}%"
    echo "    Virtual Pool: $VIRTUAL_AMOUNT lamports"
    echo "    DAMM Pool: $DAMM_AMOUNT lamports"
    echo "    Migrated: $IS_MIGRATED"
    echo "    Total: $TOTAL_SOL SOL"
    echo ""
  done
fi

# Display V2 Positions
if [ "$V2_COUNT" -gt 0 ]; then
  echo "=== CUSTOM FEE VAULT V2 POSITIONS ($V2_COUNT) ==="
  echo "Program: $FEE_SHARE_V2_PROGRAM"
  echo "Script: ./scripts/bags-claim-v2.sh"
  echo ""
  
  echo "$V2_POSITIONS" | jq -c '.[]' | while read -r pos; do
    BASE_MINT=$(echo "$pos" | jq -r '.baseMint')
    CLAIMER_INDEX=$(echo "$pos" | jq -r '.claimerIndex // 0')
    USER_BPS=$(echo "$pos" | jq -r '.userBps // 0')
    VIRTUAL_SHARE=$(echo "$pos" | jq -r '.virtualPoolClaimableLamportsUserShare // 0')
    DAMM_SHARE=$(echo "$pos" | jq -r '.dammPoolClaimableLamportsUserShare // 0')
    TOTAL_SHARE=$(echo "$pos" | jq -r '.totalClaimableLamportsUserShare // 0')
    IS_MIGRATED=$(echo "$pos" | jq -r '.isMigrated')
    
    TOTAL_SOL=$(echo "scale=6; $TOTAL_SHARE / 1000000000" | bc)
    SHARE_PERCENT=$(echo "scale=2; $USER_BPS / 100" | bc)
    
    echo "  Token: $BASE_MINT"
    echo "    Claimer Index: $CLAIMER_INDEX"
    echo "    Your Share: ${SHARE_PERCENT}%"
    echo "    Virtual Pool (your share): $VIRTUAL_SHARE lamports"
    echo "    DAMM Pool (your share): $DAMM_SHARE lamports"
    echo "    Migrated: $IS_MIGRATED"
    echo "    Total: $TOTAL_SOL SOL"
    echo ""
  done
fi

# Calculate grand total
TOTAL_STANDARD=$(echo "$STANDARD_POSITIONS" | jq '[.[] | ((.virtualPoolClaimableAmount // 0) + (.dammPoolClaimableAmount // 0))] | add // 0')
TOTAL_V1=$(echo "$V1_POSITIONS" | jq '[.[] | ((.virtualPoolClaimableAmount // 0) + (.dammPoolClaimableAmount // 0))] | add // 0')
TOTAL_V2=$(echo "$V2_POSITIONS" | jq '[.[] | (.totalClaimableLamportsUserShare // 0)] | add // 0')

GRAND_TOTAL=$((TOTAL_STANDARD + TOTAL_V1 + TOTAL_V2))
GRAND_TOTAL_SOL=$(echo "scale=6; $GRAND_TOTAL / 1000000000" | bc)

echo "=== SUMMARY ==="
echo "Standard Positions: $STANDARD_COUNT"
echo "V1 Positions: $V1_COUNT"
echo "V2 Positions: $V2_COUNT"
echo ""
echo "Total Claimable: $GRAND_TOTAL_SOL SOL ($GRAND_TOTAL lamports)"

# Suggest next action
if [ "$GRAND_TOTAL" -gt 0 ]; then
  echo ""
  echo "To claim all fees, run: ./scripts/bags-claim-all.sh"
fi
