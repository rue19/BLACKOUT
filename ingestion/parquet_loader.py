"""
BLACKOUT Parquet Loader - Load EnterpriseRAG-Bench parquet data into HydraDB

Reads from the HuggingFace parquet files and creates:
- Person nodes (extracted from content)
- Document/Message nodes (from source_type mapping)
- Claim nodes (simple extraction from content)
- Decision nodes (grouped from claims)
- Edges: AUTHORED, SUPPORTS, PART_OF
"""

import re
from typing import Any
from pathlib import Path

import pandas as pd

from ingestion.graph_writer import GraphWriter
from ingestion.id_mapper import IDMapper


# Source type to node label mapping
SOURCE_TYPE_LABELS = {
    "slack": "Message",
    "gmail": "Message",
    "fireflies": "Message",
    "confluence": "Document",
    "google_drive": "Document",
    "jira": "Document",
    "linear": "Document",
    "github": "Document",
    "hubspot": "Document",
}


def extract_persons_from_content(content: str, source_type: str) -> list[str]:
    """Extract person names/emails from document content."""
    persons = []

    # Extract email addresses
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', content)
    for email in emails:
        # Normalize email to canonical form
        email = email.lower().strip()
        if email not in persons and not email.endswith(('.png', '.jpg', '.gif')):
            persons.append(email)

    # Extract "Name (email)" patterns
    name_email = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)\s*\(([\w.+-]+@[\w-]+\.[\w.]+)\)', content)
    for name, email in name_email:
        email = email.lower().strip()
        if email not in persons:
            persons.append(email)

    return persons[:5]  # Limit to avoid too many nodes


def extract_simple_claims(content: str, doc_id: str, source_type: str) -> list[dict[str, Any]]:
    """Extract simple claims from document content using heuristics."""
    claims = []

    # Look for decision-like patterns
    decision_patterns = [
        r'(?:decided|decision|agreed|approved|confirmed)\s+(?:to|that)\s+(.{20,100})',
        r'(?:we will|we\'ll|going to)\s+(.{20,100})',
        r'(?:policy|rule|guideline)[:\s]+(.{20,100})',
        r'(?:pricing|price|cost)[:\s]+(.{20,100})',
        r'(?:deadline|due date|timeline)[:\s]+(.{20,100})',
    ]

    for pattern in decision_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches[:2]:  # Limit per pattern
            claim_text = match.strip()[:200]
            if len(claim_text) > 20:
                claims.append({
                    "id": f"claim-{doc_id}-{len(claims)}",
                    "text_summary": claim_text,
                    "status": "active",
                    "source_system": source_type,
                    "type": "claim",
                })

    # If no claims found, create a summary claim from the title
    if not claims and len(content) > 100:
        # Take first meaningful sentence
        sentences = re.split(r'[.!?]+', content)
        for sent in sentences:
            sent = sent.strip()
            if 20 < len(sent) < 200 and not sent.startswith(('#', '-', '*', 'http')):
                claims.append({
                    "id": f"claim-{doc_id}-0",
                    "text_summary": sent[:200],
                    "status": "active",
                    "source_system": source_type,
                    "type": "claim",
                })
                break

    return claims[:3]  # Max 3 claims per document


