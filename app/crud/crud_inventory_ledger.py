from typing import List
from sqlalchemy.orm import Session  # pylint: disable=no-name-in-module

from app.crud.base import CRUDBase
from app.models.inventory_ledger import InventoryLedger
from app.schemas.inventory_ledger import InventoryLedgerCreate

class CRUDInventoryLedger(CRUDBase[InventoryLedger, InventoryLedgerCreate, None]):
    def get_for_product(self, db: Session, *, product_id: int) -> List[InventoryLedger]:
        return (
            db.query(self.model)
            .filter(InventoryLedger.product_id == product_id)
            .order_by(InventoryLedger.created_at.desc())
            .all()
        )

inventory_ledger = CRUDInventoryLedger(InventoryLedger)
