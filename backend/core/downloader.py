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

        # yt-dlp options for high quality audio extraction with Anti-Bot measures
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'default_search': 'ytsearch',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            # 🛡️ Higher compatibility settings
            'quiet': False,
            'no_warnings': True,
            'http_chunk_size': 1048576,
        }

        # 🍪 Check for cookies.txt (The 100% fix for Bot Detection)
        # We look in the same directory as this script (core/) or the backend root
        cookie_path = os.path.join(os.getcwd(), 'cookies.txt')
        if os.path.exists(cookie_path):
            print(f"🍪 Found cookies.txt at {cookie_path}! Using it to bypass bot detection.")
            ydl_opts['cookiefile'] = cookie_path
        else:
            print("⚠️ No cookies.txt found. YouTube might block this request on Cloud IPs.")

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
