"""
Identity Graph Visualization using NetworkX
Alternative to Neo4j for graph analysis and visualization.
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

class IdentityGraphViz:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph
        
    def build_graph(self, assignments_path, users_path, entitlements_path):
        """Build graph from identity data."""
        print("="*60)
        print("🏗️  BUILDING IDENTITY GRAPH (NetworkX)")
        print("="*60)
        
        # Load data
        assignments = pd.read_csv(assignments_path)
        users = pd.read_csv(users_path)
        entitlements = pd.read_csv(entitlements_path)
        
        print(f"\n📊 Data Summary:")
        print(f"   Users: {len(users)}")
        print(f"   Entitlements: {len(entitlements)}")
        print(f"   Assignments: {len(assignments)}")
        
        # Add user nodes
        for _, user in users.iterrows():
            self.graph.add_node(
                user['user_id'], 
                type='user',
                department=user.get('department', 'Unknown'),
                role=user.get('role', 'Unknown')
            )
        
        # Add entitlement nodes
        risk_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
        for _, ent in entitlements.iterrows():
            self.graph.add_node(
                ent['entitlement_id'],
                type='entitlement',
                risk_level=ent.get('risk_level', 'Low'),
                color=risk_colors.get(ent.get('risk_level', 'Low'), '#6c757d')
            )
        
        # Add edges (HAS_ACCESS)
        for _, ass in assignments.iterrows():
            self.graph.add_edge(
                ass['user_id'],
                ass['entitlement_id'],
                relationship='HAS_ACCESS'
            )
        
        print(f"\n📈 Graph Statistics:")
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")
        print(f"   Density: {nx.density(self.graph):.4f}")
        
        return self.graph
    
    def analyze_centrality(self):
        """Find most connected users and entitlements."""
        print("\n" + "="*60)
        print("📊 CENTRALITY ANALYSIS")
        print("="*60)
        
        # Degree centrality (most connections)
        degree = nx.degree_centrality(self.graph)
        top_users = [(n, d) for n, d in sorted(degree.items(), key=lambda x: x[1], reverse=True) 
                     if self.graph.nodes[n].get('type') == 'user'][:5]
        top_ents = [(n, d) for n, d in sorted(degree.items(), key=lambda x: x[1], reverse=True) 
                    if self.graph.nodes[n].get('type') == 'entitlement'][:5]
        
        print("\n🔝 Most Connected Users (highest degree):")
        for user, score in top_users:
            dept = self.graph.nodes[user].get('department', 'Unknown')
            print(f"   • {user} ({dept}): {score:.3f}")
        
        print("\n🔝 Most Connected Entitlements (highest degree):")
        for ent, score in top_ents:
            risk = self.graph.nodes[ent].get('risk_level', 'Unknown')
            print(f"   • {ent} ({risk} risk): {score:.3f}")
        
        return top_users, top_ents
    
    def find_risk_paths(self):
        """Find users with access to high-risk entitlements."""
        print("\n" + "="*60)
        print("⚠️ RISK PATH ANALYSIS")
        print("="*60)
        
        risk_users = []
        for node in self.graph.nodes:
            if self.graph.nodes[node].get('type') == 'entitlement':
                risk = self.graph.nodes[node].get('risk_level', 'Low')
                if risk in ['Critical', 'High']:
                    # Find users connected to this entitlement
                    users = list(self.graph.predecessors(node))
                    for user in users:
                        risk_users.append({
                            'user': user,
                            'entitlement': node,
                            'risk_level': risk
                        })
        
        print(f"\n⚠️ Found {len(risk_users)} high-risk access paths")
        
        # Show unique users with critical access
        critical_users = set(r['user'] for r in risk_users if r['risk_level'] == 'Critical')
        print(f"\n🔴 Users with CRITICAL access: {len(critical_users)}")
        for user in list(critical_users)[:10]:
            print(f"   • {user}")
        
        return risk_users
    
    def find_similar_users(self):
        """Find users with similar entitlement patterns."""
        print("\n" + "="*60)
        print("👥 USER SIMILARITY ANALYSIS")
        print("="*60)
        
        # Get all user nodes
        users = [n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'user']
        
        # Create adjacency matrix for users (based on shared entitlements)
        similarities = []
        for i, u1 in enumerate(users[:50]):  # Limit to 50 for performance
            u1_ents = set(self.graph.successors(u1))
            for u2 in users[i+1:50]:
                u2_ents = set(self.graph.successors(u2))
                overlap = len(u1_ents & u2_ents)
                if overlap >= 2:  # Share at least 2 entitlements
                    similarities.append({
                        'user1': u1,
                        'user2': u2,
                        'shared_ents': overlap,
                        'dept1': self.graph.nodes[u1].get('department', 'Unknown'),
                        'dept2': self.graph.nodes[u2].get('department', 'Unknown')
                    })
        
        print(f"\n📊 Found {len(similarities)} similar user pairs")
        print("\n🔝 Top 5 Similar User Pairs:")
        for sim in sorted(similarities, key=lambda x: x['shared_ents'], reverse=True)[:5]:
            print(f"   • {sim['user1']} ({sim['dept1']}) ↔ {sim['user2']} ({sim['dept2']}): {sim['shared_ents']} shared entitlements")
        
        return similarities
    
    def visualize_graph(self, max_nodes=100):
        """Create a visualization of the graph."""
        print("\n" + "="*60)
        print("🎨 GENERATING VISUALIZATION")
        print("="*60)
        
        # Sample a subset for visualization
        nodes = list(self.graph.nodes)[:max_nodes]
        subgraph = self.graph.subgraph(nodes)
        
        plt.figure(figsize=(16, 12))
        
        # Set node colors based on type
        node_colors = []
        for node in subgraph.nodes:
            if subgraph.nodes[node].get('type') == 'user':
                node_colors.append('#0066cc')  # Blue for users
            else:
                # Entitlement colors based on risk
                risk = subgraph.nodes[node].get('risk_level', 'Low')
                if risk == 'Critical':
                    node_colors.append('#dc3545')  # Red
                elif risk == 'High':
                    node_colors.append('#fd7e14')  # Orange
                elif risk == 'Medium':
                    node_colors.append('#ffc107')  # Yellow
                else:
                    node_colors.append('#28a745')  # Green
        
        # Layout
        pos = nx.spring_layout(subgraph, k=2, iterations=50)
        
        # Draw
        nx.draw(subgraph, pos, 
                node_color=node_colors,
                node_size=500,
                edge_color='#cccccc',
                alpha=0.7,
                with_labels=False,
                arrows=True,
                arrowsize=10)
        
        # Add labels for important nodes
        labels = {}
        for node in subgraph.nodes:
            if subgraph.nodes[node].get('type') == 'entitlement':
                risk = subgraph.nodes[node].get('risk_level', '')
                if risk in ['Critical', 'High']:
                    labels[node] = node[:15]
            elif subgraph.nodes[node].get('type') == 'user':
                dept = subgraph.nodes[node].get('department', '')
                if dept in ['Finance', 'Executive']:
                    labels[node] = f"{node} ({dept})"
        
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=8, font_weight='bold')
        
        plt.title("Identity Graph: Users (Blue) → Entitlements (Colored by Risk Level)\nRed=Critical, Orange=High, Yellow=Medium, Green=Low", fontsize=14)
        plt.tight_layout()
        plt.savefig("05-identity-graph-analytics/output/identity_graph.png", dpi=150, bbox_inches='tight')
        plt.show()
        
        print("📊 Graph visualization saved to: 05-identity-graph-analytics/output/identity_graph.png")
    
    def generate_report(self):
        """Generate comprehensive graph analysis report."""
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE GRAPH REPORT")
        print("="*60)
        
        report = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "graph_density": round(nx.density(self.graph), 4),
            "users": len([n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'user']),
            "entitlements": len([n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'entitlement']),
            "is_connected": nx.is_weakly_connected(self.graph),
            "components": nx.number_weakly_connected_components(self.graph)
        }
        
        for key, value in report.items():
            print(f"   {key}: {value}")
        
        # Save report
        import json
        with open("05-identity-graph-analytics/output/graph_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n💾 Report saved to: 05-identity-graph-analytics/output/graph_report.json")


def main():
    # Create output directory
    import os
    os.makedirs("05-identity-graph-analytics/output", exist_ok=True)
    
    # Build graph
    viz = IdentityGraphViz()
    viz.build_graph(
        "datasets/synthetic/assignments.csv",
        "datasets/synthetic/users.csv",
        "datasets/synthetic/entitlements.csv"
    )
    
    # Analyze
    viz.analyze_centrality()
    viz.find_risk_paths()
    viz.find_similar_users()
    
    # Visualize
    viz.visualize_graph(max_nodes=150)
    
    # Generate report
    viz.generate_report()
    
    print("\n" + "="*60)
    print("✅ Identity Graph Analysis Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
