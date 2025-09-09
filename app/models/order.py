from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for guest orders
    
    # Order details
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, paid, processing, shipped, delivered, cancelled
    order_reference = Column(String(20), unique=True, index=True)
    
    # Customer information
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    
    # Shipping address
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(50), nullable=False)
    shipping_country = Column(String(50), default="Sénégal")
    
    # Billing address (optional, can be same as shipping)
    billing_address = Column(Text, nullable=True)
    billing_city = Column(String(50), nullable=True)
    billing_country = Column(String(50), nullable=True)
    
    # Payment information
    payment_method = Column(String(50), default="wave_qr")
    payment_confirmed_at = Column(DateTime, nullable=True)
    payment_notes = Column(Text, nullable=True)  # Admin notes about payment verification
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="orders")  # Temporarily commented to fix mapping issue
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details (captured at time of order to preserve pricing)
    product_name = Column(String(200), nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)  # price * quantity
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
