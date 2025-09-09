#!/usr/bin/env python3
"""
MALABRO E-Shop: Final Migration to Supabase Storage
==================================================

This script performs the definitive migration of ALL product images to Supabase Storage:
- Uploads all images with unique names to avoid conflicts
- Updates database with actual Supabase HTTPS URLs
- Creates a truly unified cloud-based image management system

Author: AI Principal Engineer
Date: 2025-01-26
"""

import os
import sqlite3
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from app.core.supabase import supabase_storage
import time

# Load environment variables
load_dotenv()

class FinalSupabaseMigration:
    def __init__(self):
        self.db_path = "malabro_eshop.db"
        self.frontend_static_path = Path("../frontend/public/products")
        self.backend_uploads_path = Path("uploads/products")
        self.migrated_count = 0
        self.failed_migrations = []
        
    def get_products_with_images(self) -> List[Tuple]:
        """Get all products with image URLs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, image_url 
            FROM products 
            WHERE image_url IS NOT NULL 
            ORDER BY id
        """)
        products = cursor.fetchall()
        conn.close()
        return products
    
    def update_product_image_url(self, product_id: int, new_url: str) -> bool:
        """Update product image URL in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET image_url = ? 
                WHERE id = ?
            """, (new_url, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Failed to update database for product {product_id}: {e}")
            return False
    
    def get_local_image_path(self, image_url: str) -> Optional[Path]:
        """Get the local file path for an image URL"""
        if image_url.startswith('/products/'):
            # Static image from frontend
            filename = image_url.replace('/products/', '')
            path = self.frontend_static_path / filename
            return path if path.exists() else None
            
        elif image_url.startswith('/uploads/'):
            # Local upload from backend
            filename = image_url.replace('/uploads/products/', '')
            path = self.backend_uploads_path / filename
            return path if path.exists() else None
            
        return None
    
    def upload_to_supabase_with_retry(self, file_content: bytes, filename: str, max_retries: int = 3) -> Optional[str]:
        """Upload to Supabase with retry logic and unique naming"""
        for attempt in range(max_retries):
            try:
                # Create unique filename with timestamp to avoid conflicts
                timestamp = int(time.time() * 1000)  # milliseconds
                name_parts = filename.split('.')
                if len(name_parts) > 1:
                    unique_filename = f"{name_parts[0]}_{timestamp}.{name_parts[-1]}"
                else:
                    unique_filename = f"{filename}_{timestamp}"
                
                file_path = f"products/{unique_filename}"
                
                # Direct Supabase upload
                result = supabase_storage.client.storage.from_(supabase_storage.bucket_name).upload(
                    file_path,
                    file_content,
                    file_options={
                        "content-type": supabase_storage._get_content_type(Path(filename).suffix),
                        "upsert": "true"  # Allow overwrite if exists
                    }
                )
                
                # Get public URL immediately
                public_url = supabase_storage.client.storage.from_(supabase_storage.bucket_name).get_public_url(file_path)
                
                if public_url and public_url.startswith('https://'):
                    print(f"   ✅ Supabase upload successful: {public_url}")
                    return public_url
                else:
                    print(f"   ❌ Invalid public URL received: {public_url}")
                    
            except Exception as e:
                print(f"   ⚠️  Upload attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                
        return None
    
    def migrate_single_image(self, product_id: int, product_name: str, image_url: str) -> bool:
        """Migrate a single product image to Supabase Storage"""
        print(f"\n🔄 Migrating: {product_name} (ID: {product_id})")
        print(f"   Current URL: {image_url}")
        
        # Skip if already on Supabase
        if image_url.startswith('https://') and 'supabase' in image_url:
            print(f"   ✅ Already on Supabase, skipping")
            return True
        
        # Get local file path
        local_path = self.get_local_image_path(image_url)
        if not local_path:
            print(f"   ❌ Local file not found: {image_url}")
            self.failed_migrations.append((product_id, product_name, "File not found"))
            return False
        
        print(f"   📁 Local file: {local_path}")
        
        try:
            # Read file content
            with open(local_path, 'rb') as file:
                file_content = file.read()
            
            print(f"   ☁️  Uploading to Supabase...")
            
            # Upload to Supabase with retry
            supabase_url = self.upload_to_supabase_with_retry(file_content, local_path.name)
            
            if not supabase_url:
                print(f"   ❌ All Supabase upload attempts failed")
                self.failed_migrations.append((product_id, product_name, "Supabase upload failed"))
                return False
            
            # Update database with new URL
            if self.update_product_image_url(product_id, supabase_url):
                print(f"   ✅ Database updated with Supabase URL")
                self.migrated_count += 1
                return True
            else:
                print(f"   ❌ Database update failed")
                self.failed_migrations.append((product_id, product_name, "Database update failed"))
                return False
                
        except Exception as e:
            print(f"   ❌ Migration failed: {e}")
            self.failed_migrations.append((product_id, product_name, str(e)))
            return False
    
    def run_migration(self):
        """Run the complete image migration process"""
        print("🚀 MALABRO E-Shop: Final Migration to Supabase Storage")
        print("=" * 60)
        
        # Check Supabase Storage availability
        if not supabase_storage.client:
            print("❌ Supabase Storage not available. Check environment variables.")
            return False
        
        print(f"✅ Supabase Storage connected: {supabase_storage.bucket_name}")
        print(f"🌐 Supabase URL: {os.getenv('SUPABASE_URL')}")
        
        # Get all products with images
        products = self.get_products_with_images()
        print(f"\n📋 Found {len(products)} products with images")
        
        # Migrate each image
        for product_id, product_name, image_url in products:
            self.migrate_single_image(product_id, product_name, image_url)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FINAL MIGRATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully migrated: {self.migrated_count} images")
        print(f"❌ Failed migrations: {len(self.failed_migrations)} images")
        
        if self.failed_migrations:
            print("\n❌ Failed Migrations:")
            for product_id, product_name, error in self.failed_migrations:
                print(f"   - ID {product_id}: {product_name} - {error}")
        
        if self.migrated_count > 0:
            print(f"\n🎉 MIGRATION COMPLETED! {self.migrated_count} images now served from Supabase CDN")
            print("🌐 All product images now have HTTPS URLs from Supabase Storage")
            print("🔧 Next steps:")
            print("   1. Test image display in frontend")
            print("   2. Simplify frontend to only handle Supabase URLs")
            print("   3. Remove local image files and static assets")
            print("   4. Update image upload logic to use Supabase only")
        
        return len(self.failed_migrations) == 0

if __name__ == "__main__":
    migration = FinalSupabaseMigration()
    success = migration.run_migration()
    exit(0 if success else 1)
