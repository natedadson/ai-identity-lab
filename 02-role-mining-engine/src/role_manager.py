"""
Role Manager - Validates and assigns role recommendations
"""

import pandas as pd
import json
from datetime import datetime

class RoleManager:
    def __init__(self, role_definitions_path, assignments_path):
        """Initialize with role definitions and current assignments."""
        with open(role_definitions_path, 'r') as f:
            self.role_data = json.load(f)
            self.roles = self.role_data['roles']
        
        self.assignments = pd.read_csv(assignments_path)
        print(f"📋 Loaded {len(self.roles)} role definitions")
        print(f"📊 Loaded {len(self.assignments)} current assignments")
    
    def analyze_role_coverage(self):
        """Check which users already have the entitlements in each role."""
        print("\n" + "="*60)
        print("🔍 ROLE COVERAGE ANALYSIS")
        print("="*60)
        
        coverage_report = []
        
        for role in self.roles:
            role_ents = set(role['entitlements'])
            
            # Find users who have these entitlements
            users_with_ents = []
            for user_id in self.assignments['user_id'].unique():
                user_ents = set(self.assignments[self.assignments['user_id'] == user_id]['entitlement_id'])
                matching_ents = role_ents & user_ents
                
                if len(matching_ents) > 0:
                    users_with_ents.append({
                        "user_id": user_id,
                        "matching_entitlements": len(matching_ents),
                        "total_entitlements_in_role": len(role_ents),
                        "coverage_percentage": len(matching_ents) / len(role_ents) * 100,
                        "missing_entitlements": list(role_ents - user_ents)
                    })
            
            coverage_report.append({
                "role_id": role['role_id'],
                "role_name": role['name'],
                "users_with_partial_coverage": len(users_with_ents),
                "users_with_full_coverage": len([u for u in users_with_ents if u['coverage_percentage'] == 100]),
                "details": users_with_ents[:5]  # Show first 5 users
            })
            
            print(f"\n📦 Role: {role['name']} ({role['role_id']})")
            print(f"   Entitlements: {len(role['entitlements'])}")
            print(f"   Users with partial coverage: {len(users_with_ents)}")
            print(f"   Users with FULL coverage: {coverage_report[-1]['users_with_full_coverage']}")
            
            if len(users_with_ents) > 0:
                print(f"   Sample user: {users_with_ents[0]['user_id']} - "
                      f"{users_with_ents[0]['coverage_percentage']:.0f}% coverage")
        
        return coverage_report
    
    def generate_role_recommendations(self):
        """Generate recommendations for role assignment."""
        print("\n" + "="*60)
        print("💡 ROLE ASSIGNMENT RECOMMENDATIONS")
        print("="*60)
        
        recommendations = []
        
        for role in self.roles:
            role_ents = set(role['entitlements'])
            
            # Find users who would benefit from this role
            for user_id in self.assignments['user_id'].unique():
                user_ents = set(self.assignments[self.assignments['user_id'] == user_id]['entitlement_id'])
                missing_ents = role_ents - user_ents
                
                if len(missing_ents) > 0 and len(missing_ents) < len(role_ents):
                    # User already has some entitlements from this role
                    recommendations.append({
                        "user_id": user_id,
                        "role_id": role['role_id'],
                        "role_name": role['name'],
                        "current_entitlements": len(user_ents),
                        "role_entitlements": len(role_ents),
                        "already_have": len(role_ents) - len(missing_ents),
                        "missing_entitlements": list(missing_ents),
                        "priority": "HIGH" if role['risk_level'] in ['Critical', 'High-Critical'] else "MEDIUM",
                        "action": "Add missing entitlements and convert to role-based access"
                    })
        
        # Sort by priority
        recommendations.sort(key=lambda x: 0 if x['priority'] == 'HIGH' else 1)
        
        print(f"\n📋 Found {len(recommendations)} role assignment opportunities")
        
        # Show top recommendations
        for rec in recommendations[:10]:
            print(f"\n   👤 User: {rec['user_id']}")
            print(f"   🎯 Role: {rec['role_name']} ({rec['priority']} priority)")
            print(f"   📊 Already has {rec['already_have']}/{rec['role_entitlements']} entitlements")
            print(f"   ➕ Missing: {rec['missing_entitlements'][:3]}{'...' if len(rec['missing_entitlements']) > 3 else ''}")
        
        return recommendations
    
    def create_role_implementation_plan(self, recommendations):
        """Create a phased implementation plan."""
        print("\n" + "="*60)
        print("📅 ROLE IMPLEMENTATION PLAN")
        print("="*60)
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
        
        plan = {
            "phase_1_immediate": {
                "roles": ["CRITICAL_ACCESS_ROLE"],
                "users_affected": len(set([r['user_id'] for r in high_priority if r['role_id'] == 'CRITICAL_ACCESS_ROLE'])),
                "actions": [
                    "Review the Critical Access Role definition with security team",
                    "Identify users who already have 80%+ of entitlements",
                    "Add missing entitlements and convert to role-based access",
                    "Implement weekly review cycle for Critical roles"
                ],
                "timeline_days": 3
            },
            "phase_2_this_week": {
                "roles": ["HIGH_RISK_ANALYST_ROLE"],
                "users_affected": len(set([r['user_id'] for r in high_priority if r['role_id'] == 'HIGH_RISK_ANALYST_ROLE'])),
                "actions": [
                    "Validate High Risk Analyst Role with Finance department",
                    "Create role in IGA platform (SailPoint/Active Directory)",
                    "Migrate users with 100% coverage first",
                    "Schedule manager approval for remaining users"
                ],
                "timeline_days": 5
            },
            "phase_3_next_week": {
                "roles": ["STANDARD_BUNDLE_ROLE"],
                "users_affected": len(set([r['user_id'] for r in medium_priority])),
                "actions": [
                    "Create Standard Bundle Role",
                    "Gradually migrate users during regular access reviews",
                    "Monitor for any access issues post-migration"
                ],
                "timeline_days": 7
            }
        }
        
        for phase, details in plan.items():
            print(f"\n📌 {phase.replace('_', ' ').title()}")
            print(f"   Roles: {', '.join(details['roles'])}")
            print(f"   Users affected: {details['users_affected']}")
            print(f"   Timeline: {details['timeline_days']} days")
            print(f"   Actions:")
            for action in details['actions']:
                print(f"     • {action}")
        
        return plan
    
    def save_reports(self, coverage, recommendations, plan):
        """Save all reports to files."""
        output_dir = "02-role-mining-engine/output"
        
        # Save coverage report
        with open(f"{output_dir}/role_coverage_report.json", 'w') as f:
            json.dump(coverage, f, indent=2)
        
        # Save recommendations
        with open(f"{output_dir}/role_assignment_recommendations.json", 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        # Save implementation plan
        with open(f"{output_dir}/implementation_plan.json", 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"\n💾 Reports saved to {output_dir}/")
        print(f"   - role_coverage_report.json")
        print(f"   - role_assignment_recommendations.json")
        print(f"   - implementation_plan.json")


def main():
    print("="*60)
    print("🏢 ROLE MANAGEMENT SYSTEM")
    print="="*60)
    
    # Initialize manager
    manager = RoleManager(
        "02-role-mining-engine/config/role_definitions.json",
        "datasets/synthetic/assignments.csv"
    )
    
    # Analyze current coverage
    coverage = manager.analyze_role_coverage()
    
    # Generate recommendations
    recommendations = manager.generate_role_recommendations()
    
    # Create implementation plan
    plan = manager.create_role_implementation_plan(recommendations)
    
    # Save all reports
    manager.save_reports(coverage, recommendations, plan)
    
    print("\n" + "="*60)
    print("✅ Role Management Complete!")
    print("="*60)
    print("\n📝 NEXT ACTIONS:")
    print("   1. Review role definitions with security team")
    print("   2. Start with Phase 1 (Critical Access Role)")
    print("   3. Migrate users gradually")
    print("   4. Monitor for access issues post-migration")


if __name__ == "__main__":
    main()
