#!/usr/bin/env python3
"""
Create the product-images bucket in Supabase Storage with proper RLS policies
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def create_bucket():
    print("🔍 Creating Supabase Storage bucket...")
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    try:
        # Create client
        client: Client = create_client(supabase_url, supabase_key)
        
        # Check if bucket already exists
        buckets = client.storage.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]
        
        if 'product-images' in bucket_names:
            print("✅ 'product-images' bucket already exists!")
        else:
            print("📦 Creating 'product-images' bucket...")
            
            # Create bucket with public access
            result = client.storage.create_bucket(
                'product-images',
                options={
                    'public': True,
                    'allowedMimeTypes': ['image/jpeg', 'image/png', 'image/webp'],
                    'fileSizeLimit': 5242880  # 5MB
                }
            )
            
            if result.error:
                print(f"❌ Failed to create bucket: {result.error}")
                return False
            
            print("✅ Bucket created successfully!")
        
        # Test upload to verify bucket works
        print("\n🧪 Testing bucket with sample upload...")
        test_content = b"test image content"
        
        upload_result = client.storage.from_('product-images').upload(
            'test/sample.jpg',
            test_content,
            file_options={'content-type': 'image/jpeg'}
        )
        
        if upload_result.error:
            print(f"❌ Test upload failed: {upload_result.error}")
            return False
        
        # Get public URL
        public_url = client.storage.from_('product-images').get_public_url('test/sample.jpg')
        print(f"✅ Test upload successful! URL: {public_url}")
        
        # Clean up test file
        client.storage.from_('product-images').remove(['test/sample.jpg'])
        print("🧹 Test file cleaned up")
        
        print("\n🎉 Bucket setup complete and verified!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_bucket()
    print(f"\n🎯 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
