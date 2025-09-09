#!/usr/bin/env python3
"""
Test script to send real emails using Gmail SMTP
This bypasses the local SMTP server and sends actual emails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_test_email():
    """Send a real test email to sergeziehi@eworkforce.africa"""
    
    # Gmail SMTP configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "sergeziehi@eworkforce.africa"
    smtp_password = input("Enter your Gmail App Password: ")
    
    # Email details
    to_email = "sergeziehi@eworkforce.africa"
    subject = "🔔 MALABRO Test Email - Payment Notification System"
    
    # HTML email body
    body = f"""
    <html>
    <body>
        <h2>MALABRO Email Notification Test</h2>
        <p>This is a test email from the MALABRO payment notification system.</p>
        
        <h3>Test Details:</h3>
        <ul>
            <li><strong>Test Type:</strong> Real Email Delivery</li>
            <li><strong>Order Reference:</strong> TEST-REAL-001</li>
            <li><strong>Amount:</strong> 15,000 FCFA</li>
            <li><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</li>
        </ul>
        
        <p><strong>Status:</strong> ✅ Email notification system is working correctly!</p>
        
        <p>This confirms that the MALABRO platform can successfully send email notifications for:</p>
        <ol>
            <li>Payment initiation alerts to admin</li>
            <li>Order confirmations to customers</li>
            <li>Payment process updates</li>
        </ol>
        
        <p>Cordialement,<br>L'équipe MALABRO</p>
    </body>
    </html>
    """
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'html'))
        
        # Create SMTP session
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(smtp_username, smtp_password)
        
        # Send email
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        print(f"✅ Test email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("MALABRO Email Test Script")
    print("=" * 40)
    send_test_email()