def load_parquet_dataset(
    parquet_path: str,
    writer: GraphWriter,
    max_documents: int = 5000,
    batch_size: int = 500,
) -> dict[str, Any]:
    """
    Load EnterpriseRAG-Bench parquet data into HydraDB.

    Args:
        parquet_path: Path to the test.parquet file
        writer: GraphWriter instance
        max_documents: Max documents to load (for demo)
        batch_size: Batch size for writes

    Returns:
        Stats dict
    """
    print(f"Loading parquet dataset from {parquet_path}")
    df = pd.read_parquet(parquet_path)
    print(f"Total documents: {len(df)}")

    # Sample if too many
    if len(df) > max_documents:
        n_sources = df['source_type'].nunique()
        per_source = max_documents // n_sources
        sampled_dfs = []
        for source, group in df.groupby('source_type'):
            sampled_dfs.append(group.sample(min(len(group), per_source), random_state=42))
        df = pd.concat(sampled_dfs)
        print(f"Sampled to {len(df)} documents")

    stats = {
        "total_documents": len(df),
        "persons": 0,
        "documents": 0,
        "claims": 0,
        "decisions": 0,
        "edges": 0,
    }

    # Process in batches
    all_persons = {}
    all_claims = []
    all_documents = []
    doc_source_map = {}  # Track source_type for each doc_id

    for idx, row in df.iterrows():
        doc_id = row['doc_id']
        source_type = row['source_type']
        title = row.get('title', '')
        content = row.get('content', '')

        # Determine node label
        label = SOURCE_TYPE_LABELS.get(source_type, "Document")
        doc_source_map[doc_id] = label

        # Create document/message node
        node_data = {
            "id": doc_id,
            "title": title[:200] if title else "",
            "source_system": source_type,
        }
        if label == "Message":
            node_data["text"] = content[:500] if content else ""

        all_documents.append((label, node_data))
        stats["documents"] += 1

        # Extract persons from content
        persons = extract_persons_from_content(content, source_type)
        for person_id in persons:
            if person_id not in all_persons:
                all_persons[person_id] = {
                    "canonical_id": person_id,
                    "name": person_id.split('@')[0].replace('.', ' ').title() if '@' in person_id else person_id,
                }

        # Extract simple claims
        claims = extract_simple_claims(content, doc_id, source_type)
        all_claims.extend([(doc_id, source_type, c) for c in claims])
        stats["claims"] += len(claims)

        # Progress indicator
        if (stats["documents"] % 1000) == 0:
            print(f"  Processed {stats['documents']} documents...")

    # Write persons
    print(f"\nWriting {len(all_persons)} persons...")
    if all_persons:
        writer.batch_write_persons(list(all_persons.values()), batch_size)
        stats["persons"] = len(all_persons)

    # Write documents/messages
    print(f"Writing {len(all_documents)} documents/messages...")
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i + batch_size]
        messages = [d for label, d in batch if label == "Message"]
        documents = [d for label, d in batch if label == "Document"]
        if messages:
            writer.batch_write_messages(messages, batch_size)
        if documents:
            writer.batch_write_documents(documents, batch_size)

    # Write claims and edges
    print(f"Writing {len(all_claims)} claims...")
    claim_nodes = []
    evidence_edges = []
    author_edges = []

    for doc_id, source_type, claim in all_claims:
        claim_nodes.append(claim)
        # SUPPORTS edge from document to claim
        src_label = doc_source_map.get(doc_id, "Document")
        evidence_edges.append((doc_id, claim["id"], src_label, "Claim"))

        # Try to link to a person
        content = df[df['doc_id'] == doc_id]['content'].iloc[0] if len(df[df['doc_id'] == doc_id]) > 0 else ""
        persons = extract_persons_from_content(content, source_type)
        if persons:
            target_label = doc_source_map.get(doc_id, "Document")
            author_edges.append((persons[0], doc_id, "Person", target_label))

    # Write claim nodes in batches
    for i in range(0, len(claim_nodes), batch_size):
        batch = claim_nodes[i:i + batch_size]
        writer.batch_write_claims(batch, batch_size)

    # Write SUPPORTS edges
    print(f"Writing {len(evidence_edges)} SUPPORTS edges...")
    edges_data = [
        {
            "source_int_id": writer.id_mapper.get_int_id(src),
            "target_int_id": writer.id_mapper.get_int_id(tgt),
            "rel_type": "SUPPORTS",
            "source_label": src_label,
            "target_label": tgt_label,
        }
        for src, tgt, src_label, tgt_label in evidence_edges
    ]
    if edges_data:
        writer.write_edges(edges_data, batch_size)

    # Write AUTHORED edges
    print(f"Writing {len(author_edges)} AUTHORED edges...")
    edges_data = [
        {
            "source_int_id": writer.id_mapper.get_int_id(person),
            "target_int_id": writer.id_mapper.get_int_id(node),
            "rel_type": "AUTHORED",
            "source_label": "Person",
            "target_label": node_label,
        }
        for person, node, _, node_label in author_edges
    ]
    if edges_data:
        writer.write_edges(edges_data, batch_size)

    stats["edges"] = len(evidence_edges) + len(author_edges)

    print(f"\n{'=' * 60}")
    print("Parquet ingestion complete!")
    print(f"  Documents: {stats['documents']}")
    print(f"  Persons: {stats['persons']}")
    print(f"  Claims: {stats['claims']}")
    print(f"  Edges: {stats['edges']}")
    print(f"{'=' * 60}")

    return stats


if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")

    parquet_path = sys.argv[1] if len(sys.argv) > 1 else "./data/EnterpriseRAG-Bench/data/documents/test.parquet"
    graph_uri = os.getenv("HYDRADB_BOLT_URI", "bolt://127.0.0.1:7687")
    auth_token = os.getenv("HYDRADB_AUTH_TOKEN", "local-development-token-32-bytes")
    max_docs = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    writer = GraphWriter(graph_uri, auth_token)
    try:
        stats = load_parquet_dataset(parquet_path, writer, max_documents=max_docs)
    finally:
        writer.close()
