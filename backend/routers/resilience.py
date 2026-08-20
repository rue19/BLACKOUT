"""
BLACKOUT Resilience Router - GET /resilience endpoint

Uses HydraDB-compatible Cypher queries.
"""

from fastapi import APIRouter
from schemas import ResilienceResponse
from db import get_driver

router = APIRouter(prefix="/resilience", tags=["resilience"])


@router.get("", response_model=ResilienceResponse)
async def get_resilience():
    """Get the current Knowledge Resilience Score."""
    driver = get_driver()
    try:
        with driver.session(database="default") as session:
            r = session.run("MATCH (c:Claim) RETURN c.id AS cid")
            claims = [dict(record) for record in r]

            if not claims:
                return ResilienceResponse(score=100.0, breakdown={"backed_up": 0, "total": 0})

            backed_up = 0
            for claim in claims:
                r2 = session.run(
                    "MATCH (e)-[:SUPPORTS]->(c:Claim {id: $cid}) RETURN count(*) AS cnt",
                    cid=claim["cid"],
                )
                record = r2.single()
                if record and record["cnt"] >= 2:
                    backed_up += 1

            score = round((backed_up / len(claims)) * 100, 1) if claims else 100.0

            return ResilienceResponse(
                score=score,
                breakdown={
                    "backed_up": backed_up,
                    "total": len(claims),
                    "description": "Claims with 2+ independent evidence sources",
                },
            )
    finally:
        driver.close()
