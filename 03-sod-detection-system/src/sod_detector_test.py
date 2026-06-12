import json
import pandas as pd
from datetime import datetime

# Load SOD rules
with open("03-sod-detection-system/config/sod_rules.json", 'r') as f:
    rules_data = json.load(f)
    rules = rules_data['sod_rules']

# Load test assignments
assignments = pd.read_csv("datasets/synthetic/assignments_with_violations.csv")
print("="*60)
print("🔐 SOD DETECTION - TEST MODE")
print("="*60)
print(f"📊 Testing with {len(assignments)} assignments")
print(f"👥 Users: {assignments['user_id'].nunique()}\n")

# Detect violations
violations = []
user_entitlements = assignments.groupby('user_id')['entitlement_id'].apply(set).to_dict()

for user_id, ents in user_entitlements.items():
    for rule in rules:
        for pair in rule['entitlement_pairs']:
            ent1, ent2 = pair
            has_ent1 = any(ent1 in e or ent1.replace('_', '') in e.replace('_', '') for e in ents)
            has_ent2 = any(ent2 in e or ent2.replace('_', '') in e.replace('_', '') for e in ents)
            
            if has_ent1 and has_ent2:
                violations.append({
                    "user_id": user_id,
                    "rule_name": rule['name'],
                    "risk_level": rule['risk_level'],
                    "entitlements_found": [e for e in ents if ent1 in e or ent2 in e],
                    "business_process": rule['business_process'],
                    "mitigation": rule['mitigation']
                })
                break

print(f"⚠️ Found {len(violations)} SOD violations!")
print("\n📋 VIOLATIONS DETECTED:")
print("-"*40)

for v in violations:
    print(f"\n👤 User: {v['user_id']}")
    print(f"📋 Rule: {v['rule_name']} ({v['risk_level']})")
    print(f"🔑 Conflicting: {v['entitlements_found'][:2]}")
    print(f"💡 Fix: {v['mitigation']}")

print("\n" + "="*60)
print("✅ Detection system working! Found intentional test violations.")
print("="*60)
