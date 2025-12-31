import pytest
import os
import glob
from core.stems import StemSeparator
from core.downloader import AudioDownloader
from config import DOWNLOAD_DIR, STEMS_DIR

@pytest.fixture
def separator():
    return StemSeparator()

def test_separate_stems(separator):
    # Use the file specifically requested by the user
    audio_path = r"e:\Projects\Spotify_Project\test_downloads\Ek Raat - Vilen.mp3"
    
    # Check if the file exists before starting
    assert os.path.exists(audio_path), f"Input audio file not found at {audio_path}"

    # 2. Perform separation
    stems_path = separator.separate(audio_path)
    
    assert stems_path is not None
    assert os.path.exists(stems_path)
    
    # 3. Verify the 4 default stems exist and print info
    print("\n--- Stem Extraction Results ---")
    expected_stems = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
    for stem in expected_stems:
        stem_file = os.path.join(stems_path, stem)
        assert os.path.exists(stem_file), f"Missing stem: {stem}"
        
        # Calculate size in MB for the success message
        size_mb = os.path.getsize(stem_file) / (1024 * 1024)
        print(f"File: {stem:<12} | Size: {size_mb:>6.2f} MB")

    print(f"\n[SUCCESS] All 4 stems verified in: {stems_path}")
