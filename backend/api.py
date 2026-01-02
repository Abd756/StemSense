from fastapi import FastAPI, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
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
from google.cloud import storage
from config import GCS_BUCKET_NAME
from datetime import timedelta


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
    "https://stemvibe.vercel.app",
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

# Helper to check if task was cancelled
def is_cancelled(task_id: str) -> bool:
    doc = db.collection(TASKS_COLLECTION).document(task_id).get()
    if doc.exists and doc.to_dict().get("status") == "cancelled":
        print(f"🛑 Task {task_id} was cancelled by user. Stopping.")
        return True
    return False

# Helper function to run the heavy processing in the background
def run_full_workflow(task_id: str, query: str):
    # 🛑 CHECKPOINT 1: Start
    if is_cancelled(task_id): return

    # Set status to downloading in Firestore
    db.collection(TASKS_COLLECTION).document(task_id).update({"status": "downloading"})
    
    downloader = AudioDownloader()
    separator = StemSeparator()
    analyzer = AudioAnalyzer()
    packager = Packager()

    try:
        # 🛑 CHECKPOINT 2: Before Download
        if is_cancelled(task_id): return

        # 1. Download
        audio_path = downloader.download(query)
        if not audio_path:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "failed",
                "error": "Download failed"
            })
            return

        track_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        # 🛑 CHECKPOINT 3: Before Separation (Expensive!)
        if is_cancelled(task_id): return

        # 2. Separate
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "separating"})
        stems_dir = separator.separate(audio_path)
        if not stems_dir:
            db.collection(TASKS_COLLECTION).document(task_id).update({
                "status": "failed",
                "error": "Stem separation failed"
            })
            return

        # 🛑 CHECKPOINT 4: Before Analysis
        if is_cancelled(task_id): return

        # 3. Analyze
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "analyzing"})
        analysis_results = analyzer.analyze(audio_path)

        # 🛑 CHECKPOINT 5: Before Packaging
        if is_cancelled(task_id): return

        # 4. Package
        db.collection(TASKS_COLLECTION).document(task_id).update({"status": "packaging"})
        zip_path = packager.create_package(
            track_name=track_name,
            original_file=audio_path,
            stems_dir=stems_dir,
            analysis_data=analysis_results or {"note": "analysis failed"}
        )

        # 🛑 CHECKPOINT 6: Final check before marking complete
        if is_cancelled(task_id): return

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
        # One last check to see if we failed BECAUSE of a purposeful cancel
        if is_cancelled(task_id): return
        
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

@app.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel an ongoing task.
    """
    doc_ref = db.collection(TASKS_COLLECTION).document(task_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task not found")
        
    current_status = doc.to_dict().get("status")
    if current_status in ["completed", "failed", "cancelled"]:
        return {"message": "Task already finished or cancelled"}
        
    # Mark as cancelled
    doc_ref.update({"status": "cancelled"})
    return {"message": "Task cancellation requested"}

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
    Generate a Signed URL for the GCS file and redirect the user to it.
    Uses IAM Signer for Cloud Run compatibility.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"exports/{filename}")

        if not blob.exists():
            raise HTTPException(status_code=404, detail="File not found in Cloud Storage")

        # Authenticate and setup signer
        credentials, project_id = google.auth.default()
        signer = None
        service_account_email = None

        # Check if we are on Cloud Run (no private key)
        if hasattr(credentials, "service_account_email"):
            # Refresh to ensure we have the email and token
            request = google_requests.Request()
            credentials.refresh(request)
            service_account_email = credentials.service_account_email
            
            # Use IAM Signer (REQUIRES 'Service Account Token Creator' Role)
            signer = iam.Signer(request, credentials, service_account_email)

        # Generate a signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET",
            service_account_email=service_account_email,
            signer=signer # Uses local key if None, or IAM API if provided
        )
        
        return RedirectResponse(url=url)

    except Exception as e:
        print(f"Error generating signed URL: {e}")
        # Log the specific error to help debugging
        if "403" in str(e) or "Permission denied" in str(e):
             print("💡 HINT: Ensure Service Account has 'Service Account Token Creator' role.")
        raise HTTPException(status_code=500, detail="Could not generate download link")

if __name__ == "__main__":
    import uvicorn
    # Use PORT env var if available (Cloud Run sets this), otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
