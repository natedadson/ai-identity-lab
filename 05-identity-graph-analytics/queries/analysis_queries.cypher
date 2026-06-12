// ============================================
// IDENTITY GRAPH ANALYSIS QUERIES
// Run these in Neo4j Browser (http://localhost:7474)
// ============================================

// 1. Find users with Critical risk entitlements
MATCH (u:User)-[:HAS_ACCESS]->(e:Entitlement)-[:HAS_RISK]->(r:Risk {level: "Critical"})
RETURN u.user_id, u.department, e.name, e.application
LIMIT 20;

// 2. Find privilege escalation paths (users with High + Critical access)
MATCH (u:User)-[:HAS_ACCESS]->(e1:Entitlement)-[:HAS_RISK]->(r1:Risk {level: "High"})
MATCH (u)-[:HAS_ACCESS]->(e2:Entitlement)-[:HAS_RISK]->(r2:Risk {level: "Critical"})
RETURN u.user_id, u.department, 
       COLLECT(DISTINCT e1.name) as high_risk_ents,
       COLLECT(DISTINCT e2.name) as critical_ents
LIMIT 10;

// 3. Most dangerous users (most Critical entitlements)
MATCH (u:User)-[:HAS_ACCESS]->(e:Entitlement)-[:HAS_RISK]->(r:Risk {level: "Critical"})
RETURN u.user_id, u.department, u.role, COUNT(e) as critical_count
ORDER BY critical_count DESC
LIMIT 10;

// 4. Entitlements that appear together (potential role candidates)
MATCH (u:User)-[:HAS_ACCESS]->(e1:Entitlement)
MATCH (u)-[:HAS_ACCESS]->(e2:Entitlement)
WHERE e1.entitlement_id < e2.entitlement_id
RETURN e1.name, e2.name, COUNT(*) as co_occurrence
ORDER BY co_occurrence DESC
LIMIT 10;

// 5. Users with no recent access (stale accounts)
MATCH (u:User)-[r:HAS_ACCESS]->(e:Entitlement)
WHERE r.days_since_last_use > 90 OR r.days_since_last_use = -1
RETURN u.user_id, COUNT(e) as stale_entitlements
ORDER BY stale_entitlements DESC
LIMIT 10;

// 6. Department risk summary
MATCH (u:User)-[:BELONGS_TO]->(d:Department)
MATCH (u)-[:HAS_ACCESS]->(e:Entitlement)-[:HAS_RISK]->(r:Risk)
RETURN d.name, 
       r.level, 
       COUNT(DISTINCT u) as users,
       COUNT(e) as entitlements
ORDER BY d.name, r.score DESC;

// 7. Find shortest path between two users (privilege chain)
MATCH p = shortestPath((u1:User {user_id: 'user_0001'})-[*..5]-(u2:User {user_id: 'user_0100'}))
RETURN p;

// 8. Users who have both create and approve privileges (SOD risk)
MATCH (u:User)-[:HAS_ACCESS]->(e1:Entitlement)
WHERE e1.name CONTAINS 'create' OR e1.name CONTAINS 'approve'
WITH u, COLLECT(e1.name) as ents
WHERE ANY(x IN ents WHERE x CONTAINS 'create') 
  AND ANY(x IN ents WHERE x CONTAINS 'approve')
RETURN u.user_id, ents
LIMIT 10;

// 9. Graph statistics
MATCH (u:User) WITH COUNT(u) as users
MATCH (e:Entitlement) WITH users, COUNT(e) as ents
MATCH (r:Risk) WITH users, ents, COUNT(r) as risks
MATCH ()-[rel:HAS_ACCESS]->() WITH users, ents, risks, COUNT(rel) as relationships
RETURN users, ents, risks, relationships;

// 10. Potential SOD violations (users with conflicting entitlement pairs)
MATCH (u:User)-[:HAS_ACCESS]->(e1:Entitlement)
MATCH (u)-[:HAS_ACCESS]->(e2:Entitlement)
WHERE e1.name CONTAINS 'create' AND e2.name CONTAINS 'delete'
   OR e1.name CONTAINS 'approve' AND e2.name CONTAINS 'receive'
   OR e1.name CONTAINS 'view' AND e2.name CONTAINS 'edit'
RETURN u.user_id, COLLECT(DISTINCT e1.name) as ent1, COLLECT(DISTINCT e2.name) as ent2
LIMIT 10;
