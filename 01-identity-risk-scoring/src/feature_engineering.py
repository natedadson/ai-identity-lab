"""
FEATURE ENGINEERING FOR IDENTITY RISK SCORING
Converts raw identity data into ML-ready features.
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*50)
print("FEATURE ENGINEERING PIPELINE")
print("="*50)

# Load the data
print("\n📂 Loading data...")
users = pd.read_csv("datasets/synthetic/users.csv")
entitlements = pd.read_csv("datasets/synthetic/entitlements.csv")
assignments = pd.read_csv("datasets/synthetic/assignments.csv")
print(f"   Users: {len(users)}, Entitlements: {len(entitlements)}, Assignments: {len(assignments)}")

# Parse dates
users['hire_date'] = pd.to_datetime(users['hire_date'])
assignments['grant_date'] = pd.to_datetime(assignments['grant_date'])
if 'last_used' in assignments.columns:
    assignments['last_used'] = pd.to_datetime(assignments['last_used'])

# Merge all data into one table
print("\n🔗 Merging data...")
df = assignments.merge(users, on='user_id')
df = df.merge(entitlements, on='entitlement_id')
print(f"   Shape: {df.shape}")

# Create features
print("\n🔧 Creating features...")

# Feature 1: Tenure in days
df['tenure_days'] = (datetime.now() - df['hire_date']).dt.days

# Feature 2: Days since last use
if 'last_used' in df.columns:
    df['days_since_last_use'] = (datetime.now() - df['last_used']).dt.days
    df['never_used'] = df['last_used'].isna().astype(int)
    df['days_since_last_use'] = df['days_since_last_use'].fillna(-1)
else:
    df['days_since_last_use'] = -1
    df['never_used'] = 0

# Feature 3: Direct grant indicator
df['is_direct_grant'] = (df['source'] == 'direct_grant').astype(int)

# Feature 4: Risk score numeric
risk_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
df['risk_score_numeric'] = df['risk_level'].map(risk_map)

# Feature 5: Is manager/senior role
df['is_privileged_role'] = df['role'].str.contains('Manager|Executive|Admin|Senior|Engineer', case=False).astype(int)

# Feature 6: Department (one-hot encoding for top departments)
top_depts = df['department'].value_counts().head(5).index.tolist()
for dept in top_depts:
    df[f'dept_{dept.replace(" ", "_")}'] = (df['department'] == dept).astype(int)

# Create target label (what we're trying to predict)
# An assignment is "risky" if:
# - Never used AND high/critical risk, OR
# - Direct grant AND critical risk, OR
# - Privileged role with never-used critical access
df['is_risky'] = (
    ((df['never_used'] == 1) & (df['risk_score_numeric'] >= 3)) |
    ((df['is_direct_grant'] == 1) & (df['risk_score_numeric'] >= 4)) |
    ((df['is_privileged_role'] == 1) & (df['never_used'] == 1) & (df['risk_score_numeric'] >= 3))
).astype(int)

print(f"   Total features: {len(df.columns)}")
print(f"   Risky assignments: {df['is_risky'].sum()} ({df['is_risky'].mean()*100:.1f}%)")

# Save features
df.to_csv("01-identity-risk-scoring/data/features.csv", index=False)
print(f"\n✅ Saved to 01-identity-risk-scoring/data/features.csv")

# Show feature preview
print("\n📋 Feature preview (first 5 rows):")
feature_cols = ['user_id', 'entitlement_id', 'risk_score_numeric', 'never_used', 
                'is_direct_grant', 'tenure_days', 'is_privileged_role', 'is_risky']
print(df[feature_cols].head())

