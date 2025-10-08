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

# ============================================
# User Registration Email Notifications
# ============================================

def send_welcome_email(user_email: str, user_name: str, registration_date: str) -> bool:
    """Send welcome email to newly registered user"""
    from app.core.config import settings
    
    subject = "Bienvenue chez MALABRO - Votre compte a été créé ✨"
    
    # Sanitize user input to prevent injection
    safe_name = user_name.replace('<', '&lt;').replace('>', '&gt;')
    safe_email = user_email.replace('<', '&lt;').replace('>', '&gt;')
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px 10px 0 0;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px;">🎉 Bienvenue chez MALABRO!</h1>
            </div>
            
            <div style="padding: 30px; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Bonjour {safe_name}!</h2>
                
                <p style="font-size: 16px; line-height: 1.8;">
                    Nous sommes ravis de vous compter parmi nos membres. Votre compte a été créé avec succès!
                </p>
                
                <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #667eea;">
                    <h3 style="margin-top: 0; color: #667eea;">📋 Informations de votre compte</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>📧 Email:</strong></td>
                            <td style="padding: 8px 0;">{safe_email}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>👤 Nom:</strong></td>
                            <td style="padding: 8px 0;">{safe_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>📅 Date d'inscription:</strong></td>
                            <td style="padding: 8px 0;">{registration_date}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #2e7d32;">🚀 Prochaines étapes</h3>
                    <ol style="margin: 10px 0; padding-left: 20px; line-height: 2;">
                        <li>Connectez-vous avec votre email et mot de passe</li>
                        <li>Parcourez notre catalogue de produits</li>
                        <li>Ajoutez vos articles préférés au panier</li>
                        <li>Passez votre première commande en toute simplicité</li>
                    </ol>
                </div>
                
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #ff9800;">
                    <h3 style="margin-top: 0; color: #e65100;">💡 Besoin d'aide?</h3>
                    <p style="margin: 10px 0;">
                        Notre équipe est à votre disposition pour répondre à toutes vos questions.
                    </p>
                    <p style="margin: 10px 0;">
                        <strong>Email de support:</strong> {settings.ADMIN_EMAIL}<br>
                        <strong>Réponse:</strong> Sous 24h maximum
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 18px; color: #2c3e50; margin: 0;">
                        Merci de nous faire confiance!
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; margin-top: 20px;">
                <p style="font-size: 16px; color: #2c3e50; font-weight: bold; margin: 10px 0;">
                    Cordialement,<br>
                    L'équipe MALABRO
                </p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            
            <div style="text-align: center; padding: 10px;">
                <p style="font-size: 12px; color: #999; margin: 5px 0;">
                    Cet email a été envoyé automatiquement suite à votre inscription sur MALABRO.
                </p>
                <p style="font-size: 12px; color: #999; margin: 5px 0;">
                    © {datetime.now().year} MALABRO - Tous droits réservés
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        result = send_email(user_email, subject, body, is_html=True)
        if result:
            print(f"✅ Welcome email sent successfully to {user_email}")
        else:
            print(f"⚠️ Failed to send welcome email to {user_email}")
        return result
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False


def send_admin_new_user_notification(user_email: str, user_name: str, registration_date: str, is_active: bool, is_admin: bool) -> bool:
    """Send notification to admin about new user registration"""
    from app.core.config import settings
    
    # Sanitize user input
    safe_name = user_name.replace('<', '&lt;').replace('>', '&gt;')
    safe_email = user_email.replace('<', '&lt;').replace('>', '&gt;')
    
    subject = f"🆕 Nouvel utilisateur enregistré - {safe_name}"
    
    user_status = "✅ Actif" if is_active else "❌ Inactif"
    user_type = "👑 Administrateur" if is_admin else "👤 Utilisateur standard"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">🆕 Nouvelle inscription MALABRO</h2>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #2c3e50;">
                    Un nouvel utilisateur vient de s'inscrire sur la plateforme MALABRO.
                </p>
                
                <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="margin-top: 0; color: #667eea;">👤 Détails de l'utilisateur</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 12px 0; font-weight: bold; width: 40%;">Nom complet:</td>
                            <td style="padding: 12px 0;">{safe_name}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 12px 0; font-weight: bold;">Email:</td>
                            <td style="padding: 12px 0;">{safe_email}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 12px 0; font-weight: bold;">Date d'inscription:</td>
                            <td style="padding: 12px 0;">{registration_date}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 12px 0; font-weight: bold;">Statut:</td>
                            <td style="padding: 12px 0;">{user_status}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: bold;">Type de compte:</td>
                            <td style="padding: 12px 0;">{user_type}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3;">
                    <p style="margin: 0; color: #1565c0;">
                        <strong>ℹ️ Action automatique:</strong><br>
                        Un email de bienvenue a été automatiquement envoyé à l'utilisateur.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 25px 0; padding: 20px; background-color: #ffffff; border-radius: 8px;">
                    <p style="font-size: 14px; color: #666; margin: 0;">
                        Cet utilisateur peut maintenant se connecter et passer des commandes sur la plateforme.
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px;">
                <p style="color: #666; margin: 5px 0;">
                    Cordialement,<br>
                    <strong>Système MALABRO</strong>
                </p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            
            <div style="text-align: center;">
                <p style="font-size: 11px; color: #999; margin: 5px 0;">
                    Cette notification a été générée automatiquement par le système MALABRO.
                </p>
                <p style="font-size: 11px; color: #999; margin: 5px 0;">
                    © {datetime.now().year} MALABRO - Notification système
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        result = send_email(settings.ADMIN_EMAIL, subject, body, is_html=True)
        if result:
            print(f"✅ Admin notification sent successfully for new user: {user_email}")
        else:
            print(f"⚠️ Failed to send admin notification for new user: {user_email}")
        return result
    except Exception as e:
        print(f"❌ Error sending admin notification: {e}")
        return False


@router.post("/test-registration-email")
async def test_registration_email():
    """
    Test registration email functionality
    """
    from app.core.config import settings
    
    try:
        test_user_email = "test.user@example.com"
        test_user_name = "Test User"
        test_date = datetime.now().strftime('%d/%m/%Y à %H:%M')
        
        # Send both emails
        welcome_result = send_welcome_email(test_user_email, test_user_name, test_date)
        admin_result = send_admin_new_user_notification(
            test_user_email, 
            test_user_name, 
            test_date,
            is_active=True,
            is_admin=False
        )
        
        return {
            "message": "Test d'email d'inscription effectué",
            "welcome_email_sent": welcome_result,
            "admin_email_sent": admin_result,
            "test_user_email": test_user_email,
            "admin_email": settings.ADMIN_EMAIL,
            "smtp_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        return {
            "error": f"Erreur lors du test d'email d'inscription: {str(e)}",
            "smtp_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
