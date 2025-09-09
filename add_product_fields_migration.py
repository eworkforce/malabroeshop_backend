#!/usr/bin/env python3
"""
Migration script to add missing fields to Product table:
- category (VARCHAR, nullable)
- stock_quantity (INTEGER, default 0)
- is_active (BOOLEAN, default 1)
"""

import sqlite3
import sys
import os

def run_migration():
    db_path = 'malabro_eshop.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current Product table schema...")
        cursor.execute('PRAGMA table_info(products)')
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        print(f"Current columns: {existing_columns}")
        
        # Add category column if it doesn't exist
        if 'category' not in existing_columns:
            print("➕ Adding 'category' column...")
            cursor.execute('ALTER TABLE products ADD COLUMN category VARCHAR')
            print("✅ Added 'category' column")
        else:
            print("ℹ️ 'category' column already exists")
        
        # Add stock_quantity column if it doesn't exist
        if 'stock_quantity' not in existing_columns:
            print("➕ Adding 'stock_quantity' column...")
            cursor.execute('ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 0')
            print("✅ Added 'stock_quantity' column")
        else:
            print("ℹ️ 'stock_quantity' column already exists")
        
        # Add is_active column if it doesn't exist
        if 'is_active' not in existing_columns:
            print("➕ Adding 'is_active' column...")
            cursor.execute('ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1')
            print("✅ Added 'is_active' column")
        else:
            print("ℹ️ 'is_active' column already exists")
        
        # Update existing products to have default values
        print("🔄 Updating existing products with default values...")
        cursor.execute('''
            UPDATE products 
            SET stock_quantity = COALESCE(stock_quantity, 0),
                is_active = COALESCE(is_active, 1)
            WHERE stock_quantity IS NULL OR is_active IS NULL
        ''')
        
        conn.commit()
        
        # Verify the changes
        print("\n🔍 Verifying updated schema...")
        cursor.execute('PRAGMA table_info(products)')
        columns = cursor.fetchall()
        print("Updated Product table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - Default: {col[4]} - NotNull: {col[3]}")
        
        conn.close()
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
