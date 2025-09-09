from typing import List, Any, Dict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app import crud, models, schemas
from app.api.v1.endpoints import auth as deps
from app.db.session import get_db

router = APIRouter()


@router.get("/summary", response_model=Dict[str, Any])
def get_inventory_summary(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """Get inventory summary statistics."""
    
    # Total products
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()
    
    # Total stock value
    stock_value_query = db.query(
        func.sum(models.Product.price * models.Product.stock_quantity)
    ).filter(models.Product.is_active == True).scalar()
    total_stock_value = float(stock_value_query) if stock_value_query else 0.0
    
    # Total stock quantity
    total_stock_quantity = db.query(
        func.sum(models.Product.stock_quantity)
    ).filter(models.Product.is_active == True).scalar() or 0
    
    # Low stock products (stock <= low_stock_threshold)
    low_stock_count = db.query(models.Product).filter(
        and_(
            models.Product.is_active == True,
            models.Product.stock_quantity <= models.Product.low_stock_threshold
        )
    ).count()
    
    # Out of stock products
    out_of_stock_count = db.query(models.Product).filter(
        and_(
            models.Product.is_active == True,
            models.Product.stock_quantity == 0
        )
    ).count()
    
    # Products by category
    category_stats = db.query(
        models.Category.name,
        func.count(models.Product.id).label('product_count'),
        func.sum(models.Product.stock_quantity).label('total_stock')
    ).join(
        models.Product, models.Product.category_id == models.Category.id
    ).filter(
        models.Product.is_active == True
    ).group_by(models.Category.name).all()
    
    categories = [
        {
            "name": stat.name,
            "product_count": stat.product_count,
            "total_stock": stat.total_stock or 0
        }
        for stat in category_stats
    ]
    
    return {
        "total_products": total_products,
        "total_stock_value": total_stock_value,
        "total_stock_quantity": total_stock_quantity,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "categories": categories,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/low-stock", response_model=List[schemas.Product])
def get_low_stock_products(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get products with low stock (stock <= low_stock_threshold)."""
    
    products = db.query(models.Product).filter(
        and_(
            models.Product.is_active == True,
            models.Product.stock_quantity <= models.Product.low_stock_threshold
        )
    ).order_by(
        models.Product.stock_quantity.asc()
    ).offset(skip).limit(limit).all()
    
    return products


@router.get("/out-of-stock", response_model=List[schemas.Product])
def get_out_of_stock_products(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get products that are out of stock."""
    
    products = db.query(models.Product).filter(
        and_(
            models.Product.is_active == True,
            models.Product.stock_quantity == 0
        )
    ).order_by(models.Product.name).offset(skip).limit(limit).all()
    
    return products


@router.get("/stock-movements", response_model=List[schemas.InventoryLedger])
def get_recent_stock_movements(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
    days: int = 7,
    skip: int = 0,
    limit: int = 50
) -> Any:
    """Get recent stock movements within specified days."""
    
    since_date = datetime.now() - timedelta(days=days)
    
    movements = db.query(models.inventory_ledger.InventoryLedger).filter(
        models.inventory_ledger.InventoryLedger.created_at >= since_date
    ).order_by(
        models.inventory_ledger.InventoryLedger.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return movements


@router.get("/stock-levels", response_model=Dict[str, Any])
def get_stock_levels_distribution(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """Get distribution of stock levels across products."""
    
    # Stock level ranges
    ranges = [
        {"name": "Out of Stock", "min": 0, "max": 0},
        {"name": "Critical (1-5)", "min": 1, "max": 5},
        {"name": "Low (6-20)", "min": 6, "max": 20},
        {"name": "Medium (21-50)", "min": 21, "max": 50},
        {"name": "High (51-100)", "min": 51, "max": 100},
        {"name": "Very High (100+)", "min": 101, "max": 999999}
    ]
    
    distribution = []
    
    for range_info in ranges:
        if range_info["max"] == 999999:
            # Handle "Very High" range
            count = db.query(models.Product).filter(
                and_(
                    models.Product.is_active == True,
                    models.Product.stock_quantity >= range_info["min"]
                )
            ).count()
        else:
            count = db.query(models.Product).filter(
                and_(
                    models.Product.is_active == True,
                    models.Product.stock_quantity >= range_info["min"],
                    models.Product.stock_quantity <= range_info["max"]
                )
            ).count()
        
        distribution.append({
            "range": range_info["name"],
            "count": count
        })
    
    return {
        "distribution": distribution,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/top-products", response_model=List[Dict[str, Any]])
def get_top_products_by_value(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_admin_user),
    limit: int = 10
) -> Any:
    """Get top products by stock value (price * quantity)."""
    
    products = db.query(
        models.Product.id,
        models.Product.name,
        models.Product.price,
        models.Product.stock_quantity,
        (models.Product.price * models.Product.stock_quantity).label('stock_value')
    ).filter(
        models.Product.is_active == True
    ).order_by(
        (models.Product.price * models.Product.stock_quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock_quantity": product.stock_quantity,
            "stock_value": float(product.stock_value)
        }
        for product in products
    ]
