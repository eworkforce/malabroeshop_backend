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
    max_size = 5 * 1024 * 1024  # 5MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 5MB."
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
