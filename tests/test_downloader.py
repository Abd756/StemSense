import pytest
import os
import shutil
from core.downloader import AudioDownloader
from config import DOWNLOAD_DIR

@pytest.fixture
def downloader():
    # Setup: Ensure clean download directory for testing
    if os.path.exists(DOWNLOAD_DIR):
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    
    return AudioDownloader()

def test_download_by_name(downloader):
    # Using a specific song name
    query = "Ek Raat Vilen" 
    
    success = downloader.download(query)
    
    # Check if download was initiated successfully
    assert success is True
    
    # Check if a file was actually created
    downloaded_files = downloader.get_downloaded_files()
    assert len(downloaded_files) > 0
    
    # Verify it is an audio file (typically .mp3 or .m4a depending on spotDL config)
    extension = os.path.splitext(downloaded_files[0])[1]
    assert extension in ['.mp3', '.m4a', '.wav']
    
    print(f"\nSuccessfully downloaded: {downloaded_files[0]}")
