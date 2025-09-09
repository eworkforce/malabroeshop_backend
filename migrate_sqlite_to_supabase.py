#!/usr/bin/env python3
"""
MALABRO E-Shop: SQLite to Supabase Postgres Migration
====================================================

This script migrates all data from local SQLite database to Supabase Postgres
for production deployment on Google Cloud Run.

Critical for production: Google Cloud Run requires cloud database, not local files.

Author: AI Principal Engineer
Date: 2025-01-26
"""

import sqlite3
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseMigration:
    def __init__(self):
        self.sqlite_db = "malabro_eshop.db"
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise Exception("Supabase credentials not found in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        self.migrated_counts = {}
        self.failed_migrations = []
    
    def get_sqlite_data(self, table_name: str):
        """Get all data from SQLite table"""
        conn = sqlite3.connect(self.sqlite_db)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(dict(row))
        
        conn.close()
        return data
    
    def migrate_products(self):
        """Migrate products table"""
        print("🛍️ Migrating products...")
        
        sqlite_products = self.get_sqlite_data("products")
        print(f"   📊 Found {len(sqlite_products)} products in SQLite")
        
        migrated = 0
        for product in sqlite_products:
            try:
                # Prepare product data for Supabase
                supabase_product = {
                    "name": product["name"],
                    "description": product["description"],
                    "price": product["price"],
                    "image_url": product["image_url"],
                    "category": product["category"],
                    "stock_quantity": product["stock_quantity"] or 0,
                    "is_active": bool(product["is_active"])
                }
                
                # Insert into Supabase
                result = self.supabase.table("products").insert(supabase_product).execute()
                
                if result.data:
                    migrated += 1
                    print(f"   ✅ Migrated: {product['name']}")
                else:
                    print(f"   ❌ Failed: {product['name']}")
                    self.failed_migrations.append(("products", product["name"], "No data returned"))
                    
            except Exception as e:
                print(f"   ❌ Error migrating {product['name']}: {e}")
                self.failed_migrations.append(("products", product["name"], str(e)))
        
        self.migrated_counts["products"] = migrated
        print(f"   🎉 Successfully migrated {migrated}/{len(sqlite_products)} products\n")
    
    def migrate_users(self):
        """Migrate users table"""
        print("👥 Migrating users...")
        
        sqlite_users = self.get_sqlite_data("users")
        print(f"   📊 Found {len(sqlite_users)} users in SQLite")
        
        migrated = 0
        for user in sqlite_users:
            try:
                # Prepare user data for Supabase
                supabase_user = {
                    "email": user["email"],
                    "hashed_password": user["hashed_password"],
                    "full_name": user["full_name"],
                    "is_active": bool(user["is_active"]),
                    "is_admin": bool(user["is_admin"])
                }
                
                # Insert into Supabase
                result = self.supabase.table("users").insert(supabase_user).execute()
                
                if result.data:
                    migrated += 1
                    admin_marker = " (ADMIN)" if user["is_admin"] else ""
                    print(f"   ✅ Migrated: {user['email']}{admin_marker}")
                else:
                    print(f"   ❌ Failed: {user['email']}")
                    self.failed_migrations.append(("users", user["email"], "No data returned"))
                    
            except Exception as e:
                print(f"   ❌ Error migrating {user['email']}: {e}")
                self.failed_migrations.append(("users", user["email"], str(e)))
        
        self.migrated_counts["users"] = migrated
        print(f"   🎉 Successfully migrated {migrated}/{len(sqlite_users)} users\n")
    
    def migrate_orders(self):
        """Migrate orders table"""
        print("📦 Migrating orders...")
        
        sqlite_orders = self.get_sqlite_data("orders")
        print(f"   📊 Found {len(sqlite_orders)} orders in SQLite")
        
        migrated = 0
        for order in sqlite_orders:
            try:
                # Prepare order data for Supabase
                supabase_order = {
                    "user_id": order["user_id"],
                    "order_reference": order["order_reference"],
                    "total_amount": order["total_amount"],
                    "status": order["status"] or "pending",
                    "payment_method": order["payment_method"],
                    "customer_name": order["customer_name"],
                    "customer_email": order["customer_email"],
                    "customer_phone": order["customer_phone"],
                    "shipping_address": order["shipping_address"],
                    "shipping_city": order["shipping_city"],
                    "shipping_country": order["shipping_country"] or "Sénégal",
                    "billing_address": order["billing_address"],
                    "billing_city": order["billing_city"],
                    "billing_country": order["billing_country"],
                    "payment_confirmed_at": order["payment_confirmed_at"],
                    "payment_notes": order["payment_notes"]
                }
                
                # Insert into Supabase
                result = self.supabase.table("orders").insert(supabase_order).execute()
                
                if result.data:
                    migrated += 1
                    print(f"   ✅ Migrated: {order['order_reference']} ({order['customer_name']})")
                else:
                    print(f"   ❌ Failed: {order['order_reference']}")
                    self.failed_migrations.append(("orders", order["order_reference"], "No data returned"))
                    
            except Exception as e:
                print(f"   ❌ Error migrating {order['order_reference']}: {e}")
                self.failed_migrations.append(("orders", order["order_reference"], str(e)))
        
        self.migrated_counts["orders"] = migrated
        print(f"   🎉 Successfully migrated {migrated}/{len(sqlite_orders)} orders\n")
    
    def migrate_order_items(self):
        """Migrate order_items table"""
        print("📋 Migrating order items...")
        
        sqlite_items = self.get_sqlite_data("order_items")
        print(f"   📊 Found {len(sqlite_items)} order items in SQLite")
        
        migrated = 0
        for item in sqlite_items:
            try:
                # Prepare order item data for Supabase
                supabase_item = {
                    "order_id": item["order_id"],
                    "product_id": item["product_id"],
                    "product_name": item["product_name"],
                    "product_price": item["product_price"],
                    "quantity": item["quantity"],
                    "subtotal": item["subtotal"]
                }
                
                # Insert into Supabase
                result = self.supabase.table("order_items").insert(supabase_item).execute()
                
                if result.data:
                    migrated += 1
                    print(f"   ✅ Migrated: {item['product_name']} (Qty: {item['quantity']})")
                else:
                    print(f"   ❌ Failed: {item['product_name']}")
                    self.failed_migrations.append(("order_items", item["product_name"], "No data returned"))
                    
            except Exception as e:
                print(f"   ❌ Error migrating {item['product_name']}: {e}")
                self.failed_migrations.append(("order_items", item["product_name"], str(e)))
        
        self.migrated_counts["order_items"] = migrated
        print(f"   🎉 Successfully migrated {migrated}/{len(sqlite_items)} order items\n")
    
    def run_migration(self):
        """Run the complete database migration"""
        print("🚀 MALABRO E-Shop: SQLite to Supabase Postgres Migration")
        print("=" * 60)
        print("🎯 Purpose: Prepare for Google Cloud Run production deployment")
        print("📊 Source: Local SQLite database")
        print("🌐 Target: Supabase Postgres (Cloud)")
        print()
        
        # Check SQLite database exists
        if not os.path.exists(self.sqlite_db):
            print(f"❌ SQLite database not found: {self.sqlite_db}")
            return False
        
        # Check Supabase connection
        try:
            # Test connection by trying to access a table with simple select
            result = self.supabase.table("products").select("id").limit(1).execute()
            print("✅ Supabase connection successful")
            print(f"📊 Found {len(result.data)} existing products in Supabase")
            print()
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            print("💡 This might be because the tables don't exist yet or need different permissions")
            return False
        
        # Run migrations in order (respecting foreign key constraints)
        self.migrate_products()
        self.migrate_users()
        self.migrate_orders()
        self.migrate_order_items()
        
        # Print summary
        print("=" * 60)
        print("📊 MIGRATION SUMMARY")
        print("=" * 60)
        
        total_migrated = sum(self.migrated_counts.values())
        print(f"✅ Total records migrated: {total_migrated}")
        
        for table, count in self.migrated_counts.items():
            print(f"   📋 {table}: {count} records")
        
        if self.failed_migrations:
            print(f"\n❌ Failed migrations: {len(self.failed_migrations)}")
            for table, item, error in self.failed_migrations:
                print(f"   - {table}.{item}: {error}")
        else:
            print("\n🎉 ALL MIGRATIONS SUCCESSFUL!")
        
        print(f"\n🌐 Database is now ready for Google Cloud Run deployment!")
        print(f"🔄 Next step: Update backend to use Supabase Postgres instead of SQLite")
        
        return len(self.failed_migrations) == 0

if __name__ == "__main__":
    migration = DatabaseMigration()
    success = migration.run_migration()
    exit(0 if success else 1)
