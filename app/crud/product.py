from sqlalchemy.orm import Session, joinedload
from typing import Any

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def remove(self, db: Session, *, id: int) -> Product:
        """
        Delete a product after eagerly loading its relationships.
        This prevents DetachedInstanceError when the deleted object is returned.
        """
        # Eagerly load relationships to avoid DetachedInstanceError
        obj = (
            db.query(self.model)
            .options(
                joinedload(self.model.category),
                joinedload(self.model.unit_of_measure),
            )
            .get(id)
        )
        
        if obj:
            db.delete(obj)
            db.commit()
            
        return obj

product = CRUDProduct(Product)