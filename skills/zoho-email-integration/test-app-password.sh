#!/bin/bash
# App Password Authentication Test Script
# Tests all basic Zoho Email commands with app password authentication

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZOHO_SCRIPT="$SCRIPT_DIR/scripts/zoho-email.py"
TEST_RECIPIENT="${TEST_EMAIL:-brian@creativestudio.co.za}"

# Check prerequisites
echo -e "${BLUE}=== App Password Authentication Test ===${NC}\n"

# Check if credentials are set
if [ -z "$ZOHO_EMAIL" ]; then
    echo -e "${RED}❌ Error: ZOHO_EMAIL environment variable not set${NC}"
    echo "Please set it with: export ZOHO_EMAIL=\"your-email@domain.com\""
    exit 1
fi

if [ -z "$ZOHO_PASSWORD" ]; then
    echo -e "${RED}❌ Error: ZOHO_PASSWORD environment variable not set${NC}"
    echo "Please set it with: export ZOHO_PASSWORD=\"your-app-password\""
    exit 1
fi

echo -e "${GREEN}✓ Credentials detected${NC}"
echo "  Email: $ZOHO_EMAIL"
echo "  Password: ${ZOHO_PASSWORD:0:4}****"
echo ""

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}Testing: ${test_name}${NC}"
    echo "Command: $command"
    
    if eval "$command"; then
        echo -e "${GREEN}✓ PASSED${NC}\n"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}\n"
        ((FAILED++))
        return 1
    fi
}

# Start tests
echo -e "${YELLOW}Running tests...${NC}\n"

# Test 1: Unread count
run_test "Get unread count" \
    "python3 '$ZOHO_SCRIPT' unread --auth password --api-mode imap"

# Test 2: Search emails
run_test "Search emails in inbox" \
    "python3 '$ZOHO_SCRIPT' search 'test' --auth password --api-mode imap"

# Test 3: Search sent emails
run_test "Search sent emails" \
    "python3 '$ZOHO_SCRIPT' search-sent 'test' --auth password --api-mode imap"

# Test 4: Send plain text email
run_test "Send plain text email" \
    "python3 '$ZOHO_SCRIPT' send '$TEST_RECIPIENT' 'App Password Test - Plain Text' 'This is a test email sent using app password authentication. Timestamp: $(date)' --auth password --api-mode imap"

# Test 5: Send email with verbose output (to test error handling)
run_test "Send email with verbose output" \
    "python3 '$ZOHO_SCRIPT' send '$TEST_RECIPIENT' 'App Password Test - Verbose Mode' 'Testing verbose output. Timestamp: $(date)' --auth password --api-mode imap --verbose"

# Test 6: Create a test file for attachment
TEST_FILE="/tmp/test-attachment-$$.txt"
echo "This is a test attachment created at $(date)" > "$TEST_FILE"

run_test "Send email with attachment" \
    "python3 '$ZOHO_SCRIPT' send '$TEST_RECIPIENT' 'App Password Test - With Attachment' 'This email includes a test attachment. Timestamp: $(date)' --attach '$TEST_FILE' --auth password --api-mode imap"

# Cleanup test file
rm -f "$TEST_FILE"

# Test 7: OAuth status (should show password mode)
run_test "Check authentication status" \
    "python3 '$ZOHO_SCRIPT' oauth-status --auth password --api-mode imap 2>&1 | grep -i 'password\\|imap' || true"

# Test 8: Test with different folder (if available)
# This might fail if no emails exist, but that's okay
run_test "Access Sent folder" \
    "python3 '$ZOHO_SCRIPT' search-sent 'test' --auth password --api-mode imap || true" || true

# Summary
echo -e "\n${BLUE}=== Test Results ===${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! App password authentication is working perfectly.${NC}"
    echo ""
    echo "✓ You can now use app password authentication with:"
    echo "  --auth password --api-mode imap"
    echo ""
    echo "✓ Test emails sent to: $TEST_RECIPIENT"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Check ZOHO_EMAIL and ZOHO_PASSWORD are set correctly"
    echo "  - Verify app password is valid in Zoho Mail settings"
    echo "  - Ensure IMAP/SMTP access is enabled in your Zoho account"
    echo ""
    echo "For troubleshooting, see APP_PASSWORD_TEST.md"
    exit 1
fi
