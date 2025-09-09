import os
import shutil
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
PRODUCTS_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "products")

def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    """Saves an uploaded file to a destination."""
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

def get_product_image_path(filename: str) -> str:
    """Constructs the full path for a product image."""
    return os.path.join(PRODUCTS_UPLOAD_DIR, filename)

def generate_unique_filename(filename: str) -> str:
    """Generates a unique filename to prevent overwrites."""
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4()}.{ext}"
