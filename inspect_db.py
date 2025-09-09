import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.product import Product

def inspect_database():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        print(f"Found {len(products)} products in database:")
        for product in products:
            print(f"- ID: {product.id}, Name: {product.name}, Image URL: {product.image_url}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_database()
