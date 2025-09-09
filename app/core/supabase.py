"""
Supabase Storage Configuration for MALABRO E-Shop
Handles product image uploads to Supabase Storage for production deployment
"""

import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

class SupabaseStorage:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.bucket_name = "product-images"
        if not self.supabase_url or not self.supabase_key:
            print("⚠️ Supabase credentials missing, using local storage fallback")
            self.client = None
            self.use_local_storage = True
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                self.use_local_storage = False
                print("✅ Supabase Storage client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                self.client = None
                self.use_local_storage = True

    def _ensure_bucket_exists(self):
        """Ensure the product-images bucket exists"""
        if not self.client:
            return
        try:
            self.client.storage.get_bucket(self.bucket_name)
        except Exception:
            try:
                self.client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": True}
                )
            except Exception as e:
                print(f"Warning: Could not create Supabase bucket: {e}")

    def upload_image_sync(self, file_content: bytes, filename: str) -> str:
        """
        Synchronous version of upload_image for migration scripts
        """
        if self.use_local_storage or not self.client:
            return self._upload_local(file_content, filename)
        try:
            file_path = f"products/{filename}"
            file_extension = Path(filename).suffix
            self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={"content-type": self._get_content_type(file_extension)}
            )
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return public_url
        except Exception as e:
            print(f"❌ Supabase upload failed: {e}")
            return self._upload_local(file_content, filename)

    async def upload_image(self, file_content: bytes, file_extension: str) -> str:
        """
        Upload image to Supabase Storage
        """
        if not self.client:
            raise HTTPException(
                status_code=503,
                detail="Supabase Storage is not available."
            )
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        try:
            file_path = f"products/{unique_filename}"
            self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={"content-type": self._get_content_type(file_extension)}
            )
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            if not public_url or not public_url.startswith('https://'):
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate valid Supabase public URL"
                )
            return public_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Supabase upload failed: {str(e)}"
            )

    def _upload_local(self, file_content: bytes, filename: str) -> str:
        """Fallback local storage upload"""
        upload_dir = Path("uploads/products")
        upload_dir.mkdir(parents=True, exist_ok=True)
        clean_filename = filename.replace('products/', '')
        file_path = upload_dir / clean_filename
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        return f"/uploads/products/{clean_filename}"

    def _get_content_type(self, file_extension: str) -> str:
        """Get MIME type for file extension"""
        extension_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }
        return extension_map.get(file_extension.lower(), "image/jpeg")

    def delete_image(self, image_url: str) -> bool:
        """Delete image from storage"""
        if self.use_local_storage or not self.client:
            return self._delete_local(image_url)
        try:
            if "supabase" in image_url:
                path_parts = image_url.split("/")
                file_path = "/".join(path_parts[-2:])
                self.client.storage.from_(self.bucket_name).remove([file_path])
                return True
            else:
                return self._delete_local(image_url)
        except Exception as e:
            print(f"Failed to delete image: {e}")
            return False

    def _delete_local(self, image_url: str) -> bool:
        """Delete local file"""
        try:
            if image_url.startswith("/uploads/"):
                file_path = Path(image_url[1:])
                if file_path.exists():
                    file_path.unlink()
                    return True
            return False
        except Exception:
            return False

# Global instance
supabase_storage = SupabaseStorage()
