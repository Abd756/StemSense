import os
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.downloader import AudioDownloader

def test_yt_downloader_search():
    """
    Test the new yt-dlp based downloader with a search query.
    """
    downloader = AudioDownloader()
    query = "Lofi Hip Hop Short Loop"
    print(f"\nTesting Search: {query}")
    file_path = downloader.download(query)
    
    assert file_path is not None
    assert os.path.exists(file_path)
    assert file_path.endswith(".mp3")
    print(f"Search Test Successful! File saved at: {file_path}")

def test_yt_downloader_url():
    """
    Test the yt-dlp based downloader with a specific YouTube URL.
    """
    downloader = AudioDownloader()
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Never Gonna Give You Up
    print(f"\nTesting URL: {url}")
    file_path = downloader.download(url)
    
    assert file_path is not None
    assert os.path.exists(file_path)
    assert file_path.endswith(".mp3")
    print(f"URL Test Successful! File saved at: {file_path}")

if __name__ == "__main__":
    # You can run either or both
    test_yt_downloader_search()
    test_yt_downloader_url()
