from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

router = APIRouter()

class PaymentNotificationRequest(BaseModel):
    order_reference: str
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    total_amount: float
    payment_method: Optional[str] = "wave"
    # Remove admin_email from request - will be loaded from settings

def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    """Send email using SMTP"""
    try:
        from app.core.config import settings
        
        # Email configuration from settings
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        smtp_username = settings.SMTP_USERNAME
        smtp_password = settings.SMTP_PASSWORD
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured")
            return False
        
        # Create message with verified sender
        msg = MIMEMultipart()
        from_email = settings.SENDGRID_FROM_EMAIL if hasattr(settings, 'SENDGRID_FROM_EMAIL') and settings.SENDGRID_FROM_EMAIL else smtp_username
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port != 1025:  # Skip TLS for local testing
            server.starttls()  # Enable security
            if smtp_username and smtp_password:  # Only login if credentials provided
                server.login(smtp_username, smtp_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_admin_notification(notification_data: PaymentNotificationRequest, admin_email: str):
    """Send notification to admin about payment start"""
    subject = f"🔔 Nouveau paiement initié - Commande {notification_data.order_reference}"
    
    body = f"""
    <html>
    <body>
        <h2>Notification de paiement MALABRO</h2>
        <p>Un client a initié un processus de paiement via {notification_data.payment_method.title()}.</p>
        
        <h3>Détails de la commande:</h3>
        <ul>
            <li><strong>Référence:</strong> {notification_data.order_reference}</li>
            <li><strong>Client:</strong> {notification_data.customer_name}</li>
            <li><strong>Email:</strong> {notification_data.customer_email}</li>
            <li><strong>Téléphone:</strong> {notification_data.customer_phone}</li>
            <li><strong>Montant:</strong> {notification_data.total_amount:,.0f} FCFA</li>
            <li><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</li>
        </ul>
        
        <p><strong>Action requise:</strong> Surveillez votre compte Wave pour confirmer la réception du paiement.</p>
        
        <p>Cordialement,<br>Système MALABRO</p>
    </body>
    </html>
    """
    
    return send_email(admin_email, subject, body, is_html=True)

def send_customer_notification(notification_data: PaymentNotificationRequest):
    """Send notification to customer about payment process"""
    subject = f"Confirmation de commande - {notification_data.order_reference}"
    
    body = f"""
    <html>
    <body>
        <h2>Merci pour votre commande MALABRO!</h2>
        <p>Bonjour {notification_data.customer_name},</p>
        
        <p>Nous avons bien reçu votre demande de paiement pour la commande <strong>{notification_data.order_reference}</strong>.</p>
        
        <h3>Détails de votre commande:</h3>
        <ul>
            <li><strong>Référence:</strong> {notification_data.order_reference}</li>
            <li><strong>Montant:</strong> {notification_data.total_amount:,.0f} FCFA</li>
            <li><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</li>
        </ul>
        
        <p><strong>Prochaines étapes:</strong></p>
        <ol>
            <li>Effectuez votre paiement via le lien Wave fourni</li>
            <li>Notre équipe vérifiera votre paiement</li>
            <li>Vous serez contacté dans les plus brefs délais pour la livraison</li>
        </ol>
        
        <p>Pour toute question, n'hésitez pas à nous contacter.</p>
        
        <p>Cordialement,<br>L'équipe MALABRO</p>
    </body>
    </html>
    """
    
    return send_email(notification_data.customer_email, subject, body, is_html=True)

@router.post("/test-email")
async def test_email_notification():
    """
    Test email functionality
    """
    from app.core.config import settings
    
    try:
        # Test data
        test_data = PaymentNotificationRequest(
            order_reference="TEST-001",
            customer_name="Test Customer",
            customer_email="test@example.com",
            customer_phone="+225 XX XXX XX XX",
            total_amount=15000
        )
        
        # Try to send emails immediately (not in background for testing)
        admin_result = send_admin_notification(test_data, settings.ADMIN_EMAIL)
        customer_result = send_customer_notification(test_data)
        
        return {
            "message": "Test email envoyé",
            "admin_email_sent": admin_result,
            "customer_email_sent": customer_result,
            "smtp_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        return {
            "error": f"Erreur lors du test email: {str(e)}",
            "smtp_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }

@router.post("/payment-started")
async def notify_payment_started(
    notification_data: PaymentNotificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Send notifications when a customer starts the payment process
    """
    try:
        from app.core.config import settings
        
        # Send notifications in background using admin email from settings
        background_tasks.add_task(send_admin_notification, notification_data, settings.ADMIN_EMAIL)
        background_tasks.add_task(send_customer_notification, notification_data)
        
        return {
            "message": "Notifications envoyées avec succès",
            "order_reference": notification_data.order_reference
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi des notifications: {str(e)}"
        )
