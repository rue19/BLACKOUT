"""
BLACKOUT Cross-Training Service - Find closest connected expert

Uses HydraDB's algo.SSpaths procedure for path finding.
"""

from neo4j import Driver


async def find_cross_training_recommendations(
    person_id: str,
    driver: Driver
) -> list[dict]:
    """
    Find closest connected experts for cross-training.

    Uses MATCH patterns to find persons connected via AUTHORED or BACKUP_FOR.
    """
    with driver.session(database="default") as session:
        # Find the person's integer ID
        r = session.run(
            'MATCH (p:Person) WHERE p.string_id = $pid RETURN p.id AS int_id',
            pid=person_id
        )
        record = r.single()
        if not record:
            return []
        
        person_int_id = record["int_id"]

        # Find connected persons via co-authoring (2-hop through claims)
        r = session.run("""
            MATCH (p:Person {id: $pid})-[:AUTHORED]->(m1)-[:SUPPORTS]->(c:Claim)<-[:SUPPORTS]-(m2)<-[:AUTHORED]-(p2:Person)
            WHERE p2.id <> $pid
            RETURN p2.id AS int_id, p2.string_id AS string_id, p2.name AS name, count(*) AS shared_claims
            ORDER BY shared_claims DESC
            LIMIT 5
        """, pid=person_int_id)

        recommendations = []
        for record in r:
            rec = dict(record)
            recommendations.append({
                "person": {
                    "canonical_id": rec.get("string_id", ""),
                    "name": rec.get("name", ""),
                },
                "path": f"Person({person_int_id}) -> Person({rec['int_id']})",
                "claimsCoverable": rec.get("shared_claims", 0),
            })

        # Also find BACKUP_FOR relationships
        r2 = session.run("""
            MATCH (p:Person {id: $pid})<-[:BACKUP_FOR]-(backup:Person)
            RETURN backup.id AS int_id, backup.string_id AS string_id, backup.name AS name
        """, pid=person_int_id)

        seen_ids = {rec["int_id"] for rec in recommendations}
        for record in r2:
            rec = dict(record)
            if rec["int_id"] not in seen_ids:
                recommendations.append({
                    "person": {
                        "canonical_id": rec.get("string_id", ""),
                        "name": rec.get("name", ""),
                    },
                    "path": f"Person({rec['int_id']}) -[:BACKUP_FOR]-> Person({person_int_id})",
                    "claimsCoverable": 0,
                })
                seen_ids.add(rec["int_id"])

        return recommendations
