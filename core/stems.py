import os
import subprocess
from config import STEMS_DIR

class StemSeparator:
    def __init__(self, output_dir=STEMS_DIR):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def separate(self, audio_path: str):
        """
        Separate audio into stems (vocals, drums, bass, other) using Demucs.
        
        Note: This is computationally heavy.
        """
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            return None

        print(f"Starting stem separation for: {audio_path}")
        print("This may take a while (especially on CPU)...")

        try:
            # -n htdemucs: Use the hybrid transformer model (highest quality)
            # --out: Specifies the output directory
            command = [
                "demucs",
                "-n", "htdemucs",
                "--out", self.output_dir,
                audio_path
            ]
            
            # Execute demucs
            subprocess.run(command, check=True)
            
            # Demucs creates a folder named after the model used (htdemucs) 
            # and then a folder named after the track.
            track_name = os.path.splitext(os.path.basename(audio_path))[0]
            stems_path = os.path.join(self.output_dir, "htdemucs", track_name)
            
            if os.path.exists(stems_path):
                print(f"Separation completed. Stems located in: {stems_path}")
                return stems_path
            else:
                print("Error: Stems directory was not created.")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Error during separation: {e}")
            return None
        except FileNotFoundError:
            print("Error: 'demucs' command not found. Please ensure it is installed.")
            return None
