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
        Automatically detects and uses GPU (CUDA) if available.
        """
        if not os.path.exists(audio_path):
            print(f"⚠️ Audio file not found at {audio_path}. Attempting to recover from GCS...")
            try:
                from google.cloud import storage
                from config import GCS_BUCKET_NAME
                
                client = storage.Client()
                bucket = client.bucket(GCS_BUCKET_NAME)
                blob_name = f"downloads/{os.path.basename(audio_path)}"
                blob = bucket.blob(blob_name)
                
                if blob.exists():
                    print(f"🔄 Recovering from GCS: gs://{GCS_BUCKET_NAME}/{blob_name}...")
                    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                    blob.download_to_filename(audio_path)
                    print("✅ Recovery successful!")
                else:
                    print(f"❌ File not found in GCS: {blob_name}")
                    return None
            except Exception as e:
                print(f"❌ Recovery failed: {e}")
                return None

        # Detect Device (GPU vs CPU)
        device = "cpu"
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                print("🚀 CUDA GPU detected! Using GPU for high-speed separation.")
            else:
                print("💻 GPU not detected or not supported. Falling back to CPU.")
        except ImportError:
            print("📦 Torch not found. Defaulting to CPU.")

        print(f"Starting stem separation for: {audio_path}")
        if device == "cpu":
            print("⚠️ Running on CPU - this may take several minutes...")

        try:
            # -n htdemucs: Use the hybrid transformer model (highest quality)
            # -d: Specify device (cuda or cpu)
            # --out: Specifies the output directory
            command = [
                "demucs",
                "-n", "htdemucs",
                "-d", device,
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
