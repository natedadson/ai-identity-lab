"""
Role Mining Engine using Association Rule Mining
Discovers optimal groupings of entitlements that should be roles.
"""

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import json
from collections import Counter

class RoleMiner:
    """
    Discovers role candidates from user-entitlement assignments.
    """
    
    def __init__(self):
        self.frequent_itemsets = None
        self.rules = None
        self.role_candidates = []
    
    def load_data(self, assignments_path):
        """Load user-entitlement assignments."""
        df = pd.read_csv(assignments_path)
        print(f"📊 Loaded {len(df)} assignments")
        print(f"   Users: {df['user_id'].nunique()}")
        print(f"   Unique entitlements: {df['entitlement_id'].nunique()}")
        print(f"   Columns: {list(df.columns)}")
        return df
    
    def create_transactions(self, df):
        """Convert to market basket format."""
        transactions = df.groupby('user_id')['entitlement_id'].apply(list).tolist()
        
        print(f"\n📋 Created {len(transactions)} transactions")
        print(f"   Avg entitlements per user: {sum(len(t) for t in transactions)/len(transactions):.1f}")
        print(f"   Min entitlements: {min(len(t) for t in transactions)}")
        print(f"   Max entitlements: {max(len(t) for t in transactions)}")
        
        return transactions
    
    def analyze_risk_by_role(self, df):
        """Analyze risk levels associated with entitlement clusters."""
        print("\n📊 Analyzing risk patterns in entitlement clusters...")
        
        # Get entitlement risk levels
        ent_risk = df[['entitlement_id', 'entitlement_risk']].drop_duplicates()
        
        # Find most common entitlement pairs
        user_ents = df.groupby('user_id')['entitlement_id'].apply(set).tolist()
        
        pair_counts = Counter()
        for ents in user_ents:
            ents_list = list(ents)
            for i in range(len(ents_list)):
                for j in range(i+1, len(ents_list)):
                    pair = tuple(sorted([ents_list[i], ents_list[j]]))
                    pair_counts[pair] += 1
        
        # Create pairs DataFrame with risk info
        pairs_data = []
        for (e1, e2), count in pair_counts.most_common(20):
            risk1 = ent_risk[ent_risk['entitlement_id'] == e1]['entitlement_risk'].values
            risk2 = ent_risk[ent_risk['entitlement_id'] == e2]['entitlement_risk'].values
            pairs_data.append({
                "entitlement_1": e1,
                "entitlement_2": e2,
                "co_occurrence": count,
                "risk_1": risk1[0] if len(risk1) > 0 else "Unknown",
                "risk_2": risk2[0] if len(risk2) > 0 else "Unknown"
            })
        
        pairs_df = pd.DataFrame(pairs_data)
        
        if len(pairs_df) > 0:
            print("\n🔗 TOP ENTITLEMENT PAIRS (frequently co-occur):")
            for i, row in pairs_df.head(10).iterrows():
                risk_info = f"({row['risk_1']} + {row['risk_2']})"
                print(f"   {row['entitlement_1']} + {row['entitlement_2']}: {row['co_occurrence']} users {risk_info}")
        
        return pairs_df
    
    def generate_role_recommendations(self, df):
        """Generate practical role recommendations from the data."""
        print("\n🎯 GENERATING ROLE RECOMMENDATIONS")
        print("="*50)
        
        # Get entitlement clusters by risk level
        risk_groups = df.groupby('entitlement_risk')['entitlement_id'].agg(lambda x: list(set(x))).to_dict()
        
        print("\n📦 Entitlements by Risk Level:")
        for risk, ents in risk_groups.items():
            print(f"   {risk}: {len(ents)} entitlements")
        
        # Find users with similar entitlement sets
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Create user-entitlement matrix
        user_ent_dict = df.groupby('user_id')['entitlement_id'].apply(lambda x: ' '.join(x)).to_dict()
        user_list = list(user_ent_dict.keys())
        ent_strings = list(user_ent_dict.values())
        
        if len(user_list) > 1:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(ent_strings)
            similarity = cosine_similarity(tfidf_matrix)
            
            # Find similar user pairs
            similar_users = []
            for i in range(len(user_list)):
                for j in range(i+1, len(user_list)):
                    if similarity[i][j] > 0.5:  # Threshold for similarity
                        similar_users.append({
                            "user_1": user_list[i],
                            "user_2": user_list[j],
                            "similarity": round(similarity[i][j], 3)
                        })
            
            if similar_users:
                print(f"\n👥 Found {len(similar_users)} pairs of users with similar access patterns")
                print("   These users could share the same role definition")
        
        # Create role suggestions based on common entitlement patterns
        print("\n💡 ROLE SUGGESTIONS:")
        
        # Suggestion 1: Risk-based roles
        print("\n   1. Risk-Based Roles:")
        for risk in ['Critical', 'High', 'Medium', 'Low']:
            if risk in risk_groups:
                count = len(risk_groups[risk])
                if count > 0:
                    print(f"      - {risk}_Access_Role: {count} entitlements at {risk} risk level")
        
        # Suggestion 2: Most common entitlement combinations
        user_ents_list = df.groupby('user_id')['entitlement_id'].apply(set).tolist()
        
        # Find entitlement sets that appear in multiple users
        ent_set_counts = Counter()
        for ents in user_ents_list:
            if len(ents) >= 2:
                ent_set_counts[frozenset(ents)] += 1
        
        common_sets = [(list(ents), count) for ents, count in ent_set_counts.most_common(5) if count >= 2]
        
        if common_sets:
            print("\n   2. Common Entitlement Bundles (potential roles):")
            for ents, count in common_sets[:5]:
                print(f"      - Bundle with {len(ents)} entitlements: appears in {count} users")
                print(f"        Entitlements: {ents[:3]}{'...' if len(ents) > 3 else ''}")
        
        return {
            "risk_groups": risk_groups,
            "total_users": len(user_list),
            "unique_entitlements": df['entitlement_id'].nunique()
        }


