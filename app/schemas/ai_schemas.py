"""
Pydantic schemas for AI Assistant API responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProductStock(BaseModel):
    name: str
    stock: int
    category: Optional[str] = None

class InventorySummary(BaseModel):
    total_products: int
    categories: List[str]
    low_stock_items: List[ProductStock]
    out_of_stock_items: List[str]
    total_value: float

class OrderInfo(BaseModel):
    reference: str
    customer: str
    amount: float
    created_at: str

class PendingPayments(BaseModel):
    count: int
    total_amount: float
    orders: List[OrderInfo]

class TopProduct(BaseModel):
    name: str
    sales_count: int
    revenue: float

class DailySummary(BaseModel):
    date: str
    orders_count: int
    revenue: float
    pending_revenue: float
    top_products: List[TopProduct]

class AIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    context_used: Optional[str] = None
