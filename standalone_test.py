import subprocess
import os

def download_by_name(song_name):
    """
    Standalone script to test spotDL downloading by song name.
    This does not explicitly use our Spotify API credentials.
    """
    print(f"\n--- Standalone spotDL Test ---")
    print(f"Task: Search and Download '{song_name}'")
    
    # Create a local test folder
    test_dir = os.path.join(os.getcwd(), "test_downloads")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created directory: {test_dir}")

    try:
        # spotdl can take a search query directly
        # Format: spotdl download "Song Name"
        command = [
            "spotdl",
            "download",
            song_name,
            "--output",
            os.path.join(test_dir, "{title} - {artist}.{output-ext}")
        ]
        
        print("Executing command: " + " ".join(command))
        print("Please wait, searching YouTube...\n")
        
        # We run this so you can see the progress bar in the terminal
        subprocess.run(command, check=True)
        
        print(f"\n[SUCCESS] Download completed!")
        print(f"Check the folder: {test_dir}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] spotDL failed with return code {e.returncode}")
        print("This may be due to network issues or rate limits on YouTube/Spotify.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    query = input("Enter song name (e.g. 'Stairway to Heaven'): ")
    if query.strip():
        download_by_name(query)
    else:
        print("No song name entered.")