def main():
    print("="*60)
    print("🔐 ROLE MINING ENGINE")
    print("Discovering optimal role groupings from access patterns")
    print("="*60)
    
    # Initialize
    miner = RoleMiner()
    
    # Load data
    df = miner.load_data("datasets/synthetic/assignments.csv")
    
    # Create transactions
    transactions = miner.create_transactions(df)
    
    # Check data density
    avg_ents = sum(len(t) for t in transactions) / len(transactions)
    
    print(f"\n📈 Data Density Analysis:")
    print(f"   Average entitlements per user: {avg_ents:.1f}")
    
    if avg_ents < 5:
        print("   ⚠️ Sparse data - focusing on pattern analysis rather than Apriori")
        
        # Analyze risk patterns
        pairs_df = miner.analyze_risk_by_role(df)
        
        # Generate practical recommendations
        recommendations = miner.generate_role_recommendations(df)
        
        # Save analysis
        if len(pairs_df) > 0:
            pairs_df.to_csv("02-role-mining-engine/output/entitlement_pairs.csv", index=False)
            print(f"\n💾 Saved entitlement pair analysis to 02-role-mining-engine/output/entitlement_pairs.csv")
        
        # Save recommendations
        with open("02-role-mining-engine/output/role_recommendations.json", 'w') as f:
            json.dump({
                "avg_entitlements_per_user": avg_ents,
                "total_users": recommendations['total_users'],
                "unique_entitlements": recommendations['unique_entitlements'],
                "risk_based_roles": {
                    risk: len(ents) for risk, ents in recommendations['risk_groups'].items()
                }
            }, f, indent=2)
        
        print("\n📝 NEXT STEPS FOR ROLE ENGINEERING:")
        print("   1. Use the entitlement pairs above to identify frequently co-occurring permissions")
        print("   2. Create roles based on risk levels (Critical, High, Medium, Low access roles)")
        print("   3. For production, collect more data (aim for 10+ entitlements per user)")
        print("   4. Consider using department + job title as role indicators instead")
        
    else:
        # Dense data - use Apriori algorithm
        print("   ✅ Dense data - running Apriori algorithm")
        
        # Encode transactions
        te = TransactionEncoder()
        te_array = te.fit(transactions).transform(transactions)
        df_encoded = pd.DataFrame(te_array, columns=te.columns_)
        
        # Find frequent itemsets
        min_support = max(0.01, 5/len(transactions))  # Dynamic threshold
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        if len(frequent_itemsets) > 0:
            frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)
            frequent_itemsets = frequent_itemsets[frequent_itemsets['length'] >= 2]
            
            if len(frequent_itemsets) > 0:
                print(f"   Found {len(frequent_itemsets)} frequent itemsets")
                
                # Generate rules
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
                rules = rules.sort_values('lift', ascending=False)
                
                print(f"   Generated {len(rules)} association rules")
                
                # Extract role candidates
                role_candidates = []
                for idx, rule in rules.head(20).iterrows():
                    role_candidates.append({
                        "entitlements": list(rule['antecedents']) + list(rule['consequents']),
                        "support": round(rule['support'], 3),
                        "confidence": round(rule['confidence'], 3),
                        "lift": round(rule['lift'], 3)
                    })
                
                # Save results
                with open("02-role-mining-engine/output/role_candidates.json", 'w') as f:
                    json.dump(role_candidates, f, indent=2)
                
                print(f"\n💾 Saved {len(role_candidates)} role candidates to JSON")
    
    print("\n✅ Role mining complete!")


if __name__ == "__main__":
    main()
