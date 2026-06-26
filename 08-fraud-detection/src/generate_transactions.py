"""
Synthetic Transaction Generator for Fraud Detection
Creates realistic banking transactions with fraud patterns.
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

class TransactionGenerator:
    """
    Generates synthetic banking transactions with fraud patterns.
    
    Fraud Patterns:
    1. Large transaction amounts (> $50,000)
    2. Rapid succession of small transactions (structuring)
    3. Transactions to high-risk countries
    4. Unusual transaction frequency for a user
    5. Money mule rings (networked fraud)
    """
    
    def __init__(self):
        self.locations = [
            "Toronto", "New York", "London", "Paris", "Tokyo",
            "Dubai", "Singapore", "Sydney", "Zurich", "Hong Kong",
            "Lagos", "Moscow", "Shanghai", "Istanbul", "Mexico City"
        ]
        self.high_risk_locations = ["Lagos", "Moscow", "Mexico City", "Istanbul"]
        
        self.transaction_types = [
            "ACH", "Wire", "Credit Card", "ATM", "Online",
            "Bill Payment", "Interac", "Check", "Direct Deposit"
        ]
        
        self.merchants = [
            "Amazon", "Walmart", "Target", "Best Buy", "Home Depot",
            "Uber", "Netflix", "Spotify", "Apple", "Google",
            "Canadian Tire", "Sobeys", "Loblaws", "Costco", "Starbucks"
        ]
        
        self.high_risk_merchants = [
            "Crypto Exchange Ltd", "Online Casino", "FX Trading Inc",
            "Offshore Investment", "Digital Wallet Pro"
        ]
        
        self.users = []
    
    def generate_user(self, user_id):
        """Generate a user with behavioral profile."""
        location = random.choice(self.locations)
        
        return {
            "user_id": f"user_{user_id:04d}",
            "location": location,
            "account_age_days": random.randint(30, 3650),
            "avg_transaction_amount": random.randint(100, 10000),
            "monthly_transactions": random.randint(5, 50),
            "is_fraudster": random.random() < 0.01,  # 1% are fraudsters
            "money_mule_id": None  # Assigned later
        }
    
    def generate_transactions(self, users, days=90, fraud_rate=0.05):
        """Generate transaction history for users."""
        print("📊 Generating transaction data...")
        
        transactions = []
        fraud_count = 0
        
        # Generate money mule networks
        mule_rings = self._create_mule_rings(users, 3)  # 3 rings
        
        for user in users:
            user_id = user['user_id']
            location = user['location']
            avg_amount = user['avg_transaction_amount']
            monthly_tx = user['monthly_transactions']
            is_fraudster = user['is_fraudster']
            mule_id = user['money_mule_id']
            
            # Determine if this user is a money mule
            is_mule = mule_id is not None
            
            # Generate transactions for each day
            for day in range(days):
                date = datetime.now() - timedelta(days=days-day)
                
                # Number of transactions per day
                num_tx = np.random.poisson(monthly_tx / 30)
                num_tx = min(num_tx, 10)  # Cap at 10/day
                
                for _ in range(num_tx):
                    # Determine if this transaction is fraudulent
                    is_fraud = False
                    
                    # Random fraud flag (fraud_rate)
                    if random.random() < fraud_rate:
                        is_fraud = True
                        fraud_count += 1
                    
                    # Force fraud for fraudsters
                    if is_fraudster:
                        is_fraud = True
                        fraud_count += 1
                    
                    # Force fraud for mules
                    if is_mule and random.random() < 0.3:
                        is_fraud = True
                        fraud_count += 1
                    
                    # Transaction amount
                    if is_fraud:
                        # Fraudulent transactions are often larger or structured
                        if random.random() < 0.3:
                            # Large transaction
                            amount = avg_amount * random.uniform(5, 20)
                        else:
                            # Small transaction (structuring)
                            amount = avg_amount * random.uniform(0.1, 0.5)
                    else:
                        amount = avg_amount * random.uniform(0.5, 2.0)
                    
                    # Location
                    if is_fraud and random.random() < 0.4:
                        tx_location = random.choice(self.high_risk_locations)
                    else:
                        tx_location = location
                    
                    # Merchant
                    if is_fraud and random.random() < 0.3:
                        merchant = random.choice(self.high_risk_merchants)
                    else:
                        merchant = random.choice(self.merchants)
                    
                    transactions.append({
                        "transaction_id": f"tx_{len(transactions):08d}",
                        "user_id": user_id,
                        "timestamp": date.replace(
                            hour=random.randint(0, 23),
                            minute=random.randint(0, 59)
                        ).isoformat(),
                        "amount": round(amount, 2),
                        "location": tx_location,
                        "merchant": merchant,
                        "transaction_type": random.choice(self.transaction_types),
                        "is_fraud": int(is_fraud),
                        "is_mule": int(is_mule),
                        "mule_ring_id": mule_id if is_mule else None
                    })
        
        df = pd.DataFrame(transactions)
        
        # Calculate additional features
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        
        # Save data
        os.makedirs("08-fraud-detection/data", exist_ok=True)
        df.to_csv("08-fraud-detection/data/transactions.csv", index=False)
        
        # Save user profiles
        with open("08-fraud-detection/data/user_profiles.json", 'w') as f:
            json.dump(users, f, indent=2)
        
        # Save mule rings
        with open("08-fraud-detection/data/mule_rings.json", 'w') as f:
            json.dump(mule_rings, f, indent=2)
        
        print(f"\n   ✅ Generated {len(df)} transactions")
        print(f"   📊 Fraud rate: {fraud_count/len(df)*100:.2f}%")
        print(f"   👥 Users: {df['user_id'].nunique()}")
        print(f"   🕸️ Mule rings: {len(mule_rings)}")
        
        return df
    
    def _create_mule_rings(self, users, num_rings):
        """Create money mule networks."""
        mule_rings = []
        
        # Find users eligible to be mules (non-fraudsters)
        eligible_users = [u for u in users if not u['is_fraudster']]
        
        if len(eligible_users) < num_rings * 3:
            return mule_rings
        
        for ring_id in range(num_rings):
            # Select ring members (3-5 per ring)
            ring_size = random.randint(3, 5)
            ring_members = random.sample(eligible_users, ring_size)
            
            ring = {
                "ring_id": f"ring_{ring_id:03d}",
                "members": [u['user_id'] for u in ring_members],
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "total_fraud_amount": 0
            }
            
            # Assign mule IDs to users
            for member in ring_members:
                member['money_mule_id'] = ring['ring_id']
            
            mule_rings.append(ring)
        
        return mule_rings


if __name__ == "__main__":
    generator = TransactionGenerator()
    
    # Generate users
    print("👥 Generating users...")
    users = [generator.generate_user(i) for i in range(500)]
    print(f"   ✅ Generated {len(users)} users")
    
    # Generate transactions
    df = generator.generate_transactions(users, days=90, fraud_rate=0.05)
    
    print("\n✅ Transaction data saved to 08-fraud-detection/data/")
    print("   - transactions.csv")
    print("   - user_profiles.json")
    print("   - mule_rings.json")
