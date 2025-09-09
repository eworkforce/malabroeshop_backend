from pydantic import BaseModel
from typing import Optional

class UnitOfMeasureBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None

class UnitOfMeasureCreate(UnitOfMeasureBase):
    pass

class UnitOfMeasureUpdate(UnitOfMeasureBase):
    pass

class UnitOfMeasure(UnitOfMeasureBase):
    id: int

    class Config:
        from_attributes = True
