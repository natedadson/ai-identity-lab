"""
Identity Risk Scoring API - With Detailed Explanations
"""

import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

from .schemas import (
    AccessAssignmentInput, 
    BatchRiskRequest, 
    RiskScoreResponse,
    HealthResponse
)

app = FastAPI(
    title="Identity Risk Scoring API",
    description="Predicts risky access assignments",
    version="1.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
scaler = None
expected_features = []

RISK_TO_NUMERIC = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def load_model():
    global model, scaler, expected_features
    
    model_path = "01-identity-risk-scoring/models/risk_scorer.pkl"
    scaler_path = "01-identity-risk-scoring/models/scaler.pkl"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    if hasattr(scaler, 'feature_names_in_'):
        expected_features = list(scaler.feature_names_in_)
    else:
        expected_features = [
            'risk_score_numeric', 'never_used', 'is_direct_grant', 
            'tenure_days', 'days_since_last_use', 'is_privileged_role',
            'dept_R&D', 'dept_Sales', 'dept_Product', 
            'dept_Customer_Support', 'dept_Finance'
        ]
    
    print(f"Model loaded. Features: {len(expected_features)}")
    return True


def get_top_factors(prob: float, assignment: AccessAssignmentInput) -> List[str]:
    """Generate human-readable explanations."""
    factors = []
    
    if prob > 0.7:
        if assignment.risk_level in ["High", "Critical"]:
            factors.append(f"⚠️ {assignment.risk_level} risk level is a top indicator")
        
        if assignment.days_since_last_use == -1:
            factors.append("❌ Never used - stale access is highly risky")
        elif assignment.days_since_last_use > 90:
            factors.append(f"⏰ Unused for {assignment.days_since_last_use} days")
        
        if assignment.is_direct_grant:
            factors.append("🔓 Direct grant (bypasses role-based controls)")
        
        if assignment.tenure_days < 90:
            factors.append("👤 New employee with privileged access")
    
    elif prob > 0.4:
        if assignment.risk_level in ["High", "Critical"]:
            factors.append(f"📊 {assignment.risk_level} risk level requires review")
        if assignment.days_since_last_use > 60:
            factors.append("📅 Access not recently used")
    else:
        factors.append("✅ Access appears appropriate for role")
        if not assignment.is_direct_grant:
            factors.append("🛡️ Role-based assignment follows least privilege")
    
    return factors[:3] if factors else ["Risk score based on multiple factors"]


def get_recommendation(prob: float) -> str:
    if prob >= 0.7:
        return "Revoke"
    elif prob >= 0.4:
        return "Review"
    else:
        return "Approve"


def prepare_features(assignment: AccessAssignmentInput) -> pd.DataFrame:
    features_dict = {col: 0 for col in expected_features}
    
    features_dict['risk_score_numeric'] = RISK_TO_NUMERIC[assignment.risk_level]
    features_dict['never_used'] = 1 if assignment.days_since_last_use == -1 else 0
    features_dict['is_direct_grant'] = 1 if assignment.is_direct_grant else 0
    features_dict['tenure_days'] = assignment.tenure_days
    features_dict['days_since_last_use'] = assignment.days_since_last_use
    features_dict['is_privileged_role'] = 1 if any(x in assignment.role.lower() for x in ['manager', 'executive', 'admin', 'senior']) else 0
    
    dept_col = f"dept_{assignment.department}"
    if dept_col in features_dict:
        features_dict[dept_col] = 1
    else:
        for col in expected_features:
            if col.startswith('dept_'):
                features_dict[col] = 1
                break
    
    df = pd.DataFrame([features_dict])
    df = df[expected_features]
    return df


@app.on_event("startup")
async def startup_event():
    load_model()
    print("API ready!")


@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        version="1.0.0"
    )


@app.post("/predict", response_model=RiskScoreResponse)
async def predict_single(assignment: AccessAssignmentInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        features_df = prepare_features(assignment)
        features_scaled = scaler.transform(features_df)
        prob = model.predict_proba(features_scaled)[0][1]
        
        risk_level = "Critical" if prob >= 0.7 else "Medium" if prob >= 0.4 else "Low"
        
        return RiskScoreResponse(
            user_id=assignment.user_id,
            entitlement_id=assignment.entitlement_id,
            risk_probability=round(prob, 3),
            risk_level=risk_level,
            recommendation=get_recommendation(prob),
            top_factors=get_top_factors(prob, assignment)
        )
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=List[RiskScoreResponse])
async def predict_batch(request: BatchRiskRequest):
    responses = []
    for assignment in request.assignments:
        result = await predict_single(assignment)
        responses.append(result)
    return responses


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
