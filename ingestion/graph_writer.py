"""
BLACKOUT Graph Writer - Batched UNWIND writes to HydraDB

IMPORTANT: HydraDB requires node IDs to be non-negative integers.
Use IDMapper to convert string IDs to integer IDs.

HydraDB Cypher limitations:
- MERGE must match on id only, then SET labels/properties
- CREATE/UNWIND CREATE for edges only
- No RETURN *, must name columns
- No IN, ENDS WITH, CONTAINS, IS NULL in WHERE
"""

from neo4j import GraphDatabase
from typing import Any
from .id_mapper import IDMapper


class GraphWriter:
    """Batched graph writer for HydraDB using UNWIND-based Cypher."""

    def __init__(self, uri: str, auth_token: str):
        self.driver = GraphDatabase.driver(uri, auth=("neo4j", auth_token))
        self.driver.verify_connectivity()
        self.id_mapper = IDMapper()

    def close(self):
        self.driver.close()

    def run_schema(self, schema_path: str):
        """HydraDB handles identity via integer IDs, no constraints needed."""
        pass

    def batch_write_persons(self, persons: list[dict[str, Any]], batch_size: int = 500):
        """Write person nodes using UNWIND + MERGE (id only) + SET."""
        query = """
        UNWIND $rows AS row
        MERGE (n {id: row.int_id})
        SET n:Person, n.name = row.name, n.string_id = row.string_id
        """

        with self.driver.session(database="default") as session:
            for i in range(0, len(persons), batch_size):
                batch = []
                for p in persons[i:i + batch_size]:
                    int_id = self.id_mapper.get_int_id(p["canonical_id"])
                    batch.append({
                        "int_id": int_id,
                        "string_id": p["canonical_id"],
                        "name": p["name"],
                    })
                session.run(query, rows=batch)

    def batch_write_messages(self, messages: list[dict[str, Any]], batch_size: int = 500):
        """Write message nodes using UNWIND + MERGE (id only) + SET."""
        query = """
        UNWIND $rows AS row
        MERGE (n {id: row.int_id})
        SET n:Message, n.source_system = row.source_system, n.text = row.text, n.string_id = row.string_id
        """

        with self.driver.session(database="default") as session:
            for i in range(0, len(messages), batch_size):
                batch = []
                for m in messages[i:i + batch_size]:
                    int_id = self.id_mapper.get_int_id(m["id"])
                    batch.append({
                        "int_id": int_id,
                        "string_id": m["id"],
                        "source_system": m.get("source_system", ""),
                        "text": m.get("text", "")[:500],
                    })
                session.run(query, rows=batch)

    def batch_write_documents(self, documents: list[dict[str, Any]], batch_size: int = 500):
        """Write document nodes using UNWIND + MERGE (id only) + SET."""
        query = """
        UNWIND $rows AS row
        MERGE (n {id: row.int_id})
        SET n:Document, n.title = row.title, n.source_system = row.source_system, n.string_id = row.string_id
        """

        with self.driver.session(database="default") as session:
            for i in range(0, len(documents), batch_size):
                batch = []
                for d in documents[i:i + batch_size]:
                    int_id = self.id_mapper.get_int_id(d["id"])
                    batch.append({
                        "int_id": int_id,
                        "string_id": d["id"],
                        "title": d.get("title", "")[:200],
                        "source_system": d.get("source_system", ""),
                    })
                session.run(query, rows=batch)

    def batch_write_claims(self, claims: list[dict[str, Any]], batch_size: int = 500):
        """Write claim nodes using UNWIND + MERGE (id only) + SET."""
        query = """
        UNWIND $rows AS row
        MERGE (n {id: row.int_id})
        SET n:Claim, n.text_summary = row.text_summary, n.status = row.status, n.string_id = row.string_id
        """

        with self.driver.session(database="default") as session:
            for i in range(0, len(claims), batch_size):
                batch = []
                for c in claims[i:i + batch_size]:
                    int_id = self.id_mapper.get_int_id(c["id"])
                    batch.append({
                        "int_id": int_id,
                        "string_id": c["id"],
                        "text_summary": c.get("text_summary", "")[:500],
                        "status": c.get("status", "active"),
                    })
                session.run(query, rows=batch)

    def batch_write_decisions(self, decisions: list[dict[str, Any]], batch_size: int = 500):
        """Write decision nodes using UNWIND + MERGE (id only) + SET."""
        query = """
        UNWIND $rows AS row
        MERGE (n {id: row.int_id})
        SET n:Decision, n.title = row.title, n.string_id = row.string_id
        """

        with self.driver.session(database="default") as session:
            for i in range(0, len(decisions), batch_size):
                batch = []
                for d in decisions[i:i + batch_size]:
                    int_id = self.id_mapper.get_int_id(d["id"])
                    batch.append({
                        "int_id": int_id,
                        "string_id": d["id"],
                        "title": d.get("title", "")[:200],
                    })
                session.run(query, rows=batch)

    def write_edges(self, edges: list[dict[str, Any]], batch_size: int = 500):
        """Write edges in batches using UNWIND + MATCH + CREATE.
        
        Each edge dict should have: source_int_id, target_int_id, rel_type,
        and source_label and target_label for the MATCH pattern.
        """
        with self.driver.session(database="default") as session:
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]
                # Group by (rel_type, src_label, tgt_label)
                by_combo: dict[tuple, list] = {}
                for edge in batch:
                    key = (edge["rel_type"], edge.get("source_label", ""), edge.get("target_label", ""))
                    by_combo.setdefault(key, []).append(edge)

                for (rel_type, src_label, tgt_label), combo_edges in by_combo.items():
                    src_match = f":{src_label}" if src_label else ""
                    tgt_match = f":{tgt_label}" if tgt_label else ""

                    query = f"""
                    UNWIND $rows AS row
                    MATCH (s{src_match} {{id: row.source_int_id}}), (d{tgt_match} {{id: row.target_int_id}})
                    CREATE (s)-[:{rel_type}]->(d)
                    """
                    session.run(query, rows=combo_edges)

    def write_author_edges(self, person_string_id: str, node_string_ids: list[str], target_label: str = "Message"):
        """Write AUTHORED edges from a Person to multiple nodes."""
        person_int_id = self.id_mapper.get_int_id(person_string_id)
        edges = [
            {
                "source_int_id": person_int_id,
                "target_int_id": self.id_mapper.get_int_id(nid),
                "rel_type": "AUTHORED",
                "source_label": "Person",
                "target_label": target_label,
            }
            for nid in node_string_ids
            if self.id_mapper.has_id(nid)
        ]
        if edges:
            self.write_edges(edges)

    def write_supports_edges(self, evidence_string_id: str, claim_string_ids: list[str]):
        """Write SUPPORTS edges from evidence to claims."""
        evidence_int_id = self.id_mapper.get_int_id(evidence_string_id)
        src_label = "Message" if "slack" in evidence_string_id or "hero-slack" in evidence_string_id else "Document"
        edges = [
            {
                "source_int_id": evidence_int_id,
                "target_int_id": self.id_mapper.get_int_id(cid),
                "rel_type": "SUPPORTS",
                "source_label": src_label,
                "target_label": "Claim",
            }
            for cid in claim_string_ids
            if self.id_mapper.has_id(cid)
        ]
        if edges:
            self.write_edges(edges)

    def write_partof_edges(self, claim_string_ids: list[str], decision_string_id: str):
        """Write PART_OF edges from claims to a decision."""
        decision_int_id = self.id_mapper.get_int_id(decision_string_id)
        edges = [
            {
                "source_int_id": self.id_mapper.get_int_id(cid),
                "target_int_id": decision_int_id,
                "rel_type": "PART_OF",
                "source_label": "Claim",
                "target_label": "Decision",
            }
            for cid in claim_string_ids
            if self.id_mapper.has_id(cid)
        ]
        if edges:
            self.write_edges(edges)

    def write_contradictions(self, contradictions: list[tuple[str, str]]):
        """Write CONTRADICTS edges between claim pairs."""
        edges = [
            {
                "source_int_id": self.id_mapper.get_int_id(c1),
                "target_int_id": self.id_mapper.get_int_id(c2),
                "rel_type": "CONTRADICTS",
                "source_label": "Claim",
                "target_label": "Claim",
            }
            for c1, c2 in contradictions
            if self.id_mapper.has_id(c1) and self.id_mapper.has_id(c2)
        ]
        if edges:
            self.write_edges(edges)

    def write_supersessions(self, supersessions: list[tuple[str, str]]):
        """Write SUPERSEDES edges."""
        edges = [
            {
                "source_int_id": self.id_mapper.get_int_id(newer),
                "target_int_id": self.id_mapper.get_int_id(older),
                "rel_type": "SUPERSEDES",
                "source_label": "Claim",
                "target_label": "Claim",
            }
            for newer, older in supersessions
            if self.id_mapper.has_id(newer) and self.id_mapper.has_id(older)
        ]
        if edges:
            self.write_edges(edges)

    def write_backup_for_edges(self, backup_edges: list[tuple[str, str]]):
        """Write BACKUP_FOR edges."""
        edges = [
            {
                "source_int_id": self.id_mapper.get_int_id(backup),
                "target_int_id": self.id_mapper.get_int_id(person),
                "rel_type": "BACKUP_FOR",
                "source_label": "Person",
                "target_label": "Person",
            }
            for backup, person in backup_edges
            if self.id_mapper.has_id(backup) and self.id_mapper.has_id(person)
        ]
        if edges:
            self.write_edges(edges)
