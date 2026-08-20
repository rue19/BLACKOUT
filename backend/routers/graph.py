"""
BLACKOUT Graph Router - GET /graph endpoint

Uses HydraDB-compatible Cypher queries.
"""

from fastapi import APIRouter
from db import get_driver

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("")
async def get_graph(scope: str = "full"):
    """Get nodes and edges for visualization."""
    driver = get_driver()
    try:
        with driver.session(database="default") as session:
            nodes = []
            for label in ["Person", "Message", "Document", "Claim", "Decision"]:
                r = session.run(f"""
                    MATCH (n:{label})
                    RETURN n.id AS int_id, n.string_id AS string_id, n.name AS name,
                           n.text_summary AS text_summary, n.title AS title,
                           n.source_system AS source_system, n.status AS status
                """)
                for record in r:
                    rec = dict(record)
                    int_id = rec["int_id"]
                    text = (rec.get("text_summary") or "")[:50]
                    display_name = rec.get("name") or rec.get("title") or text or rec.get("string_id") or str(int_id)
                    nodes.append({
                        "id": str(int_id),
                        "label": label,
                        "name": display_name,
                        "string_id": rec.get("string_id", ""),
                    })

            edges = []
            for rel_type in ["AUTHORED", "SUPPORTS", "PART_OF", "CONTRADICTS", "SUPERSEDES", "BACKUP_FOR"]:
                r = session.run(f"""
                    MATCH (s)-[r:{rel_type}]->(d)
                    RETURN s.id AS src, d.id AS dst
                """)
                for record in r:
                    rec = dict(record)
                    edges.append({
                        "source": str(rec["src"]),
                        "target": str(rec["dst"]),
                        "type": rel_type,
                    })

            return {"nodes": nodes, "edges": edges}
    finally:
        driver.close()
