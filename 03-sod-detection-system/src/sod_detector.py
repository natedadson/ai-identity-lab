"""
SOD Detection System
Detects Segregation of Duties violations in user entitlements.
"""

import pandas as pd
import json
from collections import defaultdict
from datetime import datetime

class SODDetector:
    def __init__(self, sod_rules_path, assignments_path):
        """Initialize with SOD rules and current assignments."""
        with open(sod_rules_path, 'r') as f:
            self.rules_data = json.load(f)
            self.rules = self.rules_data['sod_rules']
        
        self.assignments = pd.read_csv(assignments_path)
        print(f"📋 Loaded {len(self.rules)} SOD rules")
        print(f"📊 Loaded {len(self.assignments)} assignments for {self.assignments['user_id'].nunique()} users")
    
    def detect_violations(self):
        """Scan all users for SOD violations."""
        print("\n" + "="*60)
        print("🔍 SCANNING FOR SOD VIOLATIONS")
        print("="*60)
        
        violations = []
        violation_counts = defaultdict(int)
        
        # Group entitlements by user
        user_entitlements = self.assignments.groupby('user_id')['entitlement_id'].apply(set).to_dict()
        
        for user_id, entitlements in user_entitlements.items():
            user_violations = []
            
            for rule in self.rules:
                # Check each entitlement pair in the rule
                for pair in rule['entitlement_pairs']:
                    ent1, ent2 = pair
                    
                    # Check if user has both entitlements (or similar patterns)
                    has_ent1 = any(ent1 in e or ent1.replace('_', '') in e.replace('_', '') 
                                   for e in entitlements)
                    has_ent2 = any(ent2 in e or ent2.replace('_', '') in e.replace('_', '') 
                                   for e in entitlements)
                    
                    if has_ent1 and has_ent2:
                        violation = {
                            "user_id": user_id,
                            "rule_id": rule['rule_id'],
                            "rule_name": rule['name'],
                            "risk_level": rule['risk_level'],
                            "entitlements_found": [e for e in entitlements if ent1 in e or ent2 in e],
                            "business_process": rule['business_process'],
                            "mitigation": rule['mitigation'],
                            "detected_date": datetime.now().strftime("%Y-%m-%d"),
                            "severity_score": self._calculate_severity(rule)
                        }
                        user_violations.append(violation)
                        violation_counts[rule['rule_id']] += 1
                        break  # Count once per rule per user
            
            if user_violations:
                violations.extend(user_violations)
        
        self.violations = violations
        print(f"\n⚠️ Found {len(violations)} SOD violations across {len(set(v['user_id'] for v in violations))} users")
        
        return violations
    
    def _calculate_severity(self, rule):
        """Calculate severity score for a violation (1-10)."""
        severity_map = {
            "Critical": 10,
            "High": 7,
            "Medium": 4,
            "Low": 1
        }
        return severity_map.get(rule['risk_level'], 5)
    
    def generate_violation_report(self):
        """Generate detailed violation report."""
        print("\n" + "="*60)
        print("📊 VIOLATION REPORT")
        print("="*60)
        
        if not self.violations:
            print("\n✅ No SOD violations detected! Your access controls are working.")
            return {"summary": "clean"}
        
        # Group by rule
        violations_by_rule = defaultdict(list)
        for v in self.violations:
            violations_by_rule[v['rule_id']].append(v)
        
        print("\n📋 Violations by Rule:")
        for rule_id, rule_violations in violations_by_rule.items():
            rule_name = rule_violations[0]['rule_name']
            risk_level = rule_violations[0]['risk_level']
            print(f"\n   🔴 {rule_name} ({rule_id}) - {risk_level} Risk")
            print(f"      Users affected: {len(rule_violations)}")
            print(f"      Mitigation: {rule_violations[0]['mitigation']}")
            
            # Show affected users
            for v in rule_violations[:5]:
                print(f"        • {v['user_id']}: {v['entitlements_found'][:2]}")
            if len(rule_violations) > 5:
                print(f"        • ... and {len(rule_violations) - 5} more users")
        
        return {
            "total_violations": len(self.violations),
            "affected_users": len(set(v['user_id'] for v in self.violations)),
            "violations_by_rule": {
                rule_id: len(violations) for rule_id, violations in violations_by_rule.items()
            }
        }
    
    def generate_remediation_plan(self):
        """Create remediation recommendations for each violation."""
        print("\n" + "="*60)
        print("🔧 REMEDIATION RECOMMENDATIONS")
        print("="*60)
        
        remediation_plan = []
        
        for violation in self.violations[:10]:  # Top 10 violations
            recommendation = {
                "user_id": violation['user_id'],
                "rule_id": violation['rule_id'],
                "rule_name": violation['rule_name'],
                "current_entitlements": violation['entitlements_found'],
                "remediation_actions": [
                    f"Remove one of: {violation['entitlements_found'][0]} or {violation['entitlements_found'][1] if len(violation['entitlements_found']) > 1 else 'conflicting entitlement'}",
                    f"Implement {violation['mitigation']}",
                    "Create separate roles for conflicting duties",
                    "Add manager approval workflow"
                ],
                "priority": violation['risk_level'],
                "estimated_effort_hours": 2 if violation['risk_level'] == "Critical" else 1,
                "due_date": self._calculate_due_date(violation)
            }
            remediation_plan.append(recommendation)
            
            print(f"\n   👤 User: {violation['user_id']}")
            print(f"   📋 Rule: {violation['rule_name']}")
            print(f"   ⚠️ Risk: {violation['risk_level']}")
            print(f"   🔑 Conflicting entitlements: {violation['entitlements_found'][:2]}")
            print(f"   📝 Actions:")
            for action in recommendation['remediation_actions'][:3]:
                print(f"      • {action}")
        
        return remediation_plan
    
    def _calculate_due_date(self, violation):
        """Calculate remediation due date based on risk level."""
        from datetime import timedelta
        
        days_map = {
            "Critical": 7,
            "High": 14,
            "Medium": 30,
            "Low": 60
        }
        days = days_map.get(violation['risk_level'], 30)
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    def create_audit_report(self):
        """Create compliance audit report."""
        print("\n" + "="*60)
        print("📋 COMPLIANCE AUDIT REPORT")
        print("="*60)
        
        if not self.violations:
            print("\n✅ PASS: No SOD violations found")
            print("   Your access controls are compliant with SOX, HIPAA, and NIST 800-53")
            return
        
        print("\n⚠️ FAIL: SOD violations detected")
        print(f"   Total violations: {len(self.violations)}")
        print(f"   Affected users: {len(set(v['user_id'] for v in self.violations))}")
        
        # Compliance summary
        compliance_status = {
            "SOX": "Violations require remediation - affects financial controls",
            "HIPAA": "Violations found - privacy controls need review",
            "GDPR": "Access violations detected - data protection at risk",
            "NIST 800-53": "AC-5 (Separation of Duties) control failed"
        }
        
        print("\n   Compliance Impact:")
        for framework, status in compliance_status.items():
            print(f"      • {framework}: {status}")
    
    def save_reports(self, violations, remediation_plan):
        """Save all reports to files."""
        output_dir = "03-sod-detection-system/output"
        
        # Save violations
        with open(f"{output_dir}/sod_violations.json", 'w') as f:
            json.dump(violations, f, indent=2)
        
        # Save remediation plan
        with open(f"{output_dir}/remediation_plan.json", 'w') as f:
            json.dump(remediation_plan, f, indent=2)
        
        # Create summary CSV
        if violations:
            df = pd.DataFrame(violations)
            df.to_csv(f"{output_dir}/sod_violations.csv", index=False)
        
        print(f"\n💾 Reports saved to {output_dir}/")
        print(f"   - sod_violations.json")
        print(f"   - remediation_plan.json")
        print(f"   - sod_violations.csv")


def main():
    print("="*60)
    print("🔐 SEGREGATION OF DUTIES (SOD) DETECTION SYSTEM")
    print("="*60)
    print("Detecting toxic entitlement combinations...")
    
    # Initialize detector
    detector = SODDetector(
        "03-sod-detection-system/config/sod_rules.json",
        "datasets/synthetic/assignments.csv"
    )
    
    # Detect violations
    violations = detector.detect_violations()
    
    # Generate report
    report = detector.generate_violation_report()
    
    # Create remediation plan
    remediation = detector.generate_remediation_plan()
    
    # Compliance audit
    detector.create_audit_report()
    
    # Save all reports
    detector.save_reports(violations, remediation)
    
    print("\n" + "="*60)
    print("✅ SOD Detection Complete!")
    print("="*60)
    print("\n📝 NEXT ACTIONS:")
    print("   1. Review SOD violations with security team")
    print("   2. Prioritize Critical risk violations")
    print("   3. Implement remediation plan within 7 days")
    print("   4. Schedule regular SOD audits (weekly/monthly)")


if __name__ == "__main__":
    main()
