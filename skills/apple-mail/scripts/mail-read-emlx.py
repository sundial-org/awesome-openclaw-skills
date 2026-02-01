#!/usr/bin/env python3
"""
Read email content from Apple Mail's database and emlx files
Usage: mail-read-emlx.py <message-row-id>
"""

import sys
import sqlite3
import os
import email
from email import policy
from pathlib import Path

def find_mail_db():
    """Find the Apple Mail database"""
    for v in [11, 10, 9]:
        db_path = Path.home() / "Library" / "Mail" / f"V{v}" / "MailData" / "Envelope Index"
        if db_path.exists():
            return str(db_path)
    return None

def find_emlx_file(mail_dir, account_id, mailbox_path, remote_id):
    """Try to find the emlx file for a message"""
    # Common locations to search
    mail_v_dir = Path(mail_dir)
    account_dir = mail_v_dir / account_id
    
    if not account_dir.exists():
        return None
    
    # Search for emlx files with the remote_id as filename
    for emlx_file in account_dir.rglob(f"{remote_id}.emlx"):
        return str(emlx_file)
    
    return None

def parse_emlx(emlx_path):
    """Parse an emlx file and return the email message"""
    with open(emlx_path, 'rb') as f:
        # First line is the byte count, skip it
        first_line = f.readline()
        # Rest is the raw email
        raw_email = f.read()
    
    msg = email.message_from_bytes(raw_email, policy=policy.default)
    return msg

def get_message_info(db_path, msg_id):
    """Get message information from the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        mgd.message_id_header,
        s.subject,
        a.comment as sender,
        datetime(m.date_received, 'unixepoch', '31 years', 'localtime') as date_received,
        m.remote_id,
        mb.url
    FROM messages m
    LEFT JOIN message_global_data mgd ON m.global_message_id = mgd.ROWID
    LEFT JOIN subjects s ON m.subject = s.ROWID  
    LEFT JOIN addresses a ON m.sender = a.ROWID
    LEFT JOIN mailboxes mb ON m.mailbox = mb.ROWID
    WHERE m.ROWID = ?
    """
    
    cursor.execute(query, (msg_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    return {
        'message_id_header': result[0],
        'subject': result[1],
        'sender': result[2],
        'date_received': result[3],
        'remote_id': result[4],
        'mailbox_url': result[5]
    }

def format_email_output(msg_info, email_msg=None):
    """Format email information for output"""
    output = []
    output.append(f"From: {msg_info['sender']}")
    
    if email_msg:
        if email_msg.get('To'):
            output.append(f"To: {email_msg.get('To')}")
        if email_msg.get('Cc'):
            output.append(f"Cc: {email_msg.get('Cc')}")
    
    output.append(f"Date: {msg_info['date_received']}")
    output.append(f"Subject: {msg_info['subject']}")
    output.append("")
    output.append("---")
    output.append("")
    
    if email_msg:
        # Get the email body
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    output.append(body)
                    break
                elif part.get_content_type() == "text/html":
                    # Fallback to HTML if no plain text
                    body = part.get_content()
                    output.append(body)
        else:
            body = email_msg.get_content()
            output.append(body)
    else:
        output.append("(Message body not available - emlx file not found)")
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: mail-read-emlx.py <message-row-id>", file=sys.stderr)
        sys.exit(1)
    
    msg_id = sys.argv[1]
    
    # Find the database
    db_path = find_mail_db()
    if not db_path:
        print("Error: Mail database not found", file=sys.stderr)
        sys.exit(1)
    
    # Get message info from database
    msg_info = get_message_info(db_path, msg_id)
    if not msg_info:
        print(f"Message not found with ID: {msg_id}", file=sys.stderr)
        sys.exit(1)
    
    # Try to find and parse the emlx file
    email_msg = None
    if msg_info['remote_id'] and msg_info['mailbox_url']:
        # Parse account ID from mailbox URL
        # Format: imap://ACCOUNT-ID/MAILBOX-PATH
        if msg_info['mailbox_url'].startswith('imap://'):
            parts = msg_info['mailbox_url'][7:].split('/', 1)
            if len(parts) >= 1:
                account_id = parts[0]
                mail_dir = Path(db_path).parent.parent
                emlx_file = find_emlx_file(mail_dir, account_id, None, msg_info['remote_id'])
                
                if emlx_file:
                    try:
                        email_msg = parse_emlx(emlx_file)
                    except Exception as e:
                        print(f"Warning: Could not parse emlx file: {e}", file=sys.stderr)
    
    # Output the formatted message
    print(format_email_output(msg_info, email_msg))

if __name__ == "__main__":
    main()
