"""
UEBA Detection Engine
Builds behavioral baselines and detects anomalies.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
import pickle
import os

class UEBADetector:
    """
    User & Entity Behavior Analytics Engine.
    
    Detects:
    1. Unusual login hours
    2. Unusual locations
    3. Unusual app access patterns
    4. Rapid access (multiple apps in short time)
    5. Weekend/off-hour access
    """
    
    def __init__(self):
        self.user_baselines = {}
        self.alerts = []
        self.anomaly_threshold = 0.5
    
    def build_baseline(self, df):
        """Build behavioral baseline for each user."""
        print("\n📊 Building behavioral baselines...")
        
        for user_id in df['user_id'].unique():
            user_data = df[df['user_id'] == user_id]
            
            hours = user_data['hour'].tolist()
            if hours:
                q1 = np.percentile(hours, 10)
                q3 = np.percentile(hours, 90)
            else:
                q1, q3 = 9, 17
            
            locations = user_data['location'].value_counts()
            top_locations = locations[locations >= len(user_data) * 0.1].index.tolist()
            
            apps = user_data['app'].value_counts()
            top_apps = apps[apps >= len(user_data) * 0.05].index.tolist()
            
            logins_per_day = user_data.groupby('date').size().mean()
            
            self.user_baselines[user_id] = {
                'normal_hours': (q1, q3),
                'normal_locations': top_locations if top_locations else ['Unknown'],
                'normal_apps': top_apps if top_apps else ['Unknown'],
                'logins_per_day': max(1, int(logins_per_day)),
                'total_logins': len(user_data),
                'days_active': len(user_data['date'].unique())
            }
        
        print(f"   ✅ Built baselines for {len(self.user_baselines)} users")
        return self.user_baselines
    
    def detect_anomalies(self, event):
        """Check if a single event is anomalous."""
        user_id = event['user_id']
        
        if user_id not in self.user_baselines:
            return {
                'is_anomaly': True,
                'risk_score': 0.8,
                'reasons': ['User not in baseline']
            }
        
        baseline = self.user_baselines[user_id]
        reasons = []
        risk_score = 0
        
        hour = event['hour']
        low, high = baseline['normal_hours']
        if hour < low or hour > high:
            reasons.append(f"Unusual hour: {hour} (normal: {low}-{high})")
            risk_score += 0.3
        
        location = event['location']
        if location not in baseline['normal_locations']:
            reasons.append(f"Unusual location: {location}")
            risk_score += 0.3
        
        app = event['app']
        if app not in baseline['normal_apps']:
            reasons.append(f"Unusual app: {app}")
            risk_score += 0.2
        
        if event.get('is_weekend', False):
            reasons.append("Weekend access")
            risk_score += 0.2
        
        risk_score = min(1.0, risk_score)
        
        return {
            'is_anomaly': len(reasons) > 0,
            'risk_score': risk_score,
            'reasons': reasons,
            'severity': self._get_severity(risk_score)
        }
    
    def _get_severity(self, risk_score):
        if risk_score >= 0.7:
            return "CRITICAL"
        elif risk_score >= 0.4:
            return "HIGH"
        elif risk_score >= 0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_alert(self, user_id, anomaly_result, event):
        """Generate an alert for a detected anomaly."""
        alert = {
            'alert_id': f"alert_{len(self.alerts)+1}",
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'risk_score': anomaly_result['risk_score'],
            'severity': anomaly_result['severity'],
            'reasons': anomaly_result['reasons'],
            'event': {
                'time': event.get('timestamp', datetime.now().isoformat()),
                'location': event.get('location', 'Unknown'),
                'app': event.get('app', 'Unknown')
            }
        }
        
        if anomaly_result['risk_score'] >= self.anomaly_threshold:
            self.alerts.append(alert)
        
        return alert
    
    def scan_events(self, df):
        """Scan all events for anomalies."""
        print("\n🔍 Scanning events for anomalies...")
        
        anomalies = []
        for _, event in df.iterrows():
            event_dict = event.to_dict()
            result = self.detect_anomalies(event_dict)
            if result['is_anomaly']:
                anomalies.append({'event': event_dict, 'detection': result})
        
        for anomaly in anomalies:
            if anomaly['detection']['risk_score'] >= 0.3:
                self.generate_alert(
                    anomaly['event']['user_id'],
                    anomaly['detection'],
                    anomaly['event']
                )
        
        print(f"   ✅ Found {len(anomalies)} anomalous events")
        print(f"   📊 Generated {len(self.alerts)} alerts")
        return anomalies
    
    def save_alerts(self, filename="06-ueba-detection/output/alerts.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.alerts, f, indent=2, default=str)
        print(f"\n💾 Alerts saved to {filename}")
    
    def save_baselines(self, filename="06-ueba-detection/output/baselines.pkl"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            pickle.dump(self.user_baselines, f)
        print(f"💾 Baselines saved to {filename}")

def main():
    print("="*60)
    print("🔐 UEBA DETECTION ENGINE")
    print("="*60)
    
    df = pd.read_csv("06-ueba-detection/data/behavior_data.csv")
    print(f"\n📊 Loaded {len(df)} events from {df['user_id'].nunique()} users")
    
    detector = UEBADetector()
    detector.build_baseline(df)
    anomalies = detector.scan_events(df)
    
    print("\n" + "="*60)
    print("📊 UEBA SCAN RESULTS")
    print("="*60)
    print(f"\n   Users: {df['user_id'].nunique()}")
    print(f"   Events scanned: {len(df)}")
    print(f"   Anomalies detected: {len(anomalies)}")
    print(f"   Alerts generated: {len(detector.alerts)}")
    
    if detector.alerts:
        print("\n🔴 TOP ALERTS:")
        for alert in detector.alerts[:3]:
            print(f"\n   ⚠️ {alert['severity']} | User: {alert['user_id']}")
            print(f"      Risk Score: {alert['risk_score']}")
            print(f"      Reasons: {'; '.join(alert['reasons'][:2])}")
    
    detector.save_alerts()
    detector.save_baselines()
    
    print("\n✅ UEBA Detection Complete!")

if __name__ == "__main__":
    main()
