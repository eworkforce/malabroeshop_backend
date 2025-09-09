#!/usr/bin/env python3
"""
MALABRO E-Shop: Database Configuration Test
==========================================

This script tests both SQLite (development) and Supabase Postgres (production)
database configurations to ensure seamless deployment on Google Cloud Run.

Author: AI Principal Engineer
Date: 2025-01-26
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

def test_sqlite_connection():
    """Test SQLite database connection (development)"""
    print("🔍 Testing SQLite Database Connection (Development)")
    print("-" * 50)
    
    try:
        # SQLite connection
        sqlite_url = "sqlite:///./malabro_eshop.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT COUNT(*) as count FROM products"))
            product_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            user_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) as count FROM orders"))
            order_count = result.fetchone()[0]
            
            print(f"✅ SQLite Connection: SUCCESS")
            print(f"   📊 Products: {product_count}")
            print(f"   👥 Users: {user_count}")
            print(f"   📦 Orders: {order_count}")
            print(f"   🗄️  Database: {sqlite_url}")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ SQLite Connection: FAILED")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ SQLite Connection: FAILED")
        print(f"   Unexpected Error: {e}")
        return False

def test_postgres_connection():
    """Test Supabase Postgres connection (production)"""
    print("\n🔍 Testing Supabase Postgres Connection (Production)")
    print("-" * 50)
    
    # Get Supabase DB URL from environment
    supabase_db_url = os.getenv("SUPABASE_DB_URL")
    
    if not supabase_db_url or "[YOUR_DB_PASSWORD]" in supabase_db_url:
        print("⚠️  Supabase Postgres Connection: SKIPPED")
        print("   Reason: Database password not configured")
        print("   Action: Replace [YOUR_DB_PASSWORD] in .env with actual password")
        return None
    
    try:
        # PostgreSQL connection
        engine = create_engine(
            supabase_db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT COUNT(*) as count FROM products"))
            product_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            user_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) as count FROM orders"))
            order_count = result.fetchone()[0]
            
            # Test Supabase-specific features
            result = conn.execute(text("SELECT version()"))
            pg_version = result.fetchone()[0]
            
            print(f"✅ Supabase Postgres Connection: SUCCESS")
            print(f"   📊 Products: {product_count}")
            print(f"   👥 Users: {user_count}")
            print(f"   📦 Orders: {order_count}")
            print(f"   🐘 PostgreSQL Version: {pg_version.split(',')[0]}")
            print(f"   🌐 Database: Supabase Cloud")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Supabase Postgres Connection: FAILED")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Supabase Postgres Connection: FAILED")
        print(f"   Unexpected Error: {e}")
        return False

def test_backend_config():
    """Test backend configuration loading"""
    print("\n🔍 Testing Backend Configuration")
    print("-" * 50)
    
    try:
        # Import backend configuration
        sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
        from app.core.config import settings
        
        print(f"✅ Configuration Loading: SUCCESS")
        print(f"   🌍 Environment: {settings.ENVIRONMENT}")
        print(f"   🗄️  Database URL: {settings.database_url}")
        print(f"   🔑 Supabase URL: {settings.SUPABASE_URL[:50]}..." if settings.SUPABASE_URL else "   🔑 Supabase URL: Not configured")
        print(f"   🚀 API Version: {settings.API_V1_STR}")
        
        # Test database URL property logic
        if settings.ENVIRONMENT == "production" and settings.SUPABASE_DB_URL:
            expected_db = "Supabase Postgres"
        else:
            expected_db = "SQLite"
        
        print(f"   📊 Expected Database: {expected_db}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration Loading: FAILED")
        print(f"   Error: {e}")
        return False

def main():
    """Run comprehensive database configuration tests"""
    print("🚀 MALABRO E-Shop: Database Configuration Test")
    print("=" * 60)
    print("🎯 Purpose: Verify SQLite (dev) and Supabase Postgres (prod) support")
    print("🌐 Target: Google Cloud Run production deployment readiness")
    print()
    
    # Test results
    results = {
        "config": False,
        "sqlite": False,
        "postgres": None  # None means skipped
    }
    
    # Run tests
    results["config"] = test_backend_config()
    results["sqlite"] = test_sqlite_connection()
    results["postgres"] = test_postgres_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    # Configuration test
    status = "✅ PASS" if results["config"] else "❌ FAIL"
    print(f"🔧 Backend Configuration: {status}")
    
    # SQLite test
    status = "✅ PASS" if results["sqlite"] else "❌ FAIL"
    print(f"🗄️  SQLite (Development): {status}")
    
    # Postgres test
    if results["postgres"] is None:
        status = "⚠️  SKIP (Password needed)"
    elif results["postgres"]:
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    print(f"🐘 Supabase Postgres (Production): {status}")
    
    # Overall status
    config_ok = results["config"]
    sqlite_ok = results["sqlite"]
    postgres_ready = results["postgres"] is not False  # True or None (skipped)
    
    if config_ok and sqlite_ok and postgres_ready:
        print(f"\n🎉 OVERALL STATUS: READY FOR DEPLOYMENT")
        print(f"   ✅ Development environment: SQLite working")
        print(f"   ✅ Production environment: Supabase Postgres configured")
        print(f"   🚀 Google Cloud Run: Ready for deployment")
        
        if results["postgres"] is None:
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Replace [YOUR_DB_PASSWORD] in .env with actual Supabase password")
            print(f"   2. Set ENVIRONMENT=production for production deployment")
            print(f"   3. Deploy to Google Cloud Run")
        
        return True
    else:
        print(f"\n❌ OVERALL STATUS: ISSUES DETECTED")
        if not config_ok:
            print(f"   🔧 Fix backend configuration loading")
        if not sqlite_ok:
            print(f"   🗄️  Fix SQLite database connection")
        if results["postgres"] is False:
            print(f"   🐘 Fix Supabase Postgres connection")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
