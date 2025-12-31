import subprocess
import os
import shutil
from config import DOWNLOAD_DIR

class AudioDownloader:
    def __init__(self, output_dir=DOWNLOAD_DIR):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download(self, query: str):
        """
        Download a track using a song name or YouTube URL via spotDL.
        """
        print(f"Starting download for: {query}")
        
        # We use subprocess to call spotdl as it's the most reliable way to use it programmatically
        # --output flag specifies the template for the filename
        # {title} - {artist}.{ext} is the default
        try:
            command = [
                "spotdl",
                "download",
                query,
                "--output",
                os.path.join(self.output_dir, "{title} - {artist}.{output-ext}"),
                "--bitrate", "320k"
            ]
            
            # Run without capture_output so user sees progress in terminal
            result = subprocess.run(command, check=True)
            print("Download completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during download. spotDL returned exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print("Error: 'spotdl' command not found. Please ensure it is installed in your virtual environment.")
            return False

    def get_downloaded_files(self):
        """Return a list of files in the download directory."""
        return [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if os.path.isfile(os.path.join(self.output_dir, f))]
