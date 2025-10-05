from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from .product import Product

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    shipping_address: str
    shipping_city: str
    shipping_country: str = "Sénégal"
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_confirmed_at: Optional[datetime] = None
    payment_notes: Optional[str] = None

class Order(OrderBase):
    id: int
    user_id: Optional[int] = None
    total_amount: float
    status: str
    order_reference: str
    payment_method: str
    payment_confirmed_at: Optional[datetime] = None
    payment_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItem] = []
    
    class Config:
        from_attributes = True

# Response schemas
class OrderSummary(BaseModel):
    id: int
    order_reference: str
    total_amount: float
    status: str
    customer_name: str
    customer_email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderConfirmation(BaseModel):
    order_id: int
    order_reference: str
    total_amount: float
    customer_email: str
    message: str

# Delivery Preparation Schemas
class OrderItemSummary(BaseModel):
    """Summary of an order item for preparation view"""
    order_id: int
    order_reference: str
    customer_name: str
    quantity: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductPreparationSummary(BaseModel):
    """Summary of a product across all paid orders"""
    product_id: int
    product_name: str
    total_quantity: int
    unit: Optional[str] = None
    order_count: int
    unique_customers: int
    orders: List[OrderItemSummary] = []
    
    class Config:
        from_attributes = True

class DeliveryPreparationSummary(BaseModel):
    """Complete delivery preparation summary"""
    summary: dict
    products: List[ProductPreparationSummary]
    date_range: dict
    
    class Config:
        from_attributes = True
