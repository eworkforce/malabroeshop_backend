from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.UnitOfMeasure])
def read_units_of_measure(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
):
    """Retrieve units of measure."""
    units = crud.unit_of_measure.get_multi(db, skip=skip, limit=limit)
    return units

@router.post("/", response_model=schemas.UnitOfMeasure)
def create_unit_of_measure(
    *, db: Session = Depends(get_db), unit_in: schemas.UnitOfMeasureCreate
):
    """Create new unit of measure."""
    unit = crud.unit_of_measure.create(db=db, obj_in=unit_in)
    return unit

@router.get("/{unit_id}", response_model=schemas.UnitOfMeasure)
def read_unit_of_measure(*, db: Session = Depends(get_db), unit_id: int):
    """Get unit of measure by ID."""
    db_unit = crud.unit_of_measure.get(db=db, id=unit_id)
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    return db_unit

@router.put("/{unit_id}", response_model=schemas.UnitOfMeasure)
def update_unit_of_measure(
    *, db: Session = Depends(get_db), unit_id: int, unit_in: schemas.UnitOfMeasureUpdate
):
    """Update a unit of measure."""
    db_unit = crud.unit_of_measure.get(db=db, id=unit_id)
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    unit = crud.unit_of_measure.update(db=db, db_obj=db_unit, obj_in=unit_in)
    return unit

@router.delete("/{unit_id}", response_model=schemas.UnitOfMeasure)
def delete_unit_of_measure(*, db: Session = Depends(get_db), unit_id: int):
    """Delete a unit of measure."""
    db_unit = crud.unit_of_measure.get(db=db, id=unit_id)
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    unit = crud.unit_of_measure.remove(db=db, id=unit_id)
    return unit
