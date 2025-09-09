import secrets
import string
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate, OrderItemCreate
from app.schemas.inventory_ledger import InventoryLedgerCreate
from app import crud

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def _generate_order_reference(self, db: Session) -> str:
        chars = string.ascii_uppercase + string.digits
        while True:
            random_part = ''.join(secrets.choice(chars) for _ in range(6))
            ref = f"MALABRO-{random_part}"
            if not db.query(Order).filter(Order.order_reference == ref).first():
                return ref

    def create_with_owner(self, db: Session, *, obj_in: OrderCreate, user_id: Optional[int] = None) -> Order:
        total_amount = sum(item.subtotal for item in obj_in.items)
        order_reference = self._generate_order_reference(db)
        
        db_obj = Order(
            user_id=user_id,
            total_amount=total_amount,
            order_reference=order_reference,
            customer_name=obj_in.customer_name,
            customer_email=obj_in.customer_email,
            customer_phone=obj_in.customer_phone,
            shipping_address=obj_in.shipping_address,
            shipping_city=obj_in.shipping_city,
            shipping_country=obj_in.shipping_country,
            billing_address=obj_in.billing_address or obj_in.shipping_address,
            billing_city=obj_in.billing_city or obj_in.shipping_city,
            billing_country=obj_in.billing_country or obj_in.shipping_country,
            payment_method="wave_qr",
            status="pending"
        )
        
        db.add(db_obj)
        db.flush()

        for item in obj_in.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                # Update stock
                original_stock = product.stock_quantity
                product.stock_quantity -= item.quantity
                db.add(product)

                # Create inventory ledger entry for the sale
                ledger_in = InventoryLedgerCreate(
                    product_id=product.id,
                    change_type="Sale",
                    quantity_change=-item.quantity,
                    new_quantity=product.stock_quantity,
                    order_id=db_obj.id,
                    user_id=user_id,
                    notes=f"Order {order_reference}"
                )
                crud.inventory_ledger.create(db=db, obj_in=ledger_in)

            db.add(OrderItem(**item.dict(), order_id=db_obj.id))

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return (
            db.query(self.model)
            .filter(Order.user_id == user_id)
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_reference(self, db: Session, *, order_reference: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_reference == order_reference).first()

    def update_status(self, db: Session, *, db_obj: Order, status: str, payment_notes: Optional[str] = None) -> Order:
        db_obj.status = status
        if payment_notes:
            db_obj.payment_notes = payment_notes
        if status == "paid":
            from datetime import datetime
            db_obj.payment_confirmed_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_pending(self, db: Session) -> List[Order]:
        return db.query(self.model).filter(Order.status == "pending").order_by(desc(Order.created_at)).all()

    def validate_items(self, db: Session, *, items: List[OrderItemCreate]) -> Optional[str]:
        """
        Validates order items for existence, price, and stock.
        Returns an error message string if invalid, otherwise None.
        """
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                return f"Le produit avec l'ID {item.product_id} n'a pas été trouvé."
            
            if abs(product.price - item.product_price) > 0.01:
                return f"Le prix du produit '{product.name}' ne correspond pas. Attendu: {product.price}, reçu: {item.product_price}."

            if product.stock_quantity < item.quantity:
                return f"Stock insuffisant pour le produit '{product.name}'. Demandé: {item.quantity}, Disponible: {product.stock_quantity}."
        
        return None

order = CRUDOrder(Order)
