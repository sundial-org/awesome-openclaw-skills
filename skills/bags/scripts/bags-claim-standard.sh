#!/bin/bash
# bags-claim-standard.sh - Claim fees from standard (non-custom vault) positions
#
# Usage: ./bags-claim-standard.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be claimed without executing transactions
#
# This script handles positions where isCustomFeeVault === false.
# These are direct fee positions without shared vaults.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false

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

echo "Bags Standard Position Claimer"
echo "==============================="
echo "Wallet: $BAGS_WALLET"
if [ "$DRY_RUN" = true ]; then
  echo "Mode: DRY RUN (no transactions will be executed)"
fi
echo ""

# Fetch claimable positions
echo "Fetching claimable positions..."
BAGS_POSITIONS=$(curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/claimable-positions?wallet=$BAGS_WALLET" \
  -H "x-api-key: $BAGS_API_KEY")

if ! echo "$BAGS_POSITIONS" | jq -e '.success == true' > /dev/null 2>&1; then
  ERROR_MSG=$(echo "$BAGS_POSITIONS" | jq -r '.error // .message // "Unknown error"')
  echo "Error: Failed to fetch positions: $ERROR_MSG"
  exit 1
fi

# Filter for standard positions only
STANDARD_POSITIONS=$(echo "$BAGS_POSITIONS" | jq '[.response[] | select(.isCustomFeeVault == false)]')
POSITION_COUNT=$(echo "$STANDARD_POSITIONS" | jq 'length')

if [ "$POSITION_COUNT" = "0" ]; then
  echo "No standard positions to claim."
  exit 0
fi

echo "Found $POSITION_COUNT standard position(s)"
echo ""

# Process each position
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_CLAIMED=0

echo "$STANDARD_POSITIONS" | jq -c '.[]' | while read -r pos; do
  BASE_MINT=$(echo "$pos" | jq -r '.baseMint')
  VIRTUAL_POOL=$(echo "$pos" | jq -r '.virtualPoolAddress')
  VIRTUAL_AMOUNT=$(echo "$pos" | jq -r '.virtualPoolClaimableAmount // 0')
  DAMM_AMOUNT=$(echo "$pos" | jq -r '.dammPoolClaimableAmount // 0')
  IS_MIGRATED=$(echo "$pos" | jq -r '.isMigrated')
  
  TOTAL_LAMPORTS=$((VIRTUAL_AMOUNT + DAMM_AMOUNT))
  
  if [ "$TOTAL_LAMPORTS" -eq 0 ]; then
    echo "Skipping $BASE_MINT (nothing to claim)"
    continue
  fi
  
  TOTAL_SOL=$(echo "scale=6; $TOTAL_LAMPORTS / 1000000000" | bc)
  echo "Processing: $BASE_MINT"
  echo "  Claimable: $TOTAL_SOL SOL"
  
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would claim this position"
    continue
  fi
  
  # Build claim request
  CLAIM_REQUEST=$(jq -n \
    --arg feeClaimer "$BAGS_WALLET" \
    --arg tokenMint "$BASE_MINT" \
    --arg virtualPoolAddress "$VIRTUAL_POOL" \
    --argjson claimVirtualPoolFees "$([ "$VIRTUAL_AMOUNT" -gt 0 ] && echo true || echo false)" \
    --argjson claimDammV2Fees "$([ "$DAMM_AMOUNT" -gt 0 ] && echo true || echo false)" \
    '{
      feeClaimer: $feeClaimer,
      tokenMint: $tokenMint,
      isCustomFeeVault: false
    }')
  
  # Add virtual pool params if claiming virtual pool fees
  if [ "$VIRTUAL_AMOUNT" -gt 0 ]; then
    CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq \
      --arg virtualPoolAddress "$VIRTUAL_POOL" \
      '. + {claimVirtualPoolFees: true, virtualPoolAddress: $virtualPoolAddress}')
  fi
  
  # Add DAMM params if claiming DAMM fees
  if [ "$DAMM_AMOUNT" -gt 0 ] && [ "$IS_MIGRATED" = "true" ]; then
    DAMM_POSITION=$(echo "$pos" | jq -r '.dammPositionInfo.position')
    DAMM_POOL=$(echo "$pos" | jq -r '.dammPositionInfo.pool')
    DAMM_NFT_ACCOUNT=$(echo "$pos" | jq -r '.dammPositionInfo.positionNftAccount')
    TOKEN_A_MINT=$(echo "$pos" | jq -r '.dammPositionInfo.tokenAMint')
    TOKEN_B_MINT=$(echo "$pos" | jq -r '.dammPositionInfo.tokenBMint')
    TOKEN_A_VAULT=$(echo "$pos" | jq -r '.dammPositionInfo.tokenAVault')
    TOKEN_B_VAULT=$(echo "$pos" | jq -r '.dammPositionInfo.tokenBVault')
    
    CLAIM_REQUEST=$(echo "$CLAIM_REQUEST" | jq \
      --arg dammV2Position "$DAMM_POSITION" \
      --arg dammV2Pool "$DAMM_POOL" \
      --arg dammV2PositionNftAccount "$DAMM_NFT_ACCOUNT" \
      --arg tokenAMint "$TOKEN_A_MINT" \
      --arg tokenBMint "$TOKEN_B_MINT" \
      --arg tokenAVault "$TOKEN_A_VAULT" \
      --arg tokenBVault "$TOKEN_B_VAULT" \
      '. + {
        claimDammV2Fees: true,
        dammV2Position: $dammV2Position,
        dammV2Pool: $dammV2Pool,
        dammV2PositionNftAccount: $dammV2PositionNftAccount,
        tokenAMint: $tokenAMint,
        tokenBMint: $tokenBMint,
        tokenAVault: $tokenAVault,
        tokenBVault: $tokenBVault
      }')
  fi
  
  # Request claim transactions
  echo "  Generating claim transaction..."
  CLAIM_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/claim-txs/v2" \
    -H "x-api-key: $BAGS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$CLAIM_REQUEST")
  
  if ! echo "$CLAIM_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$CLAIM_RESPONSE" | jq -r '.error // .message // "Unknown error"')
    echo "  Error: Failed to generate claim transaction: $ERROR_MSG"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi
  
  TX_COUNT=$(echo "$CLAIM_RESPONSE" | jq '.response | length')
  echo "  Generated $TX_COUNT transaction(s)"
  
  # Export private key temporarily
  echo "  Exporting private key..."
  BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
    | jq -r '.response.privateKey')
  
  if [ -z "$BAGS_PRIVATE_KEY" ] || [ "$BAGS_PRIVATE_KEY" = "null" ]; then
    echo "  Error: Failed to export private key"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi
  
  # Sign and submit each transaction
  echo "$CLAIM_RESPONSE" | jq -c '.response[]' | while read -r tx_obj; do
    TX_BASE58=$(echo "$tx_obj" | jq -r '.tx')
    
    echo "  Signing transaction..."
    SIGNED_TX=$(node "$SCRIPT_DIR/sign-transaction.js" "$BAGS_PRIVATE_KEY" "$TX_BASE58")
    
    if [ -z "$SIGNED_TX" ]; then
      echo "  Error: Failed to sign transaction"
      continue
    fi
    
    echo "  Submitting transaction..."
    RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
      -H "Content-Type: application/json" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"id\": 1,
        \"method\": \"sendTransaction\",
        \"params\": [\"$SIGNED_TX\", {\"encoding\": \"base64\", \"skipPreflight\": false}]
      }")
    
    SIGNATURE=$(echo "$RESULT" | jq -r '.result // empty')
    ERROR=$(echo "$RESULT" | jq -r '.error.message // empty')
    
    if [ -n "$SIGNATURE" ]; then
      echo "  Success: $SIGNATURE"
      echo "  Explorer: https://solscan.io/tx/$SIGNATURE"
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
      TOTAL_CLAIMED=$((TOTAL_CLAIMED + TOTAL_LAMPORTS))
    else
      echo "  Error: $ERROR"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
  done
  
  # Clear private key
  unset BAGS_PRIVATE_KEY
  
  echo ""
done

# Summary
echo "=== SUMMARY ==="
echo "Successful claims: $SUCCESS_COUNT"
echo "Failed claims: $FAIL_COUNT"
if [ "$TOTAL_CLAIMED" -gt 0 ]; then
  TOTAL_SOL=$(echo "scale=6; $TOTAL_CLAIMED / 1000000000" | bc)
  echo "Total claimed: $TOTAL_SOL SOL"
fi
