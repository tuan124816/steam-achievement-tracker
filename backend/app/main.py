# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import json
import asyncio
import time
from typing import List, Dict, Any

# Import tracker runner from your existing code base.
# Adjust the import path depending on where your tracker package lies.
# Example if tracker is a package at repo root: from tracker.main import run_tracker
# But run_tracker expects a config dict. We'll call it inside a background task.
from tracker.main import run_tracker  # <- adjust if needed
from backend.app.api.health import router as health_router


ROOT = Path(__file__).resolve().parents[2]
print('current ROOT is: ', ROOT)
UPLOAD_DIR = ROOT / "uploaded_configs"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

app = FastAPI(
    title="Steam Achievement Tracker API",
    version="2.0.0",
)

# Register routers
app.include_router(health_router)

# Allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # SvelteKit dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for active jobs and logs
_active_jobs: Dict[str, Dict[str, Any]] = {}
_websocket_connections: List[WebSocket] = []


@app.post("/api/config")
async def upload_config(file: UploadFile = File(...)):
    """
    Upload a config.json file to the backend (saves to uploaded_configs/).
    Returns the stored path and parsed JSON.
    """
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    data = json.loads(dest.read_text(encoding="utf-8"))
    return {"path": str(dest), "config": data}


@app.get("/api/config")
async def get_config(filename: str = "config.json"):
    p = UPLOAD_DIR / filename
    if not p.exists():
        raise HTTPException(404, "Config not found")
    return json.loads(p.read_text(encoding="utf-8"))


@app.post("/api/run")
async def run_tracker_endpoint(background_tasks: BackgroundTasks, config_path: str = "config.json"):
    """
    Start the tracker as a background job using config file saved in uploaded_configs/.
    Returns a job id that can be used to watch logs/status.
    """
    cfg_file = UPLOAD_DIR / config_path
    if not cfg_file.exists():
        raise HTTPException(400, "config file not found, upload via /api/config first")

    cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    job_id = str(int(time.time()))
    _active_jobs[job_id] = {"status": "queued", "logs": []}

    # Schedule background runner
    background_tasks.add_task(_run_job, job_id, cfg)
    return {"job_id": job_id}


async def _broadcast_log(msg: str):
    # broadcast to connected websockets (best-effort)
    for ws in list(_websocket_connections):
        try:
            await ws.send_text(msg)
        except Exception:
            try:
                await ws.close()
            except Exception:
                pass
            _websocket_connections.remove(ws)


def _append_job_log(job_id: str, line: str):
    _active_jobs.setdefault(job_id, {"logs": [], "status": "running"})
    _active_jobs[job_id]["logs"].append(line)


async def _run_job(job_id: str, cfg: Dict):
    """
    Run tracker.run_tracker(cfg) in a background thread
    and safely stream logs back to the async event loop.
    """
    _active_jobs[job_id]["status"] = "running"

    # ✅ Capture the REAL FastAPI event loop
    loop = asyncio.get_running_loop()

    def _local_log(msg: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}"

        _append_job_log(job_id, line)

        # ✅ SAFE cross-thread asyncio call
        asyncio.run_coroutine_threadsafe(
            _broadcast_log(line),
            loop
        )

    def _call_tracker():
        try:
            _local_log("Starting tracker job ...")
            run_tracker(cfg)
            _local_log("Tracker finished successfully.")
            _active_jobs[job_id]["status"] = "done"
        except Exception as e:
            _local_log(f"Tracker error: {e}")
            _active_jobs[job_id]["status"] = "failed"

    try:
        # ✅ Run blocking tracker code in thread
        await loop.run_in_executor(None, _call_tracker)
    except Exception as e:
        _append_job_log(job_id, f"job failed: {e}")
        _active_jobs[job_id]["status"] = "failed"


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = _active_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"job_id": job_id, "status": job["status"], "logs": job["logs"]}


# Serve the generated Excel by path (simple)
@app.get("/api/download")
async def download_file(filename: str):
    p = Path(filename)
    if not p.exists():
        raise HTTPException(404, "File not found")
    # use fastapi.responses.FileResponse when wiring frontend
    from fastapi.responses import FileResponse
    return FileResponse(p, filename=p.name)


# WebSocket for logs / live updates
@app.websocket("/ws/logs/{job_id}")
async def websocket_logs(ws: WebSocket, job_id: str):
    await ws.accept()
    _websocket_connections.append(ws)
    try:
        # Send current logs, then keep listening
        job = _active_jobs.get(job_id)
        if job:
            for l in job["logs"]:
                await ws.send_text(l)
        while True:
            # Keep connection alive; we don't expect client messages
            try:
                await ws.receive_text()
            except Exception:
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        _websocket_connections.remove(ws)
