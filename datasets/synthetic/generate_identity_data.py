#!/usr/bin/env python3
"""
SYNTHETIC IDENTITY DATA GENERATOR
For: AI-Native Identity Security Research Lab
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()
np.random.seed(42)
random.seed(42)

class IdentityDataGenerator:
    def __init__(self):
        self.departments = ["Finance", "Sales", "Engineering", "Human Resources", "Legal", "Information Technology", "Marketing", "Operations", "Executive", "Customer Support", "R&D", "Product"]
        
        self.role_entitlements = {
            "Finance Analyst": ["view_transactions", "create_reports", "edit_budgets"],
            "Finance Manager": ["approve_budgets", "view_all_transactions", "finance_reports"],
            "Sales Rep": ["view_customers", "create_quotes", "view_pricing"],
            "Sales Manager": ["approve_discounts", "view_team_quota", "sales_forecasts"],
            "Software Engineer": ["view_code", "create_branches", "merge_pr", "view_logs"],
            "Senior Engineer": ["deploy_prod", "aws_console", "database_query"],
            "HR Specialist": ["view_employee_data", "process_payroll", "view_candidates"],
            "HR Manager": ["approve_hiring", "salary_reviews", "hr_reports"],
            "IT Support": ["reset_passwords", "unlock_accounts", "view_tickets"],
            "Security Analyst": ["view_logs", "security_alerts", "incident_response"],
            "Security Engineer": ["configure_firewall", "iam_policies", "vulnerability_scan"],
            "Compliance Officer": ["audit_logs", "sod_reports", "access_reviews"],
            "Executive": ["all_reports", "approve_strategy", "view_all_data"],
            "Admin": ["user_management", "role_management", "system_config", "all_access"]
        }
        
        self.applications = ["Salesforce", "Workday", "AWS", "GitHub", "Jira", "Confluence", "Slack", "Zoom", "Google Workspace", "Azure", "ServiceNow", "SAP"]
        
        self.sod_pairs = [("create_vendor", "approve_payment"), ("create_user", "delete_user"), ("view_salary", "edit_salary"), ("approve_purchase", "receive_goods")]
    
    def generate_users(self, n_users=1000):
        print(f"📝 Generating {n_users} users...")
        users = []
        for i in range(n_users):
            dept = random.choice(self.departments)
            if dept == "Finance":
                role = random.choice(["Finance Analyst", "Finance Manager"])
            elif dept == "Sales":
                role = random.choice(["Sales Rep", "Sales Manager"])
            elif dept in ["Engineering", "R&D"]:
                role = random.choice(["Software Engineer", "Senior Engineer"])
            elif dept == "Information Technology":
                role = random.choice(["IT Support", "Security Analyst", "Security Engineer"])
            elif dept == "Human Resources":
                role = random.choice(["HR Specialist", "HR Manager"])
            elif dept == "Executive":
                role = "Executive"
            else:
                role = random.choice(["Analyst", "Specialist"])
            
            days_employed = random.randint(0, 2000)
            hire_date = datetime.now() - timedelta(days=days_employed)
            
            user = {
                "user_id": f"user_{i:04d}",
                "email": fake.email(),
                "name": fake.name(),
                "department": dept,
                "role": role,
                "manager_id": None if i < 5 else f"user_{random.randint(0, n_users-1):04d}",
                "hire_date": hire_date.strftime("%Y-%m-%d"),
                "tenure_days": days_employed,
                "is_active": random.random() > 0.05,
                "location": random.choice(["Toronto", "New York", "London", "Remote"])
            }
            users.append(user)
        
        df = pd.DataFrame(users)
        df.to_csv("datasets/synthetic/users.csv", index=False)
        print(f"   ✅ Saved to datasets/synthetic/users.csv")
        return df
    
    def generate_entitlements(self, n_entitlements=200):
        print(f"🔐 Generating {n_entitlements} entitlements...")
        entitlements = []
        risk_levels = ["Low", "Medium", "High", "Critical"]
        
        for i in range(n_entitlements):
            app = random.choice(self.applications)
            action = random.choice(["read", "write", "delete", "admin", "view", "edit", "approve"])
            resource = random.choice(["users", "reports", "data", "config", "security"])
            
            if action in ["admin", "delete"]:
                risk = "Critical"
            elif action in ["write", "edit", "approve"]:
                risk = "High"
            else:
                risk = random.choice(risk_levels)
            
            entitlement = {
                "entitlement_id": f"ent_{i:03d}",
                "name": f"{app}.{action}.{resource}",
                "description": f"Allows {action} access to {resource} in {app}",
                "application": app,
                "risk_level": risk,
                "risk_score": {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}[risk],
                "is_privileged": risk in ["High", "Critical"]
            }
            entitlements.append(entitlement)
        
        df = pd.DataFrame(entitlements)
        df.to_csv("datasets/synthetic/entitlements.csv", index=False)
        print(f"   ✅ Saved to datasets/synthetic/entitlements.csv")
        return df
    
    def generate_assignments(self, users_df, entitlements_df):
        print(f"🔗 Generating assignments...")
        assignments = []
        assignment_id = 0
        
        role_ent_map = {}
        for role, default_ents in self.role_entitlements.items():
            matched_ents = []
            for default_ent in default_ents:
                matches = entitlements_df[entitlements_df['name'].str.contains(default_ent, case=False, na=False)]
                matched_ents.extend(matches['entitlement_id'].tolist())
            role_ent_map[role] = list(set(matched_ents))[:5]
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            role = user['role']
            tenure_days = user['tenure_days']
            
            assigned_ents = set()
            if role in role_ent_map:
                assigned_ents.update(role_ent_map[role])
            
            extra_count = min(int(tenure_days / 365), 8)
            if extra_count > 0:
                extra_ents = entitlements_df.sample(n=min(extra_count, len(entitlements_df)))
                assigned_ents.update(extra_ents['entitlement_id'].tolist())
            
            for ent_id in assigned_ents:
                ent_info = entitlements_df[entitlements_df['entitlement_id'] == ent_id].iloc[0]
                
                if random.random() < 0.2:
                    last_used = None
                    days_since_used = -1
                else:
                    days_since_used = random.randint(1, 90)
                    last_used = datetime.now() - timedelta(days=days_since_used)
                
                assignment = {
                    "assignment_id": f"assign_{assignment_id:06d}",
                    "user_id": user_id,
                    "entitlement_id": ent_id,
                    "grant_date": (datetime.now() - timedelta(days=random.randint(1, max(tenure_days, 1)))).strftime("%Y-%m-%d"),
                    "last_used": last_used.strftime("%Y-%m-%d") if last_used else None,
                    "days_since_last_use": days_since_used,
                    "source": random.choice(["role_assignment", "direct_grant", "auto_provisioned"]),
                    "is_active_assignment": user['is_active'],
                    "entitlement_risk": ent_info['risk_level']
                }
                assignments.append(assignment)
                assignment_id += 1
        
        df = pd.DataFrame(assignments)
        df.to_csv("datasets/synthetic/assignments.csv", index=False)
        print(f"   ✅ Generated {len(assignments)} assignments")
        return df

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 SYNTHETIC IDENTITY DATA GENERATOR")
    print("="*50 + "\n")
    
    generator = IdentityDataGenerator()
    users = generator.generate_users(1000)
    entitlements = generator.generate_entitlements(200)
    assignments = generator.generate_assignments(users, entitlements)
    
    print("\n" + "="*50)
    print("📊 GENERATION COMPLETE!")
    print("="*50)
    print(f"✅ Users: {len(users)}")
    print(f"✅ Entitlements: {len(entitlements)}")
    print(f"✅ Assignments: {len(assignments)}")
    print("\n📁 Location: datasets/synthetic/")
    print("="*50 + "\n")


