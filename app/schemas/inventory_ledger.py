from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared properties
class InventoryLedgerBase(BaseModel):
    product_id: int
    change_type: str
    quantity_change: int
    new_quantity: int
    user_id: Optional[int] = None
    order_id: Optional[int] = None
    notes: Optional[str] = None

# Properties to receive on item creation
class InventoryLedgerCreate(InventoryLedgerBase):
    pass

# Properties shared by models stored in DB
class InventoryLedgerInDBBase(InventoryLedgerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class InventoryLedger(InventoryLedgerInDBBase):
    pass
