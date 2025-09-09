"""
AI Tools API endpoints for MALABRO eShop MCP Server
These endpoints will be automatically exposed as MCP tools for LLM access
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from app.db.session import get_db
from app.crud import product, order
from app.schemas.ai_schemas import (
    InventorySummary, PendingPayments, DailySummary, 
    ProductStock, OrderInfo, TopProduct
)

router = APIRouter(prefix="/ai-tools", tags=["AI Tools"])

@router.get("/inventory/summary", response_model=InventorySummary)
def get_inventory_summary(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by product category")
):
    """
    Get current inventory status - perfect for AI to answer stock questions
    
    This tool provides:
    - Total product count
    - Available categories
    - Low stock items (< 10 units)
    - Out of stock items
    - Total inventory value
    """
    try:
        # Get all products with stock information
        products = product.get_multi(db)
        
        if category:
            # Filter by category if specified
            products = [p for p in products if p.category and p.category.name.lower() == category.lower()]
        
        # Analyze stock levels
        low_stock = [
            ProductStock(
                name=p.name, 
                stock=p.stock_quantity,
                category=p.category.name if p.category else None
            ) 
            for p in products if p.stock_quantity < 10 and p.stock_quantity > 0
        ]
        
        out_of_stock = [p.name for p in products if p.stock_quantity == 0]
        
        # Get unique categories
        categories = list(set([p.category.name for p in products if p.category]))
        
        # Calculate total inventory value
        total_value = sum(p.price * p.stock_quantity for p in products)
        
        return InventorySummary(
            total_products=len(products),
            categories=categories,
            low_stock_items=low_stock,
            out_of_stock_items=out_of_stock,
            total_value=total_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventory: {str(e)}")

@router.get("/payments/pending", response_model=PendingPayments)
def get_pending_payments(
    db: Session = Depends(get_db)
):
    """
    Get all orders with pending payment status.
    
    This tool provides:
    - Count of pending payment orders
    - Total amount awaiting confirmation
    - Detailed list of pending orders with customer info
    """
    try:
        # Get orders with pending payment status
        pending_orders = order.get_pending(db)
        
        # Format order information
        order_info = [
            OrderInfo(
                reference=order.order_reference,
                customer=order.customer_name,
                amount=float(order.total_amount),
                created_at=order.created_at.isoformat()
            )
            for order in pending_orders
        ]
        
        total_amount = sum(order.total_amount for order in pending_orders)
        
        return PendingPayments(
            count=len(pending_orders),
            total_amount=float(total_amount),
            orders=order_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending payments: {str(e)}")

@router.get("/analytics/daily-summary", response_model=DailySummary)
def get_daily_summary(
    db: Session = Depends(get_db),
    target_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, defaults to today")
):
    """
    Get business metrics for a specific day - AI can provide daily performance insights
    
    This tool provides:
    - Order count for the day
    - Confirmed revenue (paid orders)
    - Pending revenue (unpaid orders)
    - Top selling products
    """
    try:
        # Parse target date or use today
        if target_date:
            try:
                query_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            query_date = date.today()
        
        # Get orders for the specified date
        start_datetime = datetime.combine(query_date, datetime.min.time())
        end_datetime = datetime.combine(query_date, datetime.max.time())
        
        # Filter orders by date range
        all_orders = order.get_multi(db)
        day_orders = [
            order for order in all_orders 
            if start_datetime <= order.created_at <= end_datetime
        ]
        
        # Calculate metrics
        paid_orders = [order for order in day_orders if order.status == "paid"]
        pending_orders = [order for order in day_orders if order.status == "pending"]
        
        revenue = sum(order.total_amount for order in paid_orders)
        pending_revenue = sum(order.total_amount for order in pending_orders)
        
        # Get top products (simplified - would need order items for accurate data)
        top_products = [
            TopProduct(name="Sample Product", sales_count=1, revenue=10.0)
        ]  # TODO: Implement proper top products calculation when order items are available
        
        return DailySummary(
            date=query_date.isoformat(),
            orders_count=len(day_orders),
            revenue=float(revenue),
            pending_revenue=float(pending_revenue),
            top_products=top_products
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily summary: {str(e)}")

@router.get("/products/search")
def search_products(
    db: Session = Depends(get_db),
    query: str = Query(..., description="Product name or category to search"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Search products by name or category - AI can help find specific products
    
    This tool provides:
    - Product search by name (partial matching)
    - Current stock levels
    - Pricing information
    """
    try:
        products = product.get_multi(db)
        
        # Simple search by name (case-insensitive)
        matching_products = [
            {
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "stock": p.stock_quantity,
                "category": p.category.name if p.category else None,
                "status": "In Stock" if p.stock_quantity > 0 else "Out of Stock"
            }
            for p in products
            if query.lower() in p.name.lower() or 
               (p.category and query.lower() in p.category.name.lower())
        ][:limit]
        
        return {
            "query": query,
            "results_count": len(matching_products),
            "products": matching_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

@router.get("/orders/recent")
def get_recent_orders(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Number of recent orders to fetch"),
    status: Optional[str] = Query(None, description="Filter by order status")
):
    """
    Get recent orders - AI can provide updates on latest customer activity
    
    This tool provides:
    - Most recent orders
    - Order status and customer information
    - Order values and timestamps
    """
    try:
        orders = order.get_multi(db, limit=limit)
        
        if status:
            orders = [order for order in orders if order.status == status]
        
        recent_orders = [
            {
                "reference": order.order_reference,
                "customer": order.customer_name,
                "email": order.customer_email,
                "status": order.status,
                "amount": float(order.total_amount),
                "created_at": order.created_at.isoformat(),
                "payment_method": getattr(order, 'payment_method', 'N/A')
            }
            for order in orders
        ]
        
        return {
            "orders_count": len(recent_orders),
            "orders": recent_orders
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent orders: {str(e)}")

@router.get("/alerts/business")
def get_business_alerts(db: Session = Depends(get_db)):
    """
    Get important business alerts - AI can proactively notify admin of issues
    
    This tool provides:
    - Low stock alerts
    - Pending payment alerts
    - Revenue alerts
    - System status
    """
    try:
        alerts = []
        
        # Check for low stock items
        products = product.get_multi(db)
        low_stock_count = len([p for p in products if 0 < p.stock_quantity < 10])
        out_of_stock_count = len([p for p in products if p.stock_quantity == 0])
        
        if low_stock_count > 0:
            alerts.append({
                "type": "warning",
                "category": "inventory",
                "message": f"{low_stock_count} products are running low on stock",
                "priority": "medium"
            })
            
        if out_of_stock_count > 0:
            alerts.append({
                "type": "error",
                "category": "inventory", 
                "message": f"{out_of_stock_count} products are out of stock",
                "priority": "high"
            })
        
        # Check for pending payments
        pending_orders = order.get_pending(db)
        if len(pending_orders) > 0:
            total_pending = sum(order.total_amount for order in pending_orders)
            alerts.append({
                "type": "info",
                "category": "payments",
                "message": f"{len(pending_orders)} orders awaiting payment confirmation (€{total_pending:.2f})",
                "priority": "medium"
            })
        
        return {
            "alerts_count": len(alerts),
            "alerts": alerts,
            "status": "healthy" if len(alerts) == 0 else "needs_attention"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching business alerts: {str(e)}")

@router.post("/chat")
def chat_with_mala_ia_bro(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint for Mala-IA-Bro AI assistant.
    
    Processes user messages and returns AI responses using Groq LLM
    with shop context and MCP tools integration.
    """
    try:
        from app.services.groq_client import GroqClient
        
        message = request.get("message", "")
        system_prompt = request.get("system_prompt", "")
        context = request.get("context", {})
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Initialize Groq client
        groq_client = GroqClient()
        
        # Send message to Groq with shop context
        response = groq_client.chat_completion(
            message=message,
            system_prompt=system_prompt,
            context=context
        )
        
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
