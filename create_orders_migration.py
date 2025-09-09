#!/usr/bin/env python3
"""
Simple database migration script to create orders and order_items tables.
Run this from the backend directory.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Create base class
Base = declarative_base()

# Define Order model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Will add FK constraint later when users table exists
    order_reference = Column(String(50), unique=True, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    payment_method = Column(String(20), default="wave_qr")
    
    # Customer information
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    
    # Shipping information
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(50), nullable=False)
    shipping_country = Column(String(50), default="Sénégal")
    
    # Billing information (optional, defaults to shipping)
    billing_address = Column(Text, nullable=True)
    billing_city = Column(String(50), nullable=True)
    billing_country = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Define OrderItem model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(200), nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

def main():
    # Database URL
    DATABASE_URL = "sqlite:///./malabro_eshop.db"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Create tables
        print("Creating orders and order_items tables...")
        Base.metadata.create_all(bind=engine, tables=[Order.__table__, OrderItem.__table__])
        print("✅ Orders tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "orders" in tables and "order_items" in tables:
            print("✅ Verified: Both 'orders' and 'order_items' tables exist in database")
            
            # Show table info
            orders_columns = [col['name'] for col in inspector.get_columns('orders')]
            order_items_columns = [col['name'] for col in inspector.get_columns('order_items')]
            
            print(f"📋 Orders table columns: {', '.join(orders_columns)}")
            print(f"📋 Order items table columns: {', '.join(order_items_columns)}")
        else:
            print("❌ Error: Tables were not created properly")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
