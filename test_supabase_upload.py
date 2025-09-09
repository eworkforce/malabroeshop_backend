#!/usr/bin/env python3
"""
Test Supabase Storage upload functionality directly
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

# Load environment variables
load_dotenv()

def test_supabase_upload():
    print("🧪 Testing Supabase Storage upload functionality...")
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    try:
        # Create client
        client: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Create test image content
        test_content = b"fake image content for testing"
        test_filename = f"test-{uuid.uuid4()}.jpg"
        file_path = f"products/{test_filename}"
        
        print(f"📤 Attempting to upload test file: {file_path}")
        
        # Try to upload to product-images bucket
        result = client.storage.from_('product-images').upload(
            file_path,
            test_content,
            file_options={'content-type': 'image/jpeg'}
        )
        
        print(f"📋 Upload result: {result}")
        print(f"📋 Result type: {type(result)}")
        
        # Check if upload was successful (no exception means success)
        print("✅ Upload successful!")
        
        # Try to get public URL
        public_url = client.storage.from_('product-images').get_public_url(file_path)
        print(f"🌐 Public URL generated: {public_url}")
        
        # Verify the URL format
        if public_url.startswith('https://') and 'supabase.co' in public_url:
            print("✅ Public URL format is correct!")
        else:
            print(f"⚠️ Unexpected URL format: {public_url}")
        
        # Clean up test file
        print("🧹 Cleaning up test file...")
        delete_result = client.storage.from_('product-images').remove([file_path])
        
        print(f"📋 Delete result: {delete_result}")
        print("✅ Test file cleanup attempted")
        
        print("\n🎉 Supabase Storage is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_upload()
    print(f"\n🎯 Test result: {'✅ SUCCESS' if success else '❌ FAILED'}")
