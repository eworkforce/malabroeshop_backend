from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.v1.endpoints import auth as deps
from app.db.session import get_db
from app.utils.file_upload import (
    save_upload_file, 
    generate_unique_filename, 
    get_product_image_path
)

router = APIRouter()


@router.get("/", response_model=List[schemas.Product])
def read_products(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve products."""
    products = crud.product.get_multi(db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    low_stock_threshold: int = Form(10),
    category_id: int = Form(...),
    unit_of_measure_id: int = Form(...),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
) -> Any:
    """Create new product."""
    image_url = None
    if image:
        unique_filename = generate_unique_filename(image.filename)
        destination = get_product_image_path(unique_filename)
        save_upload_file(image, destination)
        image_url = f"/uploads/products/{unique_filename}"

    product_in = schemas.ProductCreate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        low_stock_threshold=low_stock_threshold,
        category_id=category_id,
        unit_of_measure_id=unit_of_measure_id,
        is_active=is_active,
        image_url=image_url,
    )
    product = crud.product.create(db=db, obj_in=product_in)

    if product.stock_quantity > 0:
        ledger_in = schemas.InventoryLedgerCreate(
            product_id=product.id,
            change_type="Initial Stock",
            quantity_change=product.stock_quantity,
            new_quantity=product.stock_quantity,
            user_id=current_user.id,
            notes="Initial stock for new product",
        )
        crud.inventory_ledger.create(db=db, obj_in=ledger_in)

    return product


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(*, db: Session = Depends(get_db), product_id: int) -> Any:
    """Get product by ID."""
    product = crud.product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    low_stock_threshold: int = Form(10),
    category_id: int = Form(...),
    unit_of_measure_id: int = Form(...),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    notes: Optional[str] = Form(None),
) -> Any:
    """Update a product."""
    product = crud.product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    old_stock_quantity = product.stock_quantity

    image_url = product.image_url
    if image:
        unique_filename = generate_unique_filename(image.filename)
        destination = get_product_image_path(unique_filename)
        save_upload_file(image, destination)
        image_url = f"/uploads/products/{unique_filename}"

    product_in = schemas.ProductUpdate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        low_stock_threshold=low_stock_threshold,
        category_id=category_id,
        unit_of_measure_id=unit_of_measure_id,
        is_active=is_active,
        image_url=image_url,
    )
    product = crud.product.update(db=db, db_obj=product, obj_in=product_in)

    if old_stock_quantity != product.stock_quantity:
        ledger_in = schemas.InventoryLedgerCreate(
            product_id=product.id,
            change_type="Manual Adjustment",
            quantity_change=product.stock_quantity - old_stock_quantity,
            new_quantity=product.stock_quantity,
            user_id=current_user.id,
            notes=notes,
        )
        crud.inventory_ledger.create(db=db, obj_in=ledger_in)

    return product


from sqlalchemy.orm import joinedload

# ... (other imports)

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(*, db: Session = Depends(get_db), product_id: int) -> Any:
    """
    Delete a product after eagerly loading its relationships to prevent DetachedInstanceError.
    """
    # Eagerly load relationships to prevent DetachedInstanceError during serialization
    product = (
        db.query(models.Product)
        .options(
            joinedload(models.Product.category),
            joinedload(models.Product.unit_of_measure),
        )
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Now, perform the deletion
    db.delete(product)
    db.commit()

    return product


@router.get("/{product_id}/ledger", response_model=List[schemas.InventoryLedger])
def read_product_ledger(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """Get inventory ledger for a specific product."""
    ledger_entries = crud.inventory_ledger.get_for_product(db=db, product_id=product_id)
    return ledger_entries
