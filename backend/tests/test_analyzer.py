import os
import sys
import pytest

# Add the project root to sys.path so we can import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.analyzer import AudioAnalyzer

def test_audio_analysis():
    """
    Test the AudioAnalyzer on an existing audio file.
    Note: Ensure you have an audio file in data/downloads/ or update the path.
    """
    analyzer = AudioAnalyzer()
    
    # Path to a known test file in your project
    test_file = "e:/Projects/Spotify_Project/data/downloads/Ek Raat - Vilen.mp3"
    
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found at {test_file}. Please download a song first.")

    results = analyzer.analyze(test_file)
    
    # Assertions to ensure we got valid data
    assert results is not None
    assert "bpm" in results
    assert "key" in results
    assert "loudness_lufs" in results
    
    assert isinstance(results["bpm"], float)
    assert results["bpm"] > 0
    assert isinstance(results["key"], str)
    assert isinstance(results["loudness_lufs"], float)

    print(f"\n--- Test Results for {os.path.basename(test_file)} ---")
    print(f"BPM: {results['bpm']}")
    print(f"Key: {results['key']}")
    print(f"Loudness: {results['loudness_lufs']} LUFS")

if __name__ == "__main__":
    # This allows running the test script directly
    test_audio_analysis()
