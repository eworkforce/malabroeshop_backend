#!/usr/bin/env python3
"""
SendGrid SMTP Configuration for MALABRO
Google Cloud recommended email service setup
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def setup_sendgrid_smtp():
    """Configure SendGrid SMTP settings for .env file"""
    
    print("SendGrid SMTP Configuration for MALABRO")
    print("=" * 50)
    print()
    print("Steps to get SendGrid API Key:")
    print("1. Go to https://sendgrid.com/")
    print("2. Sign up for free account (100 emails/day)")
    print("3. Go to Settings > API Keys")
    print("4. Create new API key with 'Mail Send' permissions")
    print("5. Copy the API key")
    print()
    
    api_key = input("Enter your SendGrid API Key: ").strip()
    sender_email = input("Enter verified sender email (e.g., noreply@malabro.com): ").strip()
    
    # Test SendGrid connection
    try:
        sg = SendGridAPIClient(api_key=api_key)
        
        # Test email
        message = Mail(
            from_email=sender_email,
            to_emails='sergeziehi@eworkforce.africa',
            subject='MALABRO SendGrid Test',
            html_content='''
            <h2>🎉 SendGrid SMTP Test Successful!</h2>
            <p>Your MALABRO platform is now configured with SendGrid for reliable email delivery.</p>
            <ul>
                <li>✅ SendGrid API connection working</li>
                <li>✅ Email notifications ready</li>
                <li>✅ Production-ready SMTP service</li>
            </ul>
            <p>Cordialement,<br>L'équipe MALABRO</p>
            '''
        )
        
        response = sg.send(message)
        print(f"✅ Test email sent successfully! Status: {response.status_code}")
        
        # Generate .env configuration
        env_config = f"""
# SendGrid SMTP Configuration (Google Cloud Recommended)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD={api_key}
SENDGRID_FROM_EMAIL={sender_email}
"""
        
        print("\n" + "=" * 50)
        print("Add this to your .env file:")
        print(env_config)
        
        return True
        
    except Exception as e:
        print(f"❌ SendGrid test failed: {e}")
        return False

if __name__ == "__main__":
    # Check if sendgrid is installed
    try:
        import sendgrid
        setup_sendgrid_smtp()
    except ImportError:
        print("Installing SendGrid Python library...")
        os.system("pip install sendgrid")
        import sendgrid
        setup_sendgrid_smtp()
