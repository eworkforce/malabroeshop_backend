from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import order as order_schemas
from app.crud import order as crud_order
from app.core.auth import get_current_user_optional
from app.models.user import User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter()

def send_admin_notification_email(order_id: int):
    """Send email notification to admin about new order"""
    try:
        # Create a new database session for the background task
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            # Fetch the order with its items
            order = crud_order.get(db, id=order_id)
            if not order:
                print(f"Order {order_id} not found for notification")
                return
            
            # Email configuration
            smtp_server = os.getenv("SMTP_SERVER", "smtp.sendgrid.net")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            from_email = os.getenv("SENDGRID_FROM_EMAIL", "admin@malabro.com")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@malabro.com")
            
            if not smtp_username or not smtp_password:
                print("SMTP credentials not configured - skipping email notification")
                return
            
            # Email content
            subject = f"Nouvelle commande MALABRO - {order.order_reference}"
            body = f"""Bonjour,

Une nouvelle commande a été passée sur MALABRO E-Shop.

DÉTAILS DE LA COMMANDE:
Référence: {order.order_reference}
Client: {order.customer_name}
Email: {order.customer_email}
Téléphone: {order.customer_phone}

ADRESSE DE LIVRAISON:
{order.shipping_address}
{order.shipping_city}, {order.shipping_country}

ARTICLES COMMANDÉS:
"""
            
            for item in order.order_items:
                body += f"- {item.product_name} x{item.quantity} = {item.subtotal:,.0f} FCFA\n"
            
            body += f"""
TOTAL: {order.total_amount:,.0f} FCFA

INSTRUCTIONS DE PAIEMENT:
Le client doit scanner le QR Code Wave et effectuer un paiement de {order.total_amount:,.0f} FCFA.
Référence à mentionner: {order.order_reference}

Veuillez vérifier le paiement Wave et confirmer la commande dans l'interface d'administration.

Cordialement,
Système MALABRO E-Shop
"""
            
            # Create and send email with enhanced debugging
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = admin_email
            msg['Subject'] = subject
            msg['Reply-To'] = from_email
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            print(f"📧 Preparing to send email:")
            print(f"   From: {from_email}")
            print(f"   To: {admin_email}")
            print(f"   Subject: {subject}")
            print(f"   SMTP Server: {smtp_server}:{smtp_port}")
            
            # Improved SMTP connection with timeout and error handling
            server = None
            try:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.set_debuglevel(1)  # Enable SMTP debugging
                server.starttls()
                server.login(smtp_username, smtp_password)
                
                # Send email and get response
                result = server.send_message(msg)
                server.quit()
                
                print(f"✅ Admin notification email sent successfully for order {order.order_reference}")
                print(f"   SMTP Response: {result}")
                
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ SMTP Authentication failed: {str(e)}")
            except smtplib.SMTPConnectError as e:
                print(f"❌ SMTP Connection failed: {str(e)}")
            except smtplib.SMTPRecipientsRefused as e:
                print(f"❌ SMTP Recipients refused: {str(e)}")
            except smtplib.SMTPSenderRefused as e:
                print(f"❌ SMTP Sender refused: {str(e)}")
            except smtplib.SMTPException as e:
                print(f"❌ SMTP Error: {str(e)}")
            except Exception as e:
                print(f"❌ Unexpected email error: {str(e)}")
            finally:
                if server:
                    try:
                        server.set_debuglevel(0)  # Disable debugging
                        server.quit()
                    except Exception:
                        pass
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"Failed to send admin notification email: {str(e)}")

@router.post("/", response_model=order_schemas.OrderConfirmation)
def create_order(
    order: order_schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a new order"""
    
    # Validate order items (ensure products exist, prices are correct, and stock is sufficient)
    validation_error = crud_order.validate_items(db, items=order.items)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)
    
    # Create the order
    user_id = current_user.id if current_user else None
    db_order = crud_order.create_with_owner(db=db, obj_in=order, user_id=user_id)
    
    # Send admin notification email in background
    background_tasks.add_task(send_admin_notification_email, db_order.id)
    
    return order_schemas.OrderConfirmation(
        order_id=db_order.id,
        order_reference=db_order.order_reference,
        total_amount=db_order.total_amount,
        customer_email=db_order.customer_email,
        message=f"Votre commande {db_order.order_reference} a été créée avec succès. Veuillez procéder au paiement via le QR Code Wave."
    )

@router.get("/{order_id}", response_model=order_schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    db_order = crud_order.get_order(db=db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/reference/{order_reference}", response_model=order_schemas.Order)
def get_order_by_reference(order_reference: str, db: Session = Depends(get_db)):
    """Get order by reference number"""
    db_order = crud_order.get_order_by_reference(db=db, order_reference=order_reference)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/", response_model=List[order_schemas.OrderSummary])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get orders (user's orders if authenticated, or all orders for admin)"""
    if current_user:
        # Return user's orders
        orders = crud_order.get_user_orders(db=db, user_id=current_user.id, skip=skip, limit=limit)
    else:
        # For now, return empty list for unauthenticated users
        # In the future, this could be admin-only endpoint
        orders = []
    
    return orders

@router.put("/{order_id}/status", response_model=order_schemas.Order)
def update_order_status(
    order_id: int,
    order_update: order_schemas.OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update order status (admin only - no auth check for now)"""
    db_order = crud_order.update_order_status(
        db=db,
        order_id=order_id,
        status=order_update.status,
        payment_notes=order_update.payment_notes
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/admin/pending", response_model=List[order_schemas.OrderSummary])
def get_pending_orders(db: Session = Depends(get_db)):
    """Get all pending orders for admin review"""
    orders = crud_order.get_pending_orders(db=db)
    return orders
