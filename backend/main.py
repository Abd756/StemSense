import argparse
import os
import sys
from core.downloader import AudioDownloader
from core.stems import StemSeparator
from core.analyzer import AudioAnalyzer
from core.packager import Packager

def main():
    # 1. Set up Command Line Arguments
    parser = argparse.ArgumentParser(description="StemSense: AI Audio Analysis & Separation Workflow")
    parser.add_argument("input", help="Song name or YouTube URL")
    args = parser.parse_args()

    print("\n" + "="*50)
    print("      🎵 WELCOME TO STEMSENSE 🎵")
    print("="*50 + "\n")

    # 2. Initialize Modules
    downloader = AudioDownloader()
    separator = StemSeparator()
    analyzer = AudioAnalyzer()
    packager = Packager()

    try:
        # STEP 1: DOWNLOAD
        print("[1/4] Starting Download...")
        audio_path = downloader.download(args.input)
        if not audio_path:
            print("❌ Download failed. Exiting.")
            return

        track_filename = os.path.basename(audio_path)
        track_name = os.path.splitext(track_filename)[0]

        # STEP 2: SEPARATE STEMS
        print("\n[2/4] Separating Stems (Vocals, Drums, Bass, Other)...")
        # This will call Demucs
        stems_dir = separator.separate(audio_path)
        if not stems_dir:
            print("❌ Stem separation failed. Exiting.")
            return

        # STEP 3: ANALYZE AUDIO
        print("\n[3/4] Analyzing Audio DNA (BPM, Key, Loudness)...")
        analysis_results = analyzer.analyze(audio_path)
        if not analysis_results:
            print("⚠️ Analysis failed. Continuing without metadata.")
            analysis_results = {"error": "Analysis failed"}

        # STEP 4: PACKAGE EVERYTHING
        print("\n[4/4] Bundling everything into a ZIP...")
        zip_path = packager.create_package(
            track_name=track_name,
            original_file=audio_path,
            stems_dir=stems_dir,
            analysis_data=analysis_results
        )

        if zip_path:
            print("\n" + "="*50)
            print("✨ SUCCESS: Workflow Complete!")
            print(f"📦 Final Package: {zip_path}")
            print("="*50 + "\n")
        else:
            print("❌ Packaging failed.")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
