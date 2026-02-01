#!/usr/bin/env python3
"""
HTML Email Example - Send a newsletter
Demonstrates how to send HTML emails with the Zoho Email skill
"""

import sys
import os

# Add parent directory to path to import zoho-email
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from zoho_email import ZohoEmail

def load_template(template_name):
    """Load an HTML template from the templates directory"""
    template_path = os.path.join(
        os.path.dirname(__file__),
        'templates',
        f'{template_name}.html'
    )
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    with open(template_path, 'r') as f:
        return f.read()

def customize_template(html_content, replacements):
    """Replace placeholders in the template with actual values"""
    for key, value in replacements.items():
        html_content = html_content.replace(f"{{{{{key}}}}}", value)
    return html_content

def main():
    # Initialize Zoho Email client
    zoho = ZohoEmail(verbose=True)
    
    # Example 1: Send a simple HTML email with inline HTML
    print("Example 1: Sending simple HTML email...")
    simple_html = """
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">Hello from Zoho!</h2>
            <p>This is a <strong>simple HTML email</strong> sent via the Zoho Email skill.</p>
            <p>HTML emails are great for:</p>
            <ul>
                <li>Rich formatting</li>
                <li>Branded communications</li>
                <li>Better engagement</li>
            </ul>
        </body>
    </html>
    """
    
    # You can specify your own email here for testing
    test_email = os.environ.get('TEST_EMAIL', os.environ.get('ZOHO_EMAIL'))
    
    result = zoho.send_html_email(
        to=test_email,
        subject="Test: Simple HTML Email",
        html_body=simple_html
    )
    print(f"✓ Sent! Result: {result}")
    
    # Example 2: Send using a template file
    print("\nExample 2: Sending newsletter from template...")
    try:
        newsletter_html = load_template('newsletter')
        
        result = zoho.send_html_email(
            to=test_email,
            subject="📰 Your Monthly Newsletter",
            html_body=newsletter_html
        )
        print(f"✓ Newsletter sent! Result: {result}")
    except FileNotFoundError as e:
        print(f"⚠ Skipping newsletter example: {e}")
    
    # Example 3: Send HTML with custom plain text fallback
    print("\nExample 3: Sending with custom plain text fallback...")
    html_with_images = """
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h1 style="color: #e74c3c;">🎉 Special Offer!</h1>
            <div style="background: #f8f9fa; padding: 20px; margin: 20px 0;">
                <p style="font-size: 24px; font-weight: bold;">50% OFF</p>
                <p>Use code: <strong>SAVE50</strong></p>
            </div>
            <a href="#" style="display: inline-block; background: #e74c3c; color: white; 
                             padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                Shop Now
            </a>
        </body>
    </html>
    """
    
    plain_text = """
    🎉 SPECIAL OFFER!
    
    Get 50% OFF your next purchase!
    
    Use code: SAVE50
    
    Shop now at: https://example.com/shop
    
    This offer is valid for a limited time only.
    """
    
    result = zoho.send_email(
        to=test_email,
        subject="🎉 Special Offer Inside!",
        body=plain_text,
        html_body=html_with_images
    )
    print(f"✓ Promotional email sent! Result: {result}")
    
    print("\n" + "="*50)
    print("All examples completed successfully!")
    print(f"Check your inbox at: {test_email}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
