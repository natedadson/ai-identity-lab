"""
IDENTITY RISK SCORING MODEL
Trains a machine learning model to predict risky access assignments.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

print("="*50)
print("IDENTITY RISK SCORING MODEL")
print("="*50)

# Load features
print("\n📂 Loading features...")
df = pd.read_csv("01-identity-risk-scoring/data/features.csv")
print(f"   Shape: {df.shape}")
print(f"   Risky assignments: {df['is_risky'].sum()} ({df['is_risky'].mean()*100:.1f}%)")

# Prepare features for ML
print("\n🔧 Preparing features...")

# Define which columns to use as features (NUMERIC ONLY)
feature_cols = [
    'risk_score_numeric',    # Already numeric: 1,2,3,4
    'never_used',            # Already numeric: 0 or 1
    'is_direct_grant',       # Already numeric: 0 or 1
    'tenure_days',           # Already numeric: days
    'days_since_last_use',   # Already numeric: days or -1
    'is_privileged_role'     # Already numeric: 0 or 1
]

# Add department columns (already one-hot encoded as 0/1)
dept_cols = [col for col in df.columns if col.startswith('dept_')]
feature_cols.extend(dept_cols)

# Ensure we only use columns that exist and are numeric
feature_cols = [col for col in feature_cols if col in df.columns]

# Convert to numeric (just to be safe) and fill any NaN with 0
X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
y = df['is_risky']

print(f"   Features: {len(feature_cols)}")
print(f"   Feature columns: {feature_cols[:6]}...")
print(f"   Data types verified: all numeric ✓")

# Split into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n📊 Train size: {len(X_train)}, Test size: {len(X_test)}")
print(f"   Training risk rate: {y_train.mean()*100:.1f}%")
print(f"   Test risk rate: {y_test.mean()*100:.1f}%")

# Scale features (helps model performance)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest model
print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,      # 100 decision trees
    max_depth=10,          # Limit tree depth (prevents overfitting)
    min_samples_split=10,  # Minimum samples to split a node
    random_state=42,
    n_jobs=-1              # Use all CPU cores
)
model.fit(X_train_scaled, y_train)

# Evaluate
print("\n📈 Model Evaluation:")
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print(f"   Accuracy: {accuracy:.3f}")
print(f"   AUC-ROC: {auc:.3f}")
print(f"\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Safe', 'Risky']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\n   Confusion Matrix:")
print(f"   True Safe: {cm[0,0]}, False Risky: {cm[0,1]}")
print(f"   False Safe: {cm[1,0]}, True Risky: {cm[1,1]}")

# Feature importance (what drives risk decisions)
print("\n🔍 TOP 10 MOST IMPORTANT FEATURES:")
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(importance_df.head(10).to_string(index=False))

# Save model and scaler
print("\n💾 Saving model...")
import os
os.makedirs("01-identity-risk-scoring/models", exist_ok=True)
joblib.dump(model, "01-identity-risk-scoring/models/risk_scorer.pkl")
joblib.dump(scaler, "01-identity-risk-scoring/models/scaler.pkl")
print("   ✅ Saved to 01-identity-risk-scoring/models/")

# Simple test prediction
print("\n🧪 Test prediction on a sample:")
sample = X_test.iloc[0:1]
sample_scaled = scaler.transform(sample)
pred = model.predict(sample_scaled)[0]
proba = model.predict_proba(sample_scaled)[0]
print(f"   Actual: {'Risky' if y_test.iloc[0] == 1 else 'Safe'}")
print(f"   Predicted: {'Risky' if pred == 1 else 'Safe'}")
print(f"   Risk probability: {proba[1]:.2f}")

print("\n" + "="*50)
print("✅ MODEL TRAINING COMPLETE!")
print("="*50)
