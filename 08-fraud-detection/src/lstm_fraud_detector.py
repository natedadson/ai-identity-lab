"""
LSTM Fraud Detection Model (Optional - uses scikit-learn fallback)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import json
import os

class FraudDetector:
    """
    Fraud detection using Random Forest (works without TensorFlow).
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def prepare_features(self, df):
        """Prepare features for training."""
        print("\n🔧 Preparing features...")
        
        # Feature engineering
        df['amount_log'] = np.log1p(df['amount'])
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        
        # Select features
        feature_cols = ['amount', 'amount_log', 'hour', 'day_of_week']
        X = df[feature_cols].values
        y = df['is_fraud'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"   Features: {X.shape[1]}")
        print(f"   Samples: {X.shape[0]}")
        print(f"   Fraud rate: {y.mean()*100:.2f}%")
        
        return X_scaled, y
    
    def train(self, X, y):
        """Train Random Forest model."""
        print("\n🤖 Training Random Forest model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy: {self.model.score(X_test, y_test):.4f}")
        print(f"   AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")
        print(f"\n   Classification Report:")
        print(classification_report(y_test, y_pred))
        
        return self.model
    
    def save_model(self, path="08-fraud-detection/models/fraud_model"):
        """Save model and scaler."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, f"{path}.pkl")
        joblib.dump(self.scaler, f"{path}_scaler.pkl")
        print(f"\n💾 Model saved to {path}.pkl")
    
    def load_model(self, path="08-fraud-detection/models/fraud_model"):
        """Load model and scaler."""
        self.model = joblib.load(f"{path}.pkl")
        self.scaler = joblib.load(f"{path}_scaler.pkl")
        print(f"\n📂 Model loaded from {path}.pkl")
        return self.model


def main():
    print("="*60)
    print("🔐 FRAUD DETECTION MODEL (Random Forest)")
    print("="*60)
    
    # Load data
    df = pd.read_csv("08-fraud-detection/data/transactions.csv")
    print(f"\n📊 Loaded {len(df)} transactions")
    print(f"   Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
    
    # Initialize detector
    detector = FraudDetector()
    
    # Prepare features
    X, y = detector.prepare_features(df)
    
    # Train model
    detector.train(X, y)
    
    # Save model
    detector.save_model()
    
    print("\n" + "="*60)
    print("✅ Fraud Detection Model Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
