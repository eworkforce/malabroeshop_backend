from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, product, order, categories, units_of_measure, inventory_reports, ai_tools, notification

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(product.router, prefix="/products", tags=["products"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(units_of_measure.router, prefix="/units-of-measure", tags=["units-of-measure"])
api_router.include_router(inventory_reports.router, prefix="/inventory-reports", tags=["inventory-reports"])
api_router.include_router(ai_tools.router, tags=["ai-tools"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
