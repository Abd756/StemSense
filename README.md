# 🎵 StemSense

**StemSense** is a high-performance AI-powered tool designed to deconstruct audio tracks into their fundamental components. Using state-of-the-art machine learning models, it allows users to download any track from YouTube (via URL or Search), isolate individual instruments (stems), and perform deep musical analysis.

---

## ✨ Features

-   **🔍 Smart Search & Download**: Input a song name or a YouTube URL to fetch high-quality audio automatically.
-   **✂️ AI Stem Separation**: Powered by **Demucs**, it splits audio into 4 distinct tracks:
    -   Vocals
    -   Drums
    -   Bass
    -   Other (Melodies/Synths)
-   **📊 Musical Analytics**: 
    -   BPM Detection
    -   Musical Key Identification
    -   Integrated Loudness (LUFS) Analysis
-   **📦 Pro Packaging**: Automatically bundles the original track, isolated stems, and a comprehensive `metadata.json` into a single, organized ZIP file.

---

## 🚀 Quick Start

### Prerequisites
-   **Python 3.9+**
-   **FFmpeg** (Required for audio processing)
-   **CUDA GPU** (Optional, but highly recommended for faster stem separation)

### Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/StemSense.git
    cd StemSense
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv venv
    ./venv/Scripts/activate  # On Windows
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
Run the orchestrator:
```bash
python main.py --input "Song Name or YouTube URL"
```

---

## 🛠️ Tech Stack

-   **Language**: Python 3
-   **Audio Download**: `yt-dlp`
-   **ML Separation**: `Demucs` (Meta AI)
-   **Audio Analysis**: `Essentia` / `Librosa`
-   **Packaging**: `zipfile` (Standard Python)

---

## 📂 Project Structure

-   `core/`: The engine rooms of the application.
-   `data/`: Temporary storage for processing files (ignored by Git).
-   `tests/`: Verification suites for each module.

---

## 📄 License
MIT License. Explore and build with freedom.
