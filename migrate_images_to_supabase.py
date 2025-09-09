#!/usr/bin/env python3
"""
MALABRO E-Shop: Comprehensive Image Migration to Supabase Storage
================================================================

This script migrates ALL product images to Supabase Storage:
- Static images from /frontend/public/products/
- Local uploads from /backend/uploads/products/
- Updates database with new Supabase URLs
- Creates a unified image management system

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

# Load environment variables
load_dotenv()

class ImageMigration:
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
    
    def migrate_single_image(self, product_id: int, product_name: str, image_url: str) -> bool:
        """Migrate a single product image to Supabase Storage"""
        print(f"\n🔄 Migrating: {product_name} (ID: {product_id})")
        print(f"   Current URL: {image_url}")
        
        # Skip if already on Supabase
        if image_url.startswith('https://'):
            print(f"   ✅ Already on Supabase, skipping")
            return True
        
        # Get local file path
        local_path = self.get_local_image_path(image_url)
        if not local_path:
            print(f"   ❌ Local file not found: {image_url}")
            self.failed_migrations.append((product_id, product_name, "File not found"))
            return False
        
        print(f"   📁 Local file: {local_path}")
        
        # Generate unique filename for Supabase
        file_extension = local_path.suffix
        supabase_filename = f"products/{product_id}_{local_path.stem}{file_extension}"
        
        try:
            # Upload to Supabase Storage
            with open(local_path, 'rb') as file:
                file_content = file.read()
            
            print(f"   ☁️  Uploading to Supabase: {supabase_filename}")
            supabase_url = supabase_storage.upload_image_sync(file_content, supabase_filename)
            
            if not supabase_url:
                print(f"   ❌ Supabase upload failed")
                self.failed_migrations.append((product_id, product_name, "Supabase upload failed"))
                return False
            
            print(f"   ✅ Uploaded successfully: {supabase_url}")
            
            # Update database with new URL
            if self.update_product_image_url(product_id, supabase_url):
                print(f"   ✅ Database updated")
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
        print("🚀 MALABRO E-Shop: Image Migration to Supabase Storage")
        print("=" * 60)
        
        # Check Supabase Storage availability
        if not supabase_storage.client:
            print("❌ Supabase Storage not available. Check environment variables.")
            return False
        
        print(f"✅ Supabase Storage connected: {supabase_storage.bucket_name}")
        
        # Get all products with images
        products = self.get_products_with_images()
        print(f"\n📋 Found {len(products)} products with images")
        
        # Migrate each image
        for product_id, product_name, image_url in products:
            self.migrate_single_image(product_id, product_name, image_url)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 MIGRATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully migrated: {self.migrated_count} images")
        print(f"❌ Failed migrations: {len(self.failed_migrations)} images")
        
        if self.failed_migrations:
            print("\n❌ Failed Migrations:")
            for product_id, product_name, error in self.failed_migrations:
                print(f"   - ID {product_id}: {product_name} - {error}")
        
        if self.migrated_count > 0:
            print(f"\n🎉 Migration completed! {self.migrated_count} images now served from Supabase CDN")
            print("🔧 Next steps:")
            print("   1. Test image display in frontend")
            print("   2. Remove local image files (optional)")
            print("   3. Simplify frontend image URL handling")
        
        return len(self.failed_migrations) == 0

if __name__ == "__main__":
    migration = ImageMigration()
    success = migration.run_migration()
    exit(0 if success else 1)
