"""
API Data Schemas
Defines what data the API accepts and returns.
Uses Pydantic for automatic validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class AccessAssignmentInput(BaseModel):
    """
    Input schema for a single access assignment risk check.
    This matches the features our model expects.
    """
    # User features
    user_id: str = Field(..., example="user_0420", description="Unique user identifier")
    department: str = Field(..., example="Finance", description="User's department")
    role: str = Field(..., example="Finance Analyst", description="User's job role")
    tenure_days: int = Field(..., ge=0, le=10000, example=730, description="Days employed")
    
    # Entitlement features
    entitlement_id: str = Field(..., example="ent_030", description="Entitlement identifier")
    risk_level: str = Field(..., example="Critical", description="Low/Medium/High/Critical")
    
    # Assignment features
    is_direct_grant: bool = Field(..., example=True, description="Direct grant vs role-based")
    days_since_last_use: int = Field(..., ge=-1, example=45, description="Days since last used (-1 = never)")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_0420",
                "department": "Finance",
                "role": "Finance Analyst",
                "tenure_days": 730,
                "entitlement_id": "ent_030",
                "risk_level": "Critical",
                "is_direct_grant": True,
                "days_since_last_use": 45
            }
        }


class BatchRiskRequest(BaseModel):
    """For checking multiple assignments at once."""
    assignments: List[AccessAssignmentInput]


class RiskScoreResponse(BaseModel):
    """What the API returns for a single assignment."""
    assignment_id: Optional[str] = None
    user_id: str
    entitlement_id: str
    risk_probability: float = Field(..., ge=0, le=1, description="Risk score 0-1")
    risk_level: str = Field(..., description="Low/Medium/High/Critical")
    recommendation: str = Field(..., description="Approve/Review/Revoke")
    top_factors: List[str] = Field(default=[], description="Why this score")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_0420",
                "entitlement_id": "ent_030",
                "risk_probability": 0.92,
                "risk_level": "Critical",
                "recommendation": "Revoke",
                "top_factors": [
                    "Critical risk level (29.9% importance)",
                    "Never used access (21.4% importance)",
                    "Direct grant (17.9% importance)"
                ]
            }
        }


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
