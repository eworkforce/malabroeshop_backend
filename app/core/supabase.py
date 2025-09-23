"""
Mock Supabase Storage Configuration for MALABRO E-Shop
Disabled for SQLite-only deployment
"""

import os
import uuid
from pathlib import Path
from fastapi import HTTPException

class SupabaseStorage:
    def __init__(self):
        self.client = None  # Disabled
        self.bucket_name = "product-images"
        
    async def upload_image(self, file_content: bytes, file_extension: str) -> str:
        """Mock upload - returns local storage path"""
        filename = f"{uuid.uuid4()}.{file_extension}"
        local_path = f"/uploads/products/{filename}"
        
        # Save to local uploads directory
        upload_dir = Path("uploads/products")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        with open(upload_dir / filename, "wb") as f:
            f.write(file_content)
            
        return local_path

# Create instance
supabase_storage = SupabaseStorage()
