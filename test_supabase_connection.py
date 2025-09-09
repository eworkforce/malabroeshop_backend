#!/usr/bin/env python3
"""
Test Supabase Storage connection and upload functionality
"""

import os
from dotenv import load_dotenv
from app.core.supabase import supabase_storage

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    print("🔍 Testing Supabase Storage connection...")
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    # Test bucket access
    try:
        print("\n🪣 Testing bucket access...")
        client = supabase_storage.client
        
        # List buckets to test connection
        buckets = client.storage.list_buckets()
        print(f"✅ Successfully connected to Supabase!")
        print(f"Available buckets: {[bucket.name for bucket in buckets]}")
        
        # Check if product-images bucket exists
        bucket_names = [bucket.name for bucket in buckets]
        if 'product-images' in bucket_names:
            print("✅ 'product-images' bucket found!")
        else:
            print("❌ 'product-images' bucket not found!")
            return False
        
        # Test a simple upload
        print("\n📤 Testing image upload...")
        test_content = b"test image content"
        test_url = await supabase_storage.upload_image(test_content, ".jpg")
        
        if test_url.startswith("https://"):
            print(f"✅ Upload successful! URL: {test_url}")
            return True
        else:
            print(f"❌ Upload failed, using local fallback: {test_url}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_supabase_connection())
    print(f"\n🎯 Test result: {'✅ PASSED' if success else '❌ FAILED'}")
