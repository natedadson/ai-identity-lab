"""
Fraud Detection API
Real-time transaction fraud scoring.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time transaction fraud detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load transaction data for reference
transactions_df = None

@app.on_event("startup")
async def load_data():
    global transactions_df
    try:
        if os.path.exists("08-fraud-detection/data/transactions.csv"):
            transactions_df = pd.read_csv("08-fraud-detection/data/transactions.csv")
            print(f"✅ Loaded {len(transactions_df)} transactions")
        else:
            print("⚠️ No transaction data found. Run generate_transactions.py first.")
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")

class Transaction(BaseModel):
    user_id: str
    amount: float
    merchant: str
    location: str
    timestamp: str
    transaction_type: str

class TransactionScore(BaseModel):
    transaction_id: str
    user_id: str
    risk_score: float
    is_fraud: bool
    fraud_signals: List[str]
    recommendation: str

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "data_loaded": transactions_df is not None,
        "transactions_available": len(transactions_df) if transactions_df is not None else 0,
        "version": "1.0.0"
    }

@app.post("/score", response_model=TransactionScore)
async def score_transaction(transaction: Transaction):
    """Score a single transaction for fraud."""
    
    # Preprocess
    tx_data = transaction.dict()
    
    # Basic rules for immediate detection
    fraud_signals = []
    risk_score = 0
    
    # Rule 1: Large amount
    if tx_data['amount'] > 50000:
        risk_score += 0.4
        fraud_signals.append(f"Large transaction amount: ${tx_data['amount']:,.2f}")
    
    # Rule 2: High-risk location
    high_risk_locations = ["Lagos", "Moscow", "Mexico City", "Istanbul", "Dubai"]
    if tx_data['location'] in high_risk_locations:
        risk_score += 0.3
        fraud_signals.append(f"High-risk location: {tx_data['location']}")
    
    # Rule 3: High-risk merchant
    high_risk_merchants = ["Crypto Exchange Ltd", "Online Casino", "FX Trading Inc", 
                          "Offshore Investment", "Digital Wallet Pro"]
    if tx_data['merchant'] in high_risk_merchants:
        risk_score += 0.3
        fraud_signals.append(f"High-risk merchant: {tx_data['merchant']}")
    
    # Rule 4: Unusual transaction type for amount
    if tx_data['transaction_type'] in ["Wire", "ACH"] and tx_data['amount'] > 10000:
        risk_score += 0.2
        fraud_signals.append(f"Large {tx_data['transaction_type']} transaction")
    
    # Rule 5: Check if this user has fraud history (from training data)
    if transactions_df is not None:
        user_txs = transactions_df[transactions_df['user_id'] == tx_data['user_id']]
        if len(user_txs) > 0:
            user_fraud_rate = user_txs['is_fraud'].mean()
            if user_fraud_rate > 0.1:
                risk_score += 0.2
                fraud_signals.append(f"User has {user_fraud_rate*100:.1f}% fraud history")
    
    # Cap risk score at 1.0
    risk_score = min(1.0, risk_score)
    
    # Determine recommendation
    if risk_score > 0.6:
        recommendation = "REJECT"
        is_fraud = True
    elif risk_score > 0.3:
        recommendation = "REVIEW"
        is_fraud = False
    else:
        recommendation = "APPROVE"
        is_fraud = False
    
    return TransactionScore(
        transaction_id=f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        user_id=tx_data['user_id'],
        risk_score=round(risk_score, 3),
        is_fraud=is_fraud,
        fraud_signals=fraud_signals if fraud_signals else ["Transaction appears normal"],
        recommendation=recommendation
    )

@app.post("/score/batch")
async def score_batch(transactions: List[Transaction]):
    """Score multiple transactions."""
    results = []
    for tx in transactions:
        result = await score_transaction(tx)
        results.append(result.dict())
    return {"results": results, "count": len(results)}

@app.get("/stats")
async def get_stats():
    """Get fraud statistics."""
    if transactions_df is None:
        return {"error": "No transaction data loaded"}
    
    total = len(transactions_df)
    fraud = transactions_df['is_fraud'].sum()
    
    return {
        "total_transactions": total,
        "fraud_count": int(fraud),
        "fraud_rate": round(fraud/total*100, 2),
        "unique_users": int(transactions_df['user_id'].nunique()),
        "unique_merchants": int(transactions_df['merchant'].nunique())
    }

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 FRAUD DETECTION API")
    print("="*60)
    print("📋 Endpoints:")
    print("   POST /score        - Score a transaction")
    print("   POST /score/batch  - Score multiple transactions")
    print("   GET  /stats        - Get fraud statistics")
    print("   GET  /             - Health check")
    print("="*60)
    print("🌐 API Docs: http://localhost:8002/docs")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8002)
