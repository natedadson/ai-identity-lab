"""
Identity Graph Builder for Neo4j
Creates graph relationships between Users, Entitlements, and Risks.
"""

import pandas as pd
from neo4j import GraphDatabase
import os

class IdentityGraphBuilder:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password123"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        print("✅ Connected to Neo4j database")
    
    def close(self):
        if self.driver:
            self.driver.close()
            print("🔌 Disconnected from Neo4j")
    
    def clear_graph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️  Cleared existing graph")
    
    def create_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entitlement) REQUIRE e.entitlement_id IS UNIQUE")
            print("✅ Created constraints")
    
    def build_graph(self, users_path, entitlements_path, assignments_path):
        print("="*60)
        print("🏗️  BUILDING IDENTITY GRAPH")
        print("="*60)
        
        # Load data
        users = pd.read_csv(users_path)
        entitlements = pd.read_csv(entitlements_path)
        assignments = pd.read_csv(assignments_path)
        
        print(f"\n📊 Data Summary:")
        print(f"   Users: {len(users)}")
        print(f"   Entitlements: {len(entitlements)}")
        print(f"   Assignments: {len(assignments)}")
        
        self.connect()
        self.clear_graph()
        self.create_constraints()
        
        # Load users
        print("\n👥 Loading users...")
        with self.driver.session() as session:
            for _, user in users.iterrows():
                session.run(
                    "MERGE (u:User {user_id: $user_id}) SET u.name = $name, u.department = $department, u.role = $role",
                    user_id=user['user_id'], name=user.get('name', ''), 
                    department=user.get('department', ''), role=user.get('role', '')
                )
        print(f"   ✅ Loaded {len(users)} users")
        
        # Load entitlements
        print("\n🔑 Loading entitlements...")
        with self.driver.session() as session:
            for _, ent in entitlements.iterrows():
                session.run(
                    "MERGE (e:Entitlement {entitlement_id: $entitlement_id}) SET e.name = $name, e.risk_level = $risk_level",
                    entitlement_id=ent['entitlement_id'], name=ent.get('name', ''), risk_level=ent.get('risk_level', 'Low')
                )
        print(f"   ✅ Loaded {len(entitlements)} entitlements")
        
        # Create HAS_ACCESS relationships
        print("\n🔗 Creating HAS_ACCESS relationships...")
        with self.driver.session() as session:
            for _, ass in assignments.iterrows():
                session.run(
                    "MATCH (u:User {user_id: $user_id}) MATCH (e:Entitlement {entitlement_id: $entitlement_id}) MERGE (u)-[:HAS_ACCESS]->(e)",
                    user_id=ass['user_id'], entitlement_id=ass['entitlement_id']
                )
        print(f"   ✅ Created {len(assignments)} relationships")
        
        print("\n" + "="*60)
        print("✅ Identity Graph Built Successfully!")
        print("="*60)
        print("\n🌐 Open Neo4j Browser: http://localhost:7474")
        print("   Credentials: neo4j / password123")

def main():
    builder = IdentityGraphBuilder()
    try:
        builder.build_graph(
            "datasets/synthetic/users.csv",
            "datasets/synthetic/entitlements.csv",
            "datasets/synthetic/assignments.csv"
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure Neo4j is running: brew services start neo4j")
    finally:
        builder.close()

if __name__ == "__main__":
    main()
