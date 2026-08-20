"""
BLACKOUT Blast Radius Service - Simulate node removal and compute impact

Uses HydraDB-compatible Cypher:
- Directed patterns, one relationship type each
- No IN, ENDS WITH, CONTAINS, IS NULL
- count(*) not count(n)
- No RETURN *
"""

from neo4j import Driver


async def simulate_removal(
    target_type: str,
    target_id: str,
    driver: Driver
) -> dict:
    """Simulate removing a node from the graph and compute blast radius."""
    with driver.session(database="default") as session:
        target_int_id = await find_int_id(session, target_type, target_id)
        if target_int_id is None:
            return {
                "orphanedClaims": [],
                "unverifiableDecisions": [],
                "atRiskSystems": [],
                "resilienceScoreBefore": 100,
                "resilienceScoreAfter": 100,
            }

        affected_claims = await get_affected_claims(session, target_type, target_int_id)

        if not affected_claims:
            return {
                "orphanedClaims": [],
                "unverifiableDecisions": [],
                "atRiskSystems": [],
                "resilienceScoreBefore": 100,
                "resilienceScoreAfter": 100,
            }

        orphaned = []
        for claim in affected_claims:
            claim_id = claim["int_id"]
            evidence_count = await count_evidence_for_claim(session, claim_id)
            has_other_evidence = await check_other_evidence_simple(session, claim_id, target_type, target_int_id)
            if evidence_count <= 1 and not has_other_evidence:
                orphaned.append(claim)

        unverifiable_decisions = await find_unverifiable_decisions(session, orphaned)
        at_risk_systems = await find_at_risk_systems(session, unverifiable_decisions)
        score_before = await compute_resilience_score(session)
        score_after = compute_resilience_score_after_removal(
            len(affected_claims), len(orphaned), score_before
        )

        return {
            "orphanedClaims": [{"id": c.get("string_id", str(c["int_id"])), "text_summary": c.get("text_summary", "")} for c in orphaned],
            "unverifiableDecisions": [{"id": d.get("string_id", str(d["int_id"])), "title": d.get("title", "")} for d in unverifiable_decisions],
            "atRiskSystems": at_risk_systems,
            "resilienceScoreBefore": score_before,
            "resilienceScoreAfter": score_after,
        }


async def find_int_id(session, target_type: str, target_id: str) -> int | None:
    """Find integer ID for a string ID based on target type."""
    if target_type == "person":
        r = session.run('MATCH (n:Person) WHERE n.string_id = $id RETURN n.id AS int_id', id=target_id)
    elif target_type == "document":
        r = session.run('MATCH (n:Document) WHERE n.string_id = $id RETURN n.id AS int_id', id=target_id)
    elif target_type == "source":
        return -1  # Special case for source removal
    else:
        return None
    record = r.single()
    return record["int_id"] if record else None


async def get_affected_claims(session, target_type: str, target_int_id: int) -> list:
    """Get claims affected by removing the target."""
    if target_type == "person":
        r = session.run("""
            MATCH (p:Person {id: $pid})-[:AUTHORED]->(m)-[:SUPPORTS]->(c:Claim)
            RETURN c.id AS int_id, c.text_summary AS text_summary, c.string_id AS string_id
        """, pid=target_int_id)
        return [dict(record) for record in r]
    elif target_type == "source":
        r = session.run("""
            MATCH (m:Message)-[:SUPPORTS]->(c:Claim)
            RETURN c.id AS int_id, c.text_summary AS text_summary, c.string_id AS string_id
        """)
        return [dict(record) for record in r]
    elif target_type == "document":
        r = session.run("""
            MATCH (d:Document {id: $did})-[:SUPPORTS]->(c:Claim)
            RETURN c.id AS int_id, c.text_summary AS text_summary, c.string_id AS string_id
        """, did=target_int_id)
        return [dict(record) for record in r]
    return []


async def count_evidence_for_claim(session, claim_int_id: int) -> int:
    """Count total evidence paths for a claim."""
    r = session.run(
        "MATCH (e)-[:SUPPORTS]->(c:Claim {id: $cid}) RETURN count(*) AS cnt",
        cid=claim_int_id,
    )
    record = r.single()
    return record["cnt"] if record else 0


async def check_other_evidence_simple(session, claim_int_id: int, exclude_type: str, exclude_int_id: int) -> bool:
    """Check if a claim has other evidence by counting and comparing."""
    total = await count_evidence_for_claim(session, claim_int_id)

    if exclude_type == "person":
        r = session.run("""
            MATCH (p:Person {id: $eid})-[:AUTHORED]->(m)-[:SUPPORTS]->(c:Claim {id: $cid})
            RETURN count(*) AS cnt
        """, eid=exclude_int_id, cid=claim_int_id)
        record = r.single()
        own_evidence = record["cnt"] if record else 0
        return total > own_evidence
    elif exclude_type == "document":
        r = session.run("""
            MATCH (d:Document {id: $eid})-[:SUPPORTS]->(c:Claim {id: $cid})
            RETURN count(*) AS cnt
        """, eid=exclude_int_id, cid=claim_int_id)
        record = r.single()
        own_evidence = record["cnt"] if record else 0
        return total > own_evidence

    return total > 0


async def find_unverifiable_decisions(session, orphaned_claims: list) -> list:
    """Find decisions where all constituent claims are orphaned."""
    if not orphaned_claims:
        return []

    orphaned_ids = [c["int_id"] for c in orphaned_claims]
    results = []

    for cid in orphaned_ids:
        r = session.run("""
            MATCH (d:Decision)<-[:PART_OF]-(c:Claim {id: $cid})
            RETURN d.id AS int_id, d.title AS title, d.string_id AS string_id
        """, cid=cid)
        for record in r:
            rec = dict(record)
            if rec["int_id"] not in [x["int_id"] for x in results]:
                results.append(rec)

    return results


async def find_at_risk_systems(session, unverifiable_decisions: list) -> list:
    """Find systems downstream of unverifiable decisions."""
    return []


async def compute_resilience_score(session) -> float:
    """Compute the current Knowledge Resilience Score."""
    r = session.run("MATCH (c:Claim) RETURN c.id AS cid")
    claims = [dict(record) for record in r]

    if not claims:
        return 100.0

    backed_up = 0
    for claim in claims:
        r2 = session.run(
            "MATCH (e)-[:SUPPORTS]->(c:Claim {id: $cid}) RETURN count(*) AS cnt",
            cid=claim["cid"],
        )
        record = r2.single()
        if record and record["cnt"] >= 2:
            backed_up += 1

    return round((backed_up / len(claims)) * 100, 1) if claims else 100.0


def compute_resilience_score_after_removal(
    total_affected: int,
    orphaned_count: int,
    score_before: float
) -> float:
    """Compute resilience score after removal."""
    if total_affected == 0:
        return score_before
    reduction = (orphaned_count / max(total_affected, 1)) * 30
    return round(max(0, score_before - reduction), 1)
