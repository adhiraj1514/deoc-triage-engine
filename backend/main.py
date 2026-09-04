import os
import sys

# --- FIX FOR CLOUD DEPLOYMENT IMPORTS ---
# This tells the server to look inside the 'backend' folder for your other Python files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from cluster import cluster_disaster_reports

app = FastAPI(title="DEOC Disaster Triage Engine - Talegaon Dabhade", version="1.0")

# Enable CORS for frontend command dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW ROUTE TO SERVE THE FRONTEND DASHBOARD ---
@app.get("/")
async def serve_dashboard():
    # Looks for the HTML file one folder up, inside the 'frontend' directory
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    
    # If the file doesn't exist at that path, return a helpful error
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Dashboard index.html not found. Check folder structure.")
        
    return FileResponse(html_path)

# --- DATA SCHEMAS ---
class DisasterReport(BaseModel):
    id: str
    text: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    timestamp: str

class IncidentClusterResponse(BaseModel):
    cluster_id: str
    latitude: float
    longitude: float
    total_reports: int
    estimated_victims: int
    priority_level: str
    hazard_type: str
    sample_messages: List[str]

# --- API ENDPOINTS ---
@app.post("/api/ingest", response_model=List[IncidentClusterResponse])
def ingest_reports(reports: List[DisasterReport]):
    """
    Ingests live disaster reports, resolves offline coordinates,
    extracts NLP entities, and clusters data to mitigate command overload.
    """
    try:
        # Convert Pydantic models to dicts for the cluster engine
        raw_reports = [r.model_dump() for r in reports]
        clustered_data = cluster_disaster_reports(raw_reports)
        return clustered_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "region": "Talegaon Dabhade, Pune",
        "message": "DEOC Triage Engine backend operational."
    }