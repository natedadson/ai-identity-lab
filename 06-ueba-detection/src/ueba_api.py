"""
UEBA API - FastAPI endpoint for real-time behavior analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import pickle
import json
from datetime import datetime
import os

from ueba_detector import UEBADetector

app = FastAPI(
    title="UEBA Analytics API",
    description="Real-time User & Entity Behavior Analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
detector = None

@app.on_event("startup")
async def load_model():
    global detector
    detector = UEBADetector()
    
    # Load baselines if they exist
    if os.path.exists("06-ueba-detection/output/baselines.pkl"):
        with open("06-ueba-detection/output/baselines.pkl", 'rb') as f:
            detector.user_baselines = pickle.load(f)
        print(f"✅ Loaded baselines for {len(detector.user_baselines)} users")
    
    # Load existing alerts
    if os.path.exists("06-ueba-detection/output/alerts.json"):
        with open("06-ueba-detection/output/alerts.json", 'r') as f:
            detector.alerts = json.load(f)
        print(f"✅ Loaded {len(detector.alerts)} existing alerts")

class BehaviorEvent(BaseModel):
    user_id: str
    timestamp: str
    location: str
    app: str
    hour: int

class BatchAnalysisRequest(BaseModel):
    events: List[BehaviorEvent]

@app.get("/")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_behavior(event: BehaviorEvent):
    """Analyze a single behavior event."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    event_dict = event.dict()
    result = detector.detect_anomalies(event_dict)
    
    alert = None
    if result['is_anomaly'] and result['risk_score'] >= 0.3:
        alert = detector.generate_alert(
            event.user_id,
            result,
            event_dict
        )
        detector.save_alerts()  # Auto-save
    
    return {
        "event": event_dict,
        "analysis": result,
        "alert": alert
    }

@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Analyze multiple events in batch."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    results = []
    for event in request.events:
        result = await analyze_behavior(event)
        results.append(result)
    
    return {"results": results, "count": len(results)}

@app.get("/alerts")
async def get_alerts(limit: int = 100, severity: Optional[str] = None):
    """Get recent alerts."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    alerts = detector.alerts if detector else []
    
    if severity:
        alerts = [a for a in alerts if a.get('severity') == severity]
    
    return {"alerts": alerts[-limit:], "count": len(alerts)}

@app.get("/users/{user_id}/baseline")
async def get_user_baseline(user_id: str):
    """Get baseline for a specific user."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    if user_id not in detector.user_baselines:
        raise HTTPException(status_code=404, detail="User not found")
    
    return detector.user_baselines[user_id]

@app.get("/stats")
async def get_stats():
    """Get UEBA statistics."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    return {
        "total_users": len(detector.user_baselines),
        "total_alerts": len(detector.alerts),
        "critical_alerts": len([a for a in detector.alerts if a.get('severity') == "CRITICAL"]),
        "high_alerts": len([a for a in detector.alerts if a.get('severity') == "HIGH"]),
        "medium_alerts": len([a for a in detector.alerts if a.get('severity') == "MEDIUM"])
    }

@app.delete("/alerts")
async def clear_alerts():
    """Clear all alerts (for testing)."""
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not loaded")
    
    detector.alerts = []
    detector.save_alerts()
    return {"status": "cleared", "count": 0}

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 UEBA API SERVER")
    print("="*60)
    print("📋 Endpoints:")
    print("   POST /analyze          - Analyze single event")
    print("   POST /analyze/batch    - Analyze multiple events")
    print("   GET  /alerts           - Get recent alerts")
    print("   GET  /stats            - Get UEBA statistics")
    print("   GET  /users/{id}/baseline - Get user baseline")
    print("   GET  /                 - Health check")
    print("="*60)
    print("🌐 API Docs: http://localhost:8001/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
