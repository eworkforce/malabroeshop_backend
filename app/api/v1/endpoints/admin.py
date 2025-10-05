import mimetypes
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pathlib import Path

from app.db.session import get_db
from app.core.auth import get_current_admin_user
from app.core.supabase import supabase_storage
from app.models.user import User
from app.models.order import Order
from app.schemas import user as user_schemas
from app.schemas import order as order_schemas
from app.crud import user as crud_user
from app.crud import order as crud_order

router = APIRouter()


@router.get("/dashboard", response_model=dict)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get admin dashboard overview with key metrics"""
    
    # Get key metrics
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    completed_orders = db.query(Order).filter(Order.status == "paid").count()
    total_users = db.query(User).count()
    
    # Get total revenue (from paid orders)
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status == "paid").scalar() or 0
    
    # Get recent orders (last 10)
    recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()
    
    return {
        "metrics": {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "total_users": total_users,
            "total_revenue": float(total_revenue)
        },
        "recent_orders": [
            {
                "id": order.id,
                "order_reference": order.order_reference,
                "customer_name": order.customer_name,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at
            }
            for order in recent_orders
        ]
    }


@router.get("/orders", response_model=List[order_schemas.OrderSummary])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all orders with optional filtering"""
    
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    return [
        order_schemas.OrderSummary(
            id=order.id,
            order_reference=order.order_reference,
            total_amount=order.total_amount,
            status=order.status,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            created_at=order.created_at
        )
        for order in orders
    ]



# ===== DELIVERY PREPARATION ENDPOINT =====

@router.get("/orders/preparation-summary", response_model=dict)
def get_delivery_preparation_summary(
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get delivery preparation summary for all paid orders.
    
    Aggregates paid orders by product to help admin prepare deliveries.
    Only includes orders with status='paid'.
    
    Query Parameters:
    - date_from: Start date filter (optional, format: YYYY-MM-DD)
    - date_to: End date filter (optional, format: YYYY-MM-DD)
    
    Returns:
    - summary: Overall metrics (total paid orders, unique products, etc.)
    - products: List of products with aggregated quantities and order details
    - date_range: Applied date filters
    """
    from datetime import datetime
    from app.models.order import OrderItem
    from app.models.product import Product
    from app.models.unit_of_measure import UnitOfMeasure
    
    # Build base query for paid orders
    query = db.query(Order).filter(Order.status == "paid")
    
    # Apply date filters if provided
    date_from_parsed = None
    date_to_parsed = None
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Order.created_at >= date_from_parsed)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            # Add 1 day to include the entire end date
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d")
            # Set to end of day
            from datetime import timedelta
            date_to_end = date_to_parsed + timedelta(days=1)
            query = query.filter(Order.created_at < date_to_end)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    # Get all paid orders
    paid_orders = query.all()
    
    if not paid_orders:
        return {
            "summary": {
                "total_paid_orders": 0,
                "total_unique_products": 0,
                "total_revenue": 0,
                "last_updated": datetime.utcnow().isoformat()
            },
            "products": [],
            "date_range": {
                "date_from": date_from,
                "date_to": date_to
            }
        }
    
    # Aggregate products from all order items
    product_aggregation = {}
    total_revenue = 0
    
    for order in paid_orders:
        total_revenue += order.total_amount
        
        for item in order.order_items:
            product_id = item.product_id
            
            if product_id not in product_aggregation:
                # Get product details
                product = db.query(Product).filter(Product.id == product_id).first()
                unit_name = None
                
                if product and product.unit_of_measure:
                    unit_name = product.unit_of_measure.abbreviation or product.unit_of_measure.name
                
                product_aggregation[product_id] = {
                    "product_id": product_id,
                    "product_name": item.product_name,
                    "total_quantity": 0,
                    "unit": unit_name,
                    "order_count": 0,
                    "unique_customers": set(),
                    "orders": []
                }
            
            # Add quantity
            product_aggregation[product_id]["total_quantity"] += item.quantity
            
            # Track unique customers
            product_aggregation[product_id]["unique_customers"].add(order.customer_email)
            
            # Check if this order is already in the list for this product
            order_already_added = any(
                o["order_id"] == order.id 
                for o in product_aggregation[product_id]["orders"]
            )
            
            if not order_already_added:
                product_aggregation[product_id]["order_count"] += 1
                product_aggregation[product_id]["orders"].append({
                    "order_id": order.id,
                    "order_reference": order.order_reference,
                    "customer_name": order.customer_name,
                    "quantity": item.quantity,
                    "created_at": order.created_at.isoformat()
                })
            else:
                # Update quantity for existing order entry
                for o in product_aggregation[product_id]["orders"]:
                    if o["order_id"] == order.id:
                        o["quantity"] += item.quantity
                        break
    
    # Convert to list and prepare response
    products_list = []
    for product_data in product_aggregation.values():
        # Convert set to count
        unique_customers_count = len(product_data["unique_customers"])
        product_data["unique_customers"] = unique_customers_count
        
        # Sort orders by created_at (most recent first)
        product_data["orders"].sort(
            key=lambda x: x["created_at"],
            reverse=True
        )
        
        products_list.append(product_data)
    
    # Sort products by total quantity (highest first)
    products_list.sort(key=lambda x: x["total_quantity"], reverse=True)
    
    return {
        "summary": {
            "total_paid_orders": len(paid_orders),
            "total_unique_products": len(products_list),
            "total_revenue": float(total_revenue),
            "last_updated": datetime.utcnow().isoformat()
        },
        "products": products_list,
        "date_range": {
            "date_from": date_from,
            "date_to": date_to
        }
    }



@router.get("/orders/{order_id}", response_model=order_schemas.Order)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get detailed order information"""
    
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    payment_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update order status (admin only)"""
    
    # Validate status
    valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Get the order first
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the order status
    order = crud_order.update_status(
        db=db, 
        db_obj=order, 
        status=status, 
        payment_notes=payment_notes
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": f"Order {order.order_reference} status updated to {status}"}


@router.get("/users", response_model=List[user_schemas.User])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Activate or deactivate a user (admin only)"""
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    status_text = "activated" if is_active else "deactivated"
    return {"message": f"User {user.email} has been {status_text}"}


@router.get("/pending-orders", response_model=List[order_schemas.OrderSummary])
def get_pending_orders(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all pending orders for payment verification"""
    
    orders = crud_order.get_pending(db)
    
    return [
        order_schemas.OrderSummary(
            id=order.id,
            order_reference=order.order_reference,
            total_amount=order.total_amount,
            status=order.status,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            created_at=order.created_at
        )
        for order in orders
    ]


# ===== PRODUCT MANAGEMENT ENDPOINTS =====

@router.get("/products", response_model=List[dict])
def get_all_products_admin(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search products by name or category"),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all products with admin details (stock, status, etc.)"""
    
    from app.models.product import Product
    
    query = db.query(Product)
    
    # Apply search filter
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )
    
    # Apply status filter (skip since is_active field doesn't exist in current model)
    # if status == "active":
    #     query = query.filter(Product.is_active == True)
    # elif status == "inactive":
    #     query = query.filter(Product.is_active == False)
    
    products = query.order_by(Product.name).offset(skip).limit(limit).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": getattr(product, 'category', 'Non classé'),
            "image_url": product.image_url,
            "stock_quantity": getattr(product, 'stock_quantity', 0),
            "is_active": getattr(product, 'is_active', True),
            "created_at": getattr(product, 'created_at', None),
            "updated_at": getattr(product, 'updated_at', None)
        }
        for product in products
    ]


