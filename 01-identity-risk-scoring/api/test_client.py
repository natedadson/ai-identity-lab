"""
Test Client for Identity Risk Scoring API
Tests the API with sample data.
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{API_URL}/")
    print(f"Health: {response.json()}")
    return response.status_code == 200

def test_predict():
    """Test single prediction."""
    sample = {
        "user_id": "user_0420",
        "department": "Finance",
        "role": "Finance Analyst",
        "tenure_days": 730,
        "entitlement_id": "ent_030",
        "risk_level": "Critical",
        "is_direct_grant": True,
        "days_since_last_use": 45
    }
    
    response = requests.post(f"{API_URL}/predict", json=sample)
    print("\n📊 Single Prediction Test:")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_batch():
    """Test batch prediction."""
    samples = [
        {
            "user_id": "user_0001",
            "department": "Engineering",
            "role": "Software Engineer",
            "tenure_days": 365,
            "entitlement_id": "ent_001",
            "risk_level": "High",
            "is_direct_grant": False,
            "days_since_last_use": 10
        },
        {
            "user_id": "user_0002",
            "department": "Finance",
            "role": "Analyst",
            "tenure_days": 100,
            "entitlement_id": "ent_100",
            "risk_level": "Critical",
            "is_direct_grant": True,
            "days_since_last_use": -1  # Never used
        }
    ]
    
    response = requests.post(f"{API_URL}/predict/batch", json={"assignments": samples})
    print("\n📊 Batch Prediction Test:")
    for result in response.json():
        print(f"  User {result['user_id']}: {result['risk_probability']:.2%} → {result['recommendation']}")
    return response.status_code == 200

if __name__ == "__main__":
    print("="*50)
    print("TESTING IDENTITY RISK SCORING API")
    print("="*50)
    
    print("\n1. Testing health endpoint...")
    test_health()
    
    print("\n2. Testing single prediction...")
    test_predict()
    
    print("\n3. Testing batch prediction...")
    test_batch()
    
    print("\n✅ Tests complete!")
