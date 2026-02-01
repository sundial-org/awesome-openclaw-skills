#!/usr/bin/env python3
"""
Attachment Demonstration Example
Shows how to send emails with attachments and download attachments from received emails
"""

import sys
import os
import json

# Add parent directory to path to import zoho-email
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from zoho_email import ZohoEmail

def create_test_files():
    """Create test files for attachment demo"""
    # Create a text file
    with open('test_document.txt', 'w') as f:
        f.write("This is a test document for attachment demonstration.\n")
        f.write("It contains some sample text.\n")
    
    # Create a simple CSV file
    with open('test_data.csv', 'w') as f:
        f.write("Name,Email,Status\n")
        f.write("John Doe,john@example.com,Active\n")
        f.write("Jane Smith,jane@example.com,Pending\n")
    
    print("✓ Created test files: test_document.txt, test_data.csv")
    return ['test_document.txt', 'test_data.csv']

def demo_send_with_attachments(zoho, recipient):
    """Demonstrate sending email with attachments"""
    print("\n=== DEMO: Send Email with Attachments ===")
    
    # Create test files
    test_files = create_test_files()
    
    # Send email with attachments
    print(f"\nSending email to {recipient} with {len(test_files)} attachments...")
    
    result = zoho.send_email_with_attachment(
        to=recipient,
        subject="Attachment Demo - Test Email",
        body="This is a test email with attachments.\n\nPlease see the attached files.",
        attachments=test_files
    )
    
    print(f"✓ Email sent successfully!")
    print(json.dumps(result, indent=2))
    
    # Clean up test files
    for file in test_files:
        os.remove(file)
    print("\n✓ Cleaned up test files")

def demo_list_and_download(zoho):
    """Demonstrate listing and downloading attachments"""
    print("\n=== DEMO: List and Download Attachments ===")
    
    # Search for emails with attachments (look for recent emails)
    print("\nSearching for recent emails...")
    emails = zoho.search_emails(folder="INBOX", query="ALL", limit=10)
    
    if not emails:
        print("No emails found in inbox")
        return
    
    # Find an email with attachments
    for email_data in emails:
        email_id = email_data['id']
        subject = email_data['subject']
        
        # Get attachments for this email
        attachments = zoho.get_attachments(folder="INBOX", email_id=email_id)
        
        if attachments:
            print(f"\n✓ Found email with attachments:")
            print(f"  ID: {email_id}")
            print(f"  Subject: {subject}")
            print(f"\nAttachments ({len(attachments)}):")
            print(json.dumps(attachments, indent=2))
            
            # Download first attachment
            if attachments:
                att = attachments[0]
                print(f"\nDownloading attachment: {att['filename']}...")
                
                result = zoho.download_attachment(
                    folder="INBOX",
                    email_id=email_id,
                    attachment_index=0,
                    output_path=f"downloaded_{att['filename']}"
                )
                
                print(f"✓ Downloaded to: {result['output_path']}")
                print(f"  Size: {result['size']} bytes")
                print(f"  Type: {result['content_type']}")
                
                # Clean up downloaded file
                if os.path.exists(result['output_path']):
                    os.remove(result['output_path'])
                    print(f"✓ Cleaned up downloaded file")
            
            return
    
    print("\nNo emails with attachments found in recent messages")

def main():
    print("Zoho Email - Attachment Demo")
    print("=" * 50)
    
    try:
        zoho = ZohoEmail(verbose=True)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease set your Zoho credentials:")
        print("  export ZOHO_EMAIL='your-email@domain.com'")
        print("  export ZOHO_PASSWORD='your-app-specific-password'")
        sys.exit(1)
    
    # Menu
    print("\nSelect demo:")
    print("1. Send email with attachments (requires recipient email)")
    print("2. List and download attachments from inbox")
    print("3. Both demos")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        recipient = input("Enter recipient email: ").strip()
        if not recipient:
            print("Error: Recipient email required")
            sys.exit(1)
        demo_send_with_attachments(zoho, recipient)
    
    elif choice == "2":
        demo_list_and_download(zoho)
    
    elif choice == "3":
        recipient = input("Enter recipient email for send demo: ").strip()
        if not recipient:
            print("Error: Recipient email required")
            sys.exit(1)
        demo_send_with_attachments(zoho, recipient)
        demo_list_and_download(zoho)
    
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Demo completed!")

if __name__ == "__main__":
    main()
