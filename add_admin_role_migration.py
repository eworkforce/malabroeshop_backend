#!/usr/bin/env python3
"""
Database migration to add admin role support to users table
"""

from sqlalchemy import create_engine, text

def add_admin_role_to_users():
    """Add is_admin column to users table"""
    
    # Create database connection
    engine = create_engine('sqlite:///./malabro_eshop.db')
    
    with engine.connect() as conn:
        try:
            # Add is_admin column to users table
            conn.execute(text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
            print("✅ Added is_admin column to users table")
            
            # Create an admin user for testing (you can change these credentials)
            admin_email = "admin@malabro.com"
            admin_password_hash = "$2b$12$LQv3c1yqBwEHxPuNY7lmu.Hc8GwHuubHiaaGrAh8/dOtd9S1.9K5W"  # "admin123"
            
            # Check if admin user already exists
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": admin_email})
            existing_admin = result.fetchone()
            
            if not existing_admin:
                # Create admin user
                conn.execute(text("""
                    INSERT INTO users (email, hashed_password, full_name, is_active, is_admin, created_at)
                    VALUES (:email, :password, :name, :active, :admin, datetime('now'))
                """), {
                    "email": admin_email,
                    "password": admin_password_hash,
                    "name": "MALABRO Administrator",
                    "active": True,
                    "admin": True
                })
                print(f"✅ Created admin user: {admin_email} (password: admin123)")
            else:
                # Update existing user to be admin
                conn.execute(text("UPDATE users SET is_admin = TRUE WHERE email = :email"), {"email": admin_email})
                print(f"✅ Updated existing user {admin_email} to admin")
            
            conn.commit()
            print("✅ Admin role migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_admin_role_to_users()
