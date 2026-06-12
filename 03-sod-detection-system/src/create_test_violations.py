"""
Create test SOD violations to validate detection system
Adds intentional conflicting entitlements to test users.
"""

import pandas as pd
import random
from datetime import datetime

# Load current assignments
df = pd.read_csv("datasets/synthetic/assignments.csv")
print(f"📊 Original assignments: {len(df)}")

# Create test violations by adding conflicting entitlements
test_violations = [
    {
        "user_id": "user_0001",
        "entitlement_1": "create_vendor",
        "entitlement_2": "approve_payment",
        "rule": "Vendor Management Fraud"
    },
    {
        "user_id": "user_0002", 
        "entitlement_1": "view_salary",
        "entitlement_2": "edit_salary",
        "rule": "Payroll Fraud"
    },
    {
        "user_id": "user_0003",
        "entitlement_1": "create_user", 
        "entitlement_2": "delete_user",
        "rule": "Account Management Abuse"
    },
    {
        "user_id": "user_0004",
        "entitlement_1": "approve_purchase",
        "entitlement_2": "receive_goods",
        "rule": "Procurement Fraud"
    },
    {
        "user_id": "user_0005",
        "entitlement_1": "submit_expense",
        "entitlement_2": "approve_expense",
        "rule": "Expense Reimbursement Fraud"
    }
]

# Create new assignments for test violations
new_assignments = []
current_max_id = df['assignment_id'].str.extract('(\d+)').astype(int).max().values[0]

for i, violation in enumerate(test_violations, 1):
    new_assignments.append({
        "assignment_id": f"assign_{current_max_id + i:06d}",
        "user_id": violation["user_id"],
        "entitlement_id": violation["entitlement_1"],
        "grant_date": datetime.now().strftime("%Y-%m-%d"),
        "last_used": datetime.now().strftime("%Y-%m-%d"),
        "days_since_last_use": 1,
        "source": "direct_grant",
        "is_active_assignment": True,
        "entitlement_risk": "Critical"
    })
    new_assignments.append({
        "assignment_id": f"assign_{current_max_id + i + 5:06d}",
        "user_id": violation["user_id"],
        "entitlement_id": violation["entitlement_2"],
        "grant_date": datetime.now().strftime("%Y-%m-%d"),
        "last_used": datetime.now().strftime("%Y-%m-%d"),
        "days_since_last_use": 1,
        "source": "direct_grant",
        "is_active_assignment": True,
        "entitlement_risk": "Critical"
    })

# Add to DataFrame
new_df = pd.DataFrame(new_assignments)
combined_df = pd.concat([df, new_df], ignore_index=True)

# Save
combined_df.to_csv("datasets/synthetic/assignments_with_violations.csv", index=False)
print(f"✅ Added {len(new_assignments)} test violation assignments")
print(f"📊 New total assignments: {len(combined_df)}")
print("\n📋 Test violations added:")
for v in test_violations:
    print(f"   • {v['user_id']}: {v['rule']}")
