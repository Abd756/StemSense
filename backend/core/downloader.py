import subprocess
import os
import yt_dlp
from config import DOWNLOAD_DIR

class AudioDownloader:
    def __init__(self, output_dir=DOWNLOAD_DIR):
        """
        The AudioDownloader handles fetching high-quality audio from YouTube
        using either a direct URL or a search query (Song Name).
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download(self, query: str):
        """
        Download high-quality MP3 audio from YouTube using yt-dlp.
        
        Args:
            query (str): YouTube URL or Song Name.
            
        Returns:
            str: The absolute path to the downloaded audio file, or None if failed.
        """
        print(f"Searching and downloading: {query}")

        # yt-dlp options for high quality audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            # Search logic: if not a URL, search YouTube
            'default_search': 'ytsearch',
            # Output template: Title.mp3
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'restrictfilenames': True,  # 🛡️ Prevents special chars like | or ｜ that break Demucs
            'noplaylist': True,         # 🚫 Prevents downloading entire playlists/mixes
            'quiet': False,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info and download
                info = ydl.extract_info(query, download=True)
                
                # Handle both direct URLs and search results
                if 'entries' in info:
                    # Case: Search query
                    video_info = info['entries'][0]
                else:
                    # Case: Direct URL
                    video_info = info
                
                # Get the actual filename generated
                # (Post-processors change extension to .mp3)
                base_filename = ydl.prepare_filename(video_info)
                final_filename = os.path.splitext(base_filename)[0] + ".mp3"
                
                if os.path.exists(final_filename):
                    print(f"Download Finished: {final_filename}")
                    return final_filename
                else:
                    print("Error: Post-processor failed to create MP3 file.")
                    return None

        except Exception as e:
            print(f"Error during YouTube download: {e}")
            return None

    def get_downloaded_files(self):
        """Return a list of files in the download directory."""
        return [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if os.path.isfile(os.path.join(self.output_dir, f))]
