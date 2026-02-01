#!/usr/bin/env python3
"""
Batch Email Cleanup Example
Demonstrates automated email cleanup using batch operations
"""

import sys
import os

# Add parent directory to path to import zoho_email
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from zoho_email import ZohoEmail

def cleanup_newsletters(dry_run=True):
    """
    Clean up newsletter emails from inbox
    
    Args:
        dry_run: If True, only preview what would be done
    """
    zoho = ZohoEmail(verbose=True)
    
    print("=" * 60)
    print("Newsletter Cleanup Script")
    print("=" * 60)
    
    # Search queries for different newsletter types
    cleanup_queries = [
        ('SUBJECT "newsletter"', "Generic newsletters"),
        ('SUBJECT "unsubscribe"', "Marketing emails with unsubscribe"),
        ('FROM "no-reply@"', "No-reply automated emails"),
    ]
    
    for query, description in cleanup_queries:
        print(f"\n📧 Processing: {description}")
        print(f"   Query: {query}")
        
        # Run bulk action
        result = zoho.bulk_action(
            query=query,
            action='mark-read',  # Mark as read first
            folder='INBOX',
            limit=50,  # Process max 50 emails per query
            dry_run=dry_run
        )
        
        if dry_run:
            print(f"   📊 Found: {result['total_found']} emails")
            print(f"   📋 Would process: {result['to_process']} emails")
            
            if result.get('preview'):
                print(f"   📝 Preview (first {len(result['preview'])} emails):")
                for email in result['preview']:
                    print(f"      - [{email['id']}] {email['subject']}")
        else:
            success_count = len(result.get('success', []))
            failed_count = len(result.get('failed', []))
            print(f"   ✅ Success: {success_count}")
            if failed_count > 0:
                print(f"   ❌ Failed: {failed_count}")
    
    print("\n" + "=" * 60)
    if dry_run:
        print("💡 This was a DRY RUN. No emails were modified.")
        print("   Run with --execute to perform the cleanup.")
    else:
        print("✅ Cleanup completed!")
    print("=" * 60)


def cleanup_old_emails(days=30, dry_run=True):
    """
    Clean up old read emails
    
    Args:
        days: Archive emails older than N days
        dry_run: If True, only preview what would be done
    """
    from datetime import datetime, timedelta
    
    zoho = ZohoEmail(verbose=True)
    
    # Calculate date for IMAP search
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    query = f'(SEEN BEFORE {cutoff_date})'
    
    print("=" * 60)
    print(f"Old Email Cleanup (older than {days} days)")
    print("=" * 60)
    print(f"📅 Cutoff date: {cutoff_date}")
    print(f"🔍 Query: {query}")
    
    result = zoho.bulk_action(
        query=query,
        action='delete',  # Move to trash
        folder='INBOX',
        limit=100,
        dry_run=dry_run
    )
    
    if dry_run:
        print(f"\n📊 Found: {result['total_found']} old emails")
        print(f"📋 Would delete: {result['to_process']} emails")
        
        if result.get('preview'):
            print(f"\n📝 Preview (first {len(result['preview'])} emails):")
            for email in result['preview']:
                print(f"   - [{email['id']}] {email['date']}: {email['subject']}")
    else:
        success_count = len(result.get('success', []))
        failed_count = len(result.get('failed', []))
        print(f"\n✅ Deleted: {success_count}")
        if failed_count > 0:
            print(f"❌ Failed: {failed_count}")
    
    print("=" * 60)
    if dry_run:
        print("💡 This was a DRY RUN. No emails were deleted.")
        print("   Run with --execute to perform the cleanup.")
    else:
        print("✅ Cleanup completed! Check your Trash folder.")
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch email cleanup examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview newsletter cleanup (safe)
  python3 batch-cleanup.py --newsletters
  
  # Execute newsletter cleanup
  python3 batch-cleanup.py --newsletters --execute
  
  # Preview deletion of old emails (30+ days old)
  python3 batch-cleanup.py --old-emails --days 30
  
  # Execute old email cleanup
  python3 batch-cleanup.py --old-emails --days 30 --execute
        """
    )
    
    parser.add_argument('--newsletters', action='store_true',
                        help='Clean up newsletter emails')
    parser.add_argument('--old-emails', action='store_true',
                        help='Clean up old read emails')
    parser.add_argument('--days', type=int, default=30,
                        help='Age threshold for old emails (default: 30)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually perform the cleanup (default is dry-run)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check that credentials are set
    if not os.environ.get('ZOHO_EMAIL') or not os.environ.get('ZOHO_PASSWORD'):
        print("Error: ZOHO_EMAIL and ZOHO_PASSWORD must be set", file=sys.stderr)
        print("\nPlease run:", file=sys.stderr)
        print("  export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("  export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)
        sys.exit(1)
    
    dry_run = not args.execute
    
    if args.newsletters:
        cleanup_newsletters(dry_run=dry_run)
    elif args.old_emails:
        cleanup_old_emails(days=args.days, dry_run=dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
