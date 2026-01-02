import os
import requests
from google.cloud import storage
from datetime import timedelta

# Configuration
BUCKET_NAME = "stemsense-audio-700920052420"
# The specific file the user asked to test
FILENAME = "StemSense_Dastaan-E-Om_Shanti_Om_Full_Song_Om_Shanti_Om_Shahrukh_Khan_20260102_133937.zip"
BLOB_PATH = f"exports/{FILENAME}"

def test_gcs_download():
    print(f"🧪 Testing GCS Download for: {BLOB_PATH}")
    print(f"🪣 Bucket: {BUCKET_NAME}")

    try:
        # 1. Initialize Storage Client
        # (This will use GOOGLE_APPLICATION_CREDENTIALS from env)
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(BLOB_PATH)

        # 2. Check if file exists
        if not blob.exists():
            print(f"❌ Error: File NOT FOUND in bucket!")
            return

        print("✅ File found in bucket.")

        # 3. Generate Signed URL
        print("🔑 Generating Signed URL...")
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET",
        )
        print(f"🔗 Signed URL generated: {url[:50]}...")

        # 4. Attempt Download
        print("⬇️ Attempting to download via Signed URL...")
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            print(f"✅ Success! HTTP 200 OK.")
            print(f"📦 Content Size: {response.headers.get('Content-Length')} bytes")
            
            # Optional: Save a tiny chunk to prove it works
            with open("test_downloaded_file.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    break # Just read first chunk to verify readability
            print("✅ Verified: First chunk written to 'test_downloaded_file.zip'")
            
            # Cleanup
            os.remove("test_downloaded_file.zip")
        else:
            print(f"❌ Failed to download. HTTP {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        if "403" in str(e):
             print("💡 Hint: Permission denied. Check your Service Account permissions.")

if __name__ == "__main__":
    test_gcs_download()
