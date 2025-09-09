#!/usr/bin/env python3
"""
Debug Supabase Storage initialization issue
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_supabase():
    print("🔍 Debugging Supabase Storage initialization...")
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_ANON_KEY: {supabase_key[:20]}..." if supabase_key else "❌ Missing")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    # Test Supabase client creation
    try:
        print("\n📦 Importing Supabase...")
        from supabase import create_client, Client
        print("✅ Supabase import successful!")
        
        print("\n🔧 Creating Supabase client...")
        client: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Client created: {type(client)}")
        
        if client is None:
            print("❌ Client is None!")
            return False
        
        print("\n🪣 Testing storage access...")
        storage = client.storage
        print(f"✅ Storage object: {type(storage)}")
        
        print("\n📋 Listing buckets...")
        buckets = storage.list_buckets()
        print(f"✅ Buckets response: {type(buckets)}")
        print(f"Available buckets: {[bucket.name for bucket in buckets]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_supabase()
    print(f"\n🎯 Debug result: {'✅ SUCCESS' if success else '❌ FAILED'}")
