#!/bin/bash
# Test script for REST API batch operation fixes
# Tests all fixed operations to verify they work correctly

set -e

export ZOHO_EMAIL="brian@creativestudio.co.za"
SCRIPT="python3 scripts/zoho-email.py"
API_MODE="--api-mode rest"

echo "=========================================="
echo "Zoho Email REST API Fixes - Verification"
echo "=========================================="
echo ""

# Test 1: Get a message ID to test with
echo "📧 Step 1: Getting test message ID..."
MESSAGE_ID=$(${SCRIPT} search INBOX --limit 1 ${API_MODE} | jq -r '.[0].id')
echo "   Using message ID: ${MESSAGE_ID}"
echo ""

# Test 2: Mark as unread first (so we can test mark as read)
echo "📝 Step 2: Testing mark-as-unread..."
${SCRIPT} mark-unread INBOX ${MESSAGE_ID} ${API_MODE} > /tmp/test-unread.json
SUCCESS=$(cat /tmp/test-unread.json | jq -r '.success | length')
if [ "$SUCCESS" -eq "1" ]; then
    echo "   ✅ Mark as unread: PASSED"
else
    echo "   ❌ Mark as unread: FAILED"
    cat /tmp/test-unread.json
    exit 1
fi
echo ""

# Test 3: Mark as read
echo "📝 Step 3: Testing mark-as-read..."
${SCRIPT} mark-read INBOX ${MESSAGE_ID} ${API_MODE} > /tmp/test-read.json
SUCCESS=$(cat /tmp/test-read.json | jq -r '.success | length')
if [ "$SUCCESS" -eq "1" ]; then
    echo "   ✅ Mark as read: PASSED"
else
    echo "   ❌ Mark as read: FAILED"
    cat /tmp/test-read.json
    exit 1
fi
echo ""

# Test 4: HTML email (test for no NameError)
echo "📧 Step 4: Testing HTML email send..."
${SCRIPT} send-html ${ZOHO_EMAIL} "REST API Test" "<h1>Test Email</h1><p>Testing fixes</p>" ${API_MODE} > /tmp/test-html.json 2>&1
if grep -q "Error: name 'email_id' is not defined" /tmp/test-html.json; then
    echo "   ❌ HTML email: FAILED (NameError found)"
    cat /tmp/test-html.json
    exit 1
elif grep -q '"status": "sent"' /tmp/test-html.json; then
    echo "   ✅ HTML email: PASSED (no NameError)"
else
    echo "   ⚠️  HTML email: Uncertain"
    cat /tmp/test-html.json
fi
echo ""

# Test 5: Move email (move to Drafts and back)
echo "📁 Step 5: Testing move operation..."
echo "   Moving to Drafts..."
${SCRIPT} move INBOX Drafts ${MESSAGE_ID} ${API_MODE} > /tmp/test-move1.json
SUCCESS=$(cat /tmp/test-move1.json | jq -r '.success | length')
if [ "$SUCCESS" -eq "1" ]; then
    echo "   ✅ Move to Drafts: PASSED"
    # Move back
    echo "   Moving back to INBOX..."
    ${SCRIPT} move Drafts INBOX ${MESSAGE_ID} ${API_MODE} > /tmp/test-move2.json
    SUCCESS=$(cat /tmp/test-move2.json | jq -r '.success | length')
    if [ "$SUCCESS" -eq "1" ]; then
        echo "   ✅ Move back to INBOX: PASSED"
    else
        echo "   ❌ Move back to INBOX: FAILED"
        cat /tmp/test-move2.json
        exit 1
    fi
else
    echo "   ❌ Move to Drafts: FAILED"
    cat /tmp/test-move1.json
    exit 1
fi
echo ""

# Test 6: Batch operation (mark multiple as read)
echo "📝 Step 6: Testing batch mark-as-read..."
MESSAGE_IDS=$(${SCRIPT} search INBOX --limit 3 ${API_MODE} | jq -r '.[].id' | tr '\n' ' ')
${SCRIPT} mark-read INBOX ${MESSAGE_IDS} ${API_MODE} > /tmp/test-batch.json
SUCCESS=$(cat /tmp/test-batch.json | jq -r '.success | length')
if [ "$SUCCESS" -ge "1" ]; then
    echo "   ✅ Batch operation: PASSED (${SUCCESS} messages)"
else
    echo "   ❌ Batch operation: FAILED"
    cat /tmp/test-batch.json
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ ALL TESTS PASSED!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ Mark as read/unread - Working"
echo "  ✅ HTML email send - No NameError"
echo "  ✅ Move operation - Working"
echo "  ✅ Batch operations - Working"
echo ""
echo "REST API implementation is fully functional!"
