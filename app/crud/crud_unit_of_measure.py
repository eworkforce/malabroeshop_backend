from .base import CRUDBase
from app.models.unit_of_measure import UnitOfMeasure
from app.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate

class CRUDUnitOfMeasure(CRUDBase[UnitOfMeasure, UnitOfMeasureCreate, UnitOfMeasureUpdate]):
    pass

unit_of_measure = CRUDUnitOfMeasure(UnitOfMeasure)
