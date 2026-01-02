import os

# Project Settings
DOWNLOAD_DIR = os.path.join(os.getcwd(), "data", "downloads")
STEMS_DIR = os.path.join(os.getcwd(), "data", "stems")
EXPORT_DIR = os.path.join(os.getcwd(), "data", "exports")

# Ensure directories exist
for directory in [DOWNLOAD_DIR, STEMS_DIR, EXPORT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Google Cloud Storage Settings
# Replace with your actual bucket name created in the console
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "stemsense-audio-700920052420")
