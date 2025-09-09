from pydantic import BaseModel
from typing import Optional

from .category import Category
from .unit_of_measure import UnitOfMeasure

# Shared properties
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = 0
    low_stock_threshold: Optional[int] = 10
    is_active: Optional[bool] = True
    category_id: Optional[int] = None
    unit_of_measure_id: Optional[int] = None

# Properties to receive on item creation
class ProductCreate(ProductBase):
    name: str
    price: float

# Properties to receive on item update
class ProductUpdate(ProductBase):
    pass

# Properties shared by models stored in DB
class ProductInDBBase(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Product(ProductInDBBase):
    category: Optional[Category] = None
    unit_of_measure: Optional[UnitOfMeasure] = None

# Properties stored in DB
class ProductInDB(ProductInDBBase):
    pass
