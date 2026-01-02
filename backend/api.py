from fastapi import FastAPI, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import shutil
from datetime import datetime

# Import our StemSense modules
from core.downloader import AudioDownloader
from core.stems import StemSeparator
from core.analyzer import AudioAnalyzer
from core.packager import Packager
from config import EXPORT_DIR

app = FastAPI(
    title="StemSense API",
    description="AI Audio Separation & Analysis Service",
    version="1.0.0"
)

# 🛡️ CORS Middleware (Gateway) configuration
# This allows our Next.js frontend to talk to this API
frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    frontend_url,
]

# Ensure we don't have empty strings and help with debugging
active_origins = [o for o in origins if o]
print(f"✅ API active and allowing requests from: {active_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=active_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent storage for task statuses using Google Cloud Firestore
from google.cloud import firestore
db = firestore.Client()
TASKS_COLLECTION = "stemsense_tasks"

class ProcessRequest(BaseModel):
    input: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result_file: Optional[str] = None
    error: Optional[str] = None
    created_at: str

# Helper function to run the heavy processing in the background
def run_full_workflow(task_id: str, query: str):
    # Set status to downloading in Firestore
    db.collection(TASKS_COLLECTION).document(task_id).update({"status": "downloading"})
    
    downloader = AudioDownloader()
    separator = StemSeparator()
    analyzer = AudioAnalyzer()
    packager = Packager()

    try:
        # 1. Download
        audio_path = downloader.download(query)
        if not audio_path:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "failed",
                "error": "Download failed"
            })
            return

        track_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        # 2. Separate
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "separating"})
        stems_dir = separator.separate(audio_path)
        if not stems_dir:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "failed",
                "error": "Stem separation failed"
            })
            return

        # 3. Analyze
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "analyzing"})
        analysis_results = analyzer.analyze(audio_path)

        # 4. Package
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "packaging"})
        zip_path = packager.create_package(
            track_name=track_name,
            original_file=audio_path,
            stems_dir=stems_dir,
            analysis_data=analysis_results or {"note": "analysis failed"}
        )

        if zip_path:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "completed",
                "result_file": os.path.basename(zip_path)
            })
        else:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "failed",
                "error": "Packaging failed"
            })

    except Exception as e:
        db.collection(TASKS_COLLECTION).document(task_id).update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/")
async def root():
    return {"message": "Welcome to StemSense API. Use POST /process to start."}

@app.post("/process", response_model=dict)
async def process_audio(background_tasks: BackgroundTasks, input: str = Form(...)):
    """
    Submit a song name or YouTube URL for processing via Form Data.
    """
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "status": "queued",
        "result_file": None,
        "error": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to Firestore
    db.collection(TASKS_COLLECTION).document(task_id).set(task_data)
    
    # Start the background task
    background_tasks.add_task(run_full_workflow, task_id, input)
    
    return {"task_id": task_id, "message": "Job submitted successfully"}

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """
    Check the status of a processing task from Firestore.
    """
    doc_ref = db.collection(TASKS_COLLECTION).document(task_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return doc.to_dict()

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a completed ZIP package.
    """
    file_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/zip'
    )

if __name__ == "__main__":
    import uvicorn
    # Use PORT env var if available (Cloud Run sets this), otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
