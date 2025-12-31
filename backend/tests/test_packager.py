import os
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.packager import Packager

def test_packaging():
    packager = Packager()
    
    # We will use the existing audio file and some dummy metadata
    track_name = "Ek Raat"
    original_file = "e:/Projects/Spotify_Project/data/downloads/Ek Raat - Vilen.mp3"
    
    # Since we haven't run stems yet, we'll create a dummy stems folder for testing
    dummy_stems_dir = os.path.join(os.getcwd(), "data", "dummy_stems")
    os.makedirs(dummy_stems_dir, exist_ok=True)
    
    # Create a dummy file in it
    with open(os.path.join(dummy_stems_dir, "vocals.wav"), "w") as f:
        f.write("dummy audio data")

    analysis_data = {
        "bpm": 89.29,
        "key": "E",
        "loudness_lufs": -8.13,
        "processed_at": "2025-12-31"
    }

    if not os.path.exists(original_file):
        pytest.skip("No original file to package. Run downloader first.")

    zip_path = packager.create_package(track_name, original_file, dummy_stems_dir, analysis_data)

    assert zip_path is not None
    assert os.path.exists(zip_path)
    assert zip_path.endswith(".zip")
    
    print(f"\n--- Packager Test Successful ---")
    print(f"ZIP File: {zip_path}")
    
    # Cleanup dummy data
    os.remove(os.path.join(dummy_stems_dir, "vocals.wav"))
    os.rmdir(dummy_stems_dir)

if __name__ == "__main__":
    test_packaging()
