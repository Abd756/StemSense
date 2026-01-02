<h1 align="center">StemSense 🎵 | AI Audio Engine</h1>

<p align="center">
  <img src="assets/hero.png" alt="StemSense Dashboard" width="800">
</p>

<p align="center">
  <strong>StemSense</strong> is a professional-grade, full-stack application that leverages industry-leading AI models to isolate audio stems (Vocals, Drums, Bass, Other) and perform deep musical analysis (BPM, Key, Loudness) on any song from YouTube.
</p>

---

## 🚀 Key Features & AI Technology

### 1. 🤖 AI Stem Separation
*   **Model**: **Demucs** (v4) by Meta (Facebook) Research.
*   **Architecture**: Uses the **Hybrid Transformer (htdemucs)** model for state-of-the-art vocal and instrumental isolation without quality loss.
*   **Performance**: Automatically detects and uses **NVIDIA CUDA GPU** for high-speed processing.

### 2. 📥 Smart Audio Downloader
*   **Library**: **yt-dlp**.
*   **Functionality**: Extracts high-quality 320kbps MP3 audio from any YouTube URL or search query. Implements filename sanitization to ensure compatibility with AI models.

### 3. 📊 Clinical Audio Analysis
*   **Musical Data**: **Librosa** is used to accurately detect the song's **Tempo (BPM)** and **Musical Key** (e.g., C Minor).
*   **Loudness**: **pyloudnorm** is utilized to calculate professional-standard **Integrated LUFS** (Loudness Units Full Scale).

---

## 🛠️ Project Stack

| **Component** | **Technology** |
| :--- | :--- |
| **Frontend** | Next.js (App Router), TypeScript, Tailwind CSS, Framer Motion |
| **Backend** | Python 3.10+, FastAPI, Uvicorn (Asynchronous Processing) |
| **API Bridge** | Axios, ngrok (for public tunneling) |
| **Automation** | Python BackgroundTasks |

---

## ⚙️ Installation & Setup

### Prerequisites
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js (LTS)](https://nodejs.org/)
*   [ffmpeg](https://ffmpeg.org/download.html) (Essential for audio processing)

### 1. Backend Setup
```powershell
# Navigate to project root
cd e:\Projects\Spotify_Project

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) For high-speed GPU processing
pip install torch --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

# 🛡️ Firebase Credentials (Required for Firestore access)
# Set your service account key path (Replace with your actual path)
$env:GOOGLE_APPLICATION_CREDENTIALS="E:\gcp-key.json"
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
```

---

## 🏃‍♂️ Running the Project

You will need **two separate terminals** running at the same time:

### **Terminal 1: The Engine (Backend)**
```powershell
# From project root
$env:GOOGLE_APPLICATION_CREDENTIALS="E:\gcp-key.json"
python backend/api.py
```
*Wait for: `Uvicorn running on http://0.0.0.0:8080`*

### **Terminal 2: The Interface (Frontend)**
```powershell
# From project root
cd frontend
npm run dev
```
*Open [http://localhost:3000](http://localhost:3000) in your browser.*

---

## 📂 Project Structure
```text
Spotify_Project/
├── backend/            # Python API & AI Core
│   ├── core/           # Demucs, yt-dlp, and Librosa logic
│   ├── data/           # Processed MP3s and Zip Exports
│   └── api.py          # FastAPI Server
├── frontend/           # Next.js Application
│   ├── src/app         # UI Components and Layout
│   └── src/lib/api.ts  # Connection to Backend
└── README.md           # You are here
```

---

## 📝 Usage Guide
1.  Launch both **Backend** and **Frontend**.
2.  Paste a **YouTube Link** or type a **Song Name** (e.g., "The Weeknd Blinding Lights").
3.  Watch the **Processing Pipeline** animate through steps: Download ➔ Separate ➔ Analyze ➔ Package.
4.  Once complete, click the **Download Stems** button to receive a ZIP containing your high-quality files and metadata.

---
*Built with ❤️ for Music Producers and AI Enthusiasts.*
