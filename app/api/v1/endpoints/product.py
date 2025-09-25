import mimetypes
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

# Image validation constants
MAX_IMAGE_SIZE = 1024 * 1024  # 1MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

def validate_image_upload(file: Optional[UploadFile]) -> None:
    """
    Validate uploaded image file size and type.
    Raises HTTPException with clear error message if validation fails.
    """
    if not file:
        return  # No file uploaded, skip validation
    
    # Get file size by reading the file
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Reset file pointer for later use
    file.file.seek(0)
    
    # Validate file size
    if file_size > MAX_IMAGE_SIZE:
        size_mb = round(file_size / (1024 * 1024), 2)
        raise HTTPException(
            status_code=413,
            detail={
                "error": "IMAGE_TOO_LARGE",
                "message": f"Image size ({size_mb}MB) exceeds maximum allowed size of 1MB. Please compress your image or use a smaller image.",
                "max_size_mb": 1,
                "current_size_mb": size_mb,
                "suggestion": "Try using an image compression tool or resize the image to reduce file size.",
                "mobile_friendly": True
            }
        )
    
    # Validate file type
    if file.filename:
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=415,
                detail={
                    "error": "INVALID_IMAGE_TYPE",
                    "message": f"File type is not supported. Please use JPG, PNG, or WebP images.",
                    "allowed_types": ["JPG", "PNG", "WebP"],
                    "current_type": mime_type or "unknown",
                    "mobile_friendly": True
                }
            )


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
    """Create new product with image validation."""
    
    # Validate image before processing
    try:
        validate_image_upload(image)
    except HTTPException as e:
        # Add additional mobile-friendly context
        error_detail = e.detail
        if isinstance(error_detail, dict):
            error_detail["endpoint"] = "create_product"
            error_detail["help"] = "Please use a smaller image (under 1MB) or compress your image before uploading."
        raise HTTPException(status_code=e.status_code, detail=error_detail)
    
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
    return product


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
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
    """Update a product with image validation."""
    
    # Validate image before processing
    try:
        validate_image_upload(image)
    except HTTPException as e:
        # Add additional mobile-friendly context
        error_detail = e.detail
        if isinstance(error_detail, dict):
            error_detail["endpoint"] = "update_product"
            error_detail["help"] = "Please use a smaller image (under 1MB) or compress your image before uploading."
        raise HTTPException(status_code=e.status_code, detail=error_detail)
    
    product = crud.product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    image_url = product.image_url  # Keep existing image by default
    if image:
        unique_filename = generate_unique_filename(image.filename)
        destination = get_product_image_path(unique_filename)
        save_upload_file(image, destination)
        image_url = f"/uploads/products/{unique_filename}"

    product_update = schemas.ProductUpdate(
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
    product = crud.product.update(db=db, db_obj=product, obj_in=product_update)
    return product


@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a product after eagerly loading its relationships to prevent DetachedInstanceError.
    """
    # Eagerly load the product with its relationships to avoid DetachedInstanceError
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Force loading of relationships by accessing them
    _ = product.category
    _ = product.unit_of_measure
    
    product = crud.product.remove(db=db, id=product_id)
    return product


@router.get("/{product_id}/ledger", response_model=List[schemas.InventoryLedger])
def read_product_ledger(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get inventory ledger for a specific product."""
    product = crud.product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    ledger_entries = crud.inventory_ledger.get_by_product(db=db, product_id=product_id)
    return ledger_entries


@router.post("/validate-image")
async def validate_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Validate image size and type before actual upload.
    This endpoint can be used by frontend to check images before form submission.
    """
    try:
        validate_image_upload(file)
        
        # If validation passes, return success with file info
        file_size = len(file.file.read())
        file.file.seek(0)  # Reset file pointer
        
        return {
            "valid": True,
            "message": "Image is valid and ready for upload",
            "file_info": {
                "filename": file.filename,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "content_type": file.content_type
            }
        }
    except HTTPException as e:
        # Return validation errors in a user-friendly format
        return {
            "valid": False,
            "error": e.detail
        }
