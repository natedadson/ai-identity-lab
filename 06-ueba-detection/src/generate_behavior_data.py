"""
Generate synthetic user behavior data for UEBA testing.
Creates realistic login patterns, access logs, and anomalies.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

class BehaviorDataGenerator:
    """
    Generates synthetic user behavior data.
    Includes normal patterns + intentional anomalies.
    """
    
    def __init__(self):
        self.users = []
        self.apps = [
            "Salesforce", "Workday", "AWS Console", "GitHub",
            "Jira", "Confluence", "Slack", "Zoom",
            "Google Workspace", "Azure Portal", "ServiceNow", "SAP"
        ]
        self.locations = ["Toronto", "New York", "London", "Remote", "Chicago", "Austin"]
        self.departments = ["Finance", "Engineering", "Sales", "HR", "IT", "Executive"]
        
        # Normal hours (9am-5pm)
        self.work_start = 9
        self.work_end = 17
    
    def generate_user(self, user_id):
        """Generate a user with baseline behavior."""
        dept = random.choice(self.departments)
        location = random.choice(self.locations)
        
        return {
            "user_id": f"user_{user_id:04d}",
            "department": dept,
            "location": location,
            "role": random.choice(["Analyst", "Manager", "Admin", "Engineer", "Executive"]),
            "tenure_days": random.randint(30, 2000),
            "normal_login_hours": (self.work_start + random.randint(-1, 1),
                                   self.work_end + random.randint(-1, 1)),
            "normal_locations": [location],
            "common_apps": random.sample(self.apps, random.randint(3, 8)),
            "risk_score": random.uniform(0, 0.3)
        }
    
    def generate_login_events(self, user, days=30):
        """Generate login events for a user."""
        events = []
        user_id = user['user_id']
        location = user['location']
        start_hour, end_hour = user['normal_login_hours']
        
        for day in range(days):
            date = datetime.now() - timedelta(days=days-day)
            
            num_logins = random.randint(1, 5)
            
            for _ in range(num_logins):
                if random.random() < 0.85:
                    hour = random.randint(start_hour, end_hour)
                else:
                    hour = random.randint(0, 23)
                
                if random.random() < 0.9:
                    loc = location
                else:
                    loc = random.choice(self.locations)
                
                events.append({
                    "user_id": user_id,
                    "timestamp": date.replace(hour=hour, minute=random.randint(0, 59)).isoformat(),
                    "location": loc,
                    "app": random.choice(user['common_apps'] if random.random() < 0.7 else self.apps),
                    "hour": hour,
                    "date": date.strftime("%Y-%m-%d"),
                    "is_weekend": date.weekday() >= 5
                })
        
        return events
    
    def add_anomalies(self, events):
        """Add intentional anomalies for testing."""
        anomalies = []
        
        # Select 5% of users for anomalies
        users = list(set([e['user_id'] for e in events]))
        anomaly_users = random.sample(users, max(1, int(len(users) * 0.05)))
        
        for user_id in anomaly_users:
            # Anomaly 1: 3am login from different country
            anomaly1 = {
                "user_id": user_id,
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 5))).replace(hour=3).isoformat(),
                "location": random.choice(["Shanghai", "Moscow", "Dubai"]),
                "app": random.choice(self.apps),
                "hour": 3,
                "date": (datetime.now() - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
                "is_weekend": False,
                "is_anomaly": True,
                "anomaly_type": "unusual_hour_location"
            }
            anomalies.append(anomaly1)
            
            # Anomaly 2: Rapid access to 5+ apps in 10 minutes
            for i in range(5):
                anomaly2 = {
                    "user_id": user_id,
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 3), minutes=i*2)).isoformat(),
                    "location": random.choice([user['location'] for user in self.users if user['user_id'] == user_id] or ["Toronto"]),
                    "app": random.choice(self.apps),
                    "hour": random.randint(10, 15),
                    "date": (datetime.now() - timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d"),
                    "is_weekend": False,
                    "is_anomaly": True,
                    "anomaly_type": "rapid_access"
                }
                anomalies.append(anomaly2)
        
        return events + anomalies
    
    def generate_dataset(self, n_users=100, days=30):
        """Generate complete behavioral dataset."""
        print("📊 Generating UEBA dataset...")
        
        # Generate users
        self.users = [self.generate_user(i) for i in range(n_users)]
        print(f"   ✅ Generated {len(self.users)} users")
        
        # Generate events
        all_events = []
        for user in self.users:
            events = self.generate_login_events(user, days)
            all_events.extend(events)
        
        print(f"   ✅ Generated {len(all_events)} normal events")
        
        # Add anomalies
        all_events = self.add_anomalies(all_events)
        
        df = pd.DataFrame(all_events)
        
        # Add labels for evaluation
        df['is_anomaly'] = df.get('is_anomaly', False)
        df['anomaly_type'] = df.get('anomaly_type', 'normal')
        
        # Ensure data directory exists
        os.makedirs("06-ueba-detection/data", exist_ok=True)
        
        # Save to CSV
        df.to_csv("06-ueba-detection/data/behavior_data.csv", index=False)
        
        # Save user profiles
        with open("06-ueba-detection/data/user_profiles.json", 'w') as f:
            json.dump(self.users, f, indent=2)
        
        anomaly_count = df['is_anomaly'].sum()
        print(f"\n   📊 Dataset Summary:")
        print(f"      Total events: {len(df)}")
        print(f"      Anomalies: {anomaly_count} ({anomaly_count/len(df)*100:.1f}%)")
        print(f"      Users: {df['user_id'].nunique()}")
        print(f"      Apps: {df['app'].nunique()}")
        print(f"      Locations: {df['location'].nunique()}")
        
        return df

if __name__ == "__main__":
    generator = BehaviorDataGenerator()
    df = generator.generate_dataset(n_users=100, days=30)
    print("\n✅ Dataset saved to 06-ueba-detection/data/")
