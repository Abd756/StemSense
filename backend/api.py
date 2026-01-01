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

# In-memory storage for task statuses (In a real app, use Redis or a DB)
tasks = {}

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
    tasks[task_id]["status"] = "downloading"
    
    downloader = AudioDownloader()
    separator = StemSeparator()
    analyzer = AudioAnalyzer()
    packager = Packager()

    try:
        # 1. Download
        audio_path = downloader.download(query)
        if not audio_path:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "Download failed"
            return

        track_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        # 2. Separate
        tasks[task_id]["status"] = "separating"
        stems_dir = separator.separate(audio_path)
        if not stems_dir:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "Stem separation failed"
            return

        # 3. Analyze
        tasks[task_id]["status"] = "analyzing"
        analysis_results = analyzer.analyze(audio_path)

        # 4. Package
        tasks[task_id]["status"] = "packaging"
        zip_path = packager.create_package(
            track_name=track_name,
            original_file=audio_path,
            stems_dir=stems_dir,
            analysis_data=analysis_results or {"note": "analysis failed"}
        )

        if zip_path:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result_file"] = os.path.basename(zip_path)
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "Packaging failed"

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.get("/")
async def root():
    return {"message": "Welcome to StemSense API. Use POST /process to start."}

@app.post("/process", response_model=dict)
async def process_audio(background_tasks: BackgroundTasks, input: str = Form(...)):
    """
    Submit a song name or YouTube URL for processing via Form Data.
    """
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "result_file": None,
        "error": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Start the background task
    background_tasks.add_task(run_full_workflow, task_id, input)
    
    return {"task_id": task_id, "message": "Job submitted successfully"}

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """
    Check the status of a processing task.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