@router.post("/products", response_model=dict)
def create_product(
    product_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new product (admin only)"""
    
    from app.models.product import Product
    from datetime import datetime
    
    # Validate required fields
    required_fields = ["name", "description", "price", "category"]
    for field in required_fields:
        if field not in product_data or not product_data[field]:
            raise HTTPException(
                status_code=400,
                detail=f"Field '{field}' is required"
            )
    
    # Create new product
    new_product = Product(
        name=product_data["name"],
        description=product_data["description"],
        price=float(product_data["price"]),
        category=product_data["category"],
        image_url=product_data.get("image_url", ""),
        stock_quantity=product_data.get("stock_quantity", 0),
        is_active=product_data.get("is_active", True)
    )
    
    # Add created_at if the model supports it
    if hasattr(new_product, 'created_at'):
        new_product.created_at = datetime.utcnow()
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {
        "message": f"Product '{new_product.name}' created successfully",
        "product_id": new_product.id
    }


@router.put("/products/{product_id}", response_model=dict)
def update_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update an existing product (admin only)"""
    
    from app.models.product import Product
    from datetime import datetime
    
    # Get existing product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    updateable_fields = [
        "name", "description", "price", "category", 
        "image_url", "stock_quantity", "is_active"
    ]
    
    for field in updateable_fields:
        if field in product_data:
            if field == "price":
                setattr(product, field, float(product_data[field]))
            elif field == "stock_quantity":
                setattr(product, field, int(product_data[field]) if product_data[field] is not None else 0)
            elif field == "is_active":
                setattr(product, field, bool(product_data[field]))
            else:
                setattr(product, field, product_data[field])
    
    # Update timestamp if supported
    if hasattr(product, 'updated_at'):
        product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": f"Product '{product.name}' updated successfully",
        "product_id": product.id
    }


@router.delete("/products/{product_id}", response_model=dict)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a product (admin only)"""
    
    from app.models.product import Product
    
    # Get existing product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_name = product.name
    
    # Delete the product
    db.delete(product)
    db.commit()
    
    return {
        "message": f"Product '{product_name}' deleted successfully",
        "product_id": product_id
    }


@router.put("/products/{product_id}/status", response_model=dict)
def toggle_product_status(
    product_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Toggle product active/inactive status (admin only)"""
    
    from app.models.product import Product
    from datetime import datetime
    
    # Get existing product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update status
    if hasattr(product, 'is_active'):
        product.is_active = is_active
    
    # Update timestamp if supported
    if hasattr(product, 'updated_at'):
        product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    status_text = "activated" if is_active else "deactivated"
    return {
        "message": f"Product '{product.name}' has been {status_text}",
        "product_id": product.id
    }


@router.post("/products/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload a product image to Supabase Storage and return the public URL"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed."
        )
    
    # Validate file size (5MB max)
    max_size = 1024 * 1024  # 1MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 1MB. Please compress your image."
        )
    
    # Get file extension
    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    
    try:
        # Upload directly to Supabase Storage (no local fallback)
        if not supabase_storage.client:
            raise HTTPException(
                status_code=503,
                detail="Supabase Storage is not available. Please check configuration."
            )
        
        image_url = await supabase_storage.upload_image(file_content, file_extension)
        
        # Verify we got a Supabase URL
        if not image_url or not image_url.startswith('https://'):
            raise HTTPException(
                status_code=500,
                detail="Failed to upload image to Supabase Storage"
            )
        
        return {
            "message": "Image uploaded successfully to Supabase Storage",
            "image_url": image_url,
            "storage_type": "supabase"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )
