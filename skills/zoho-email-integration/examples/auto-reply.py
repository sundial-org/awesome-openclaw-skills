#!/usr/bin/env python3
"""
Auto-reply example
Searches for emails with specific keywords and sends automated responses
"""

import sys
import os

# Add parent directory to path to import zoho-email
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from zoho_email import ZohoEmail

def main():
    zoho = ZohoEmail()
    
    # Search for pricing inquiries
    print("Searching for pricing inquiries...")
    results = zoho.search_emails(
        folder="INBOX",
        query='SUBJECT "pricing" UNSEEN',  # Only unseen emails
        limit=5
    )
    
    for email in results:
        sender = email['from']
        subject = email['subject']
        
        print(f"Found: {subject} from {sender}")
        
        # Send automated response
        reply_subject = f"Re: {subject}"
        reply_body = """Thank you for your interest in our services!

We've received your pricing inquiry and our team will get back to you within 24 hours with a detailed quote.

In the meantime, you can view our standard pricing guide at: https://example.com/pricing

Best regards,
The Team"""
        
        zoho.send_email(
            to=sender,
            subject=reply_subject,
            body=reply_body
        )
        
        print(f"✓ Sent auto-reply to {sender}")

if __name__ == "__main__":
    main()
