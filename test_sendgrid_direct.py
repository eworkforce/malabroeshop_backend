#!/usr/bin/env python3
"""
Direct SendGrid API test to verify email delivery
Bypasses SMTP and uses SendGrid's native API
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

def test_sendgrid_api():
    """Test SendGrid API directly"""
    
    # SendGrid configuration - using environment variables
    import os
    api_key = os.getenv('SMTP_PASSWORD', 'your-sendgrid-api-key-here')
    from_email = os.getenv('SENDGRID_FROM_EMAIL', 'sergeziehi@eworkforce.africa')
    to_email = "sergeziehi@eworkforce.africa"
    
    if api_key == 'your-sendgrid-api-key-here':
        print("❌ Error: Please set SMTP_PASSWORD environment variable with your SendGrid API key")
        return False
    
    # Create email content
    subject = "🎉 MALABRO SendGrid Test - Direct API"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #8A307F;">🎉 MALABRO SendGrid Integration Success!</h2>
            
            <p>Excellent! Your MALABRO platform is now configured with SendGrid for reliable email delivery.</p>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #F28C28; margin-top: 0;">Test Details:</h3>
                <ul>
                    <li><strong>Service:</strong> SendGrid API (Google Cloud Partner)</li>
                    <li><strong>Test Time:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</li>
                    <li><strong>Status:</strong> ✅ Production Ready</li>
                </ul>
            </div>
            
            <h3 style="color: #8A307F;">Payment Notifications Ready:</h3>
            <ol>
                <li>✅ Admin payment alerts</li>
                <li>✅ Customer order confirmations</li>
                <li>✅ Wave payment process notifications</li>
            </ol>
            
            <p style="background: #e8f5e8; padding: 10px; border-radius: 5px;">
                <strong>Next Step:</strong> Your payment notification workflow is now fully operational!
            </p>
            
            <p style="margin-top: 30px;">
                Cordialement,<br>
                <strong>L'équipe MALABRO</strong><br>
                <em>Fraîcheur et qualité à votre porte</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=api_key)
        
        # Create mail object
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Send email
        print("Sending test email via SendGrid API...")
        response = sg.send(message)
        
        print(f"✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        return True
        
    except Exception as e:
        print(f"❌ SendGrid API test failed: {e}")
        return False

if __name__ == "__main__":
    print("MALABRO SendGrid Direct API Test")
    print("=" * 40)
    test_sendgrid_api()
