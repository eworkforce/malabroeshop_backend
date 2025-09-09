from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Category])
def read_categories(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
):
    """Retrieve categories."""
    categories = crud.category.get_multi(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=schemas.Category)
def create_category(
    *, db: Session = Depends(get_db), category_in: schemas.CategoryCreate
):
    """Create new category."""
    category = crud.category.create(db=db, obj_in=category_in)
    return category

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(*, db: Session = Depends(get_db), category_id: int):
    """Get category by ID."""
    db_category = crud.category.get(db=db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    *, db: Session = Depends(get_db), category_id: int, category_in: schemas.CategoryUpdate
):
    """Update a category."""
    db_category = crud.category.get(db=db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.category.update(db=db, db_obj=db_category, obj_in=category_in)
    return category

@router.delete("/{category_id}", response_model=schemas.Category)
def delete_category(*, db: Session = Depends(get_db), category_id: int):
    """Delete a category."""
    db_category = crud.category.get(db=db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.category.remove(db=db, id=category_id)
    return category
