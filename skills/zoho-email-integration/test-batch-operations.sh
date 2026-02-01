#!/bin/bash
# Test script for batch operations
# Verifies syntax and help text (doesn't require real credentials)

set -e

echo "=================================="
echo "Batch Operations Test Suite"
echo "=================================="
echo ""

# Set dummy credentials for syntax checking
export ZOHO_EMAIL="test@example.com"
export ZOHO_PASSWORD="dummy_password"

cd "$(dirname "$0")"

echo "✅ 1. Checking Python syntax..."
python3 -m py_compile scripts/zoho-email.py
echo "   Syntax OK"
echo ""

echo "✅ 2. Testing CLI help text..."
python3 scripts/zoho-email.py | grep -q "Batch Operations"
echo "   Help text includes batch operations"
echo ""

echo "✅ 3. Testing mark-read command structure..."
python3 scripts/zoho-email.py mark-read 2>&1 | grep -q "folder and at least one email_id required"
echo "   Command accepts correct arguments"
echo ""

echo "✅ 4. Testing mark-unread command structure..."
python3 scripts/zoho-email.py mark-unread 2>&1 | grep -q "folder and at least one email_id required"
echo "   Command accepts correct arguments"
echo ""

echo "✅ 5. Testing delete command structure..."
python3 scripts/zoho-email.py delete 2>&1 | grep -q "folder and at least one email_id required"
echo "   Command accepts correct arguments"
echo ""

echo "✅ 6. Testing move command structure..."
python3 scripts/zoho-email.py move 2>&1 | grep -q "source_folder, target_folder"
echo "   Command accepts correct arguments"
echo ""

echo "✅ 7. Testing bulk-action command structure..."
python3 scripts/zoho-email.py bulk-action 2>&1 | grep -q "folder, --search, and --action are required"
echo "   Command accepts correct arguments"
echo ""

echo "✅ 8. Testing batch cleanup example script..."
python3 -m py_compile examples/batch-cleanup.py
echo "   Syntax OK"
echo ""

echo "✅ 9. Testing batch cleanup help..."
python3 examples/batch-cleanup.py --help | grep -q "Batch email cleanup examples"
echo "   Help text works"
echo ""

echo "✅ 10. Verifying documentation..."
[ -f "BATCH_FEATURE.md" ] && echo "   BATCH_FEATURE.md exists"
grep -q "Batch Operations" SKILL.md && echo "   SKILL.md updated"
grep -q "Batch Operations" CHANGELOG.md && echo "   CHANGELOG.md updated"
echo ""

echo "=================================="
echo "✅ All batch operation tests passed!"
echo "=================================="
echo ""
echo "Note: These tests verify syntax and structure only."
echo "To test with real emails:"
echo "  1. Set real ZOHO_EMAIL and ZOHO_PASSWORD"
echo "  2. Create a test folder in your Zoho Mail"
echo "  3. Run: python3 scripts/zoho-email.py mark-read TestFolder <email_id>"
echo ""
