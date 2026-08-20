"""
BLACKOUT Pipeline Orchestrator - Runs the full ingestion pipeline
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

from ingestion.sources import (
    slack_loader,
    confluence_loader,
    github_loader,
    gmail_loader,
    linear_loader,
    drive_loader,
    hubspot_loader,
    fireflies_loader,
    jira_loader,
)
from ingestion.extraction.claim_extractor import ClaimExtractor
from ingestion.resolution.entity_resolver import EntityResolver
from ingestion.resolution.contradiction_linker import ContradictionLinker
from ingestion.graph_writer import GraphWriter


# Source loaders mapping
LOADERS = {
    "slack": slack_loader,
    "confluence": confluence_loader,
    "github": github_loader,
    "gmail": gmail_loader,
    "linear": linear_loader,
    "drive": drive_loader,
    "hubspot": hubspot_loader,
    "fireflies": fireflies_loader,
    "jira": jira_loader,
}


def run_pipeline(
    data_dir: str,
    graph_uri: str,
    auth_token: str,
    anthropic_api_key: str,
    max_records_per_source: int = 100,
):
    """
    Run the full ingestion pipeline.

    Args:
        data_dir: Path to the dataset directory
        graph_uri: HydraDB Bolt URI
        auth_token: HydraDB auth token
        anthropic_api_key: Anthropic API key for Claude
        max_records_per_source: Max records to process per source (for testing)
    """
    print("=" * 60)
    print("BLACKOUT Ingestion Pipeline")
    print("=" * 60)

    # Initialize components
    writer = GraphWriter(graph_uri, auth_token)
    extractor = ClaimExtractor(anthropic_api_key)
    resolver = EntityResolver()
    linker = ContradictionLinker()

    data_path = Path(data_dir)

    # Step 1: Run schema
    print("\n[1/6] Running schema...")
    schema_path = Path(__file__).parent / "schema.cypher"
    if schema_path.exists():
        writer.run_schema(str(schema_path))
        print("  Schema applied successfully")

    # Step 2: Load all sources
    print("\n[2/6] Loading sources...")
    all_records = []

    for source_name, loader in LOADERS.items():
        source_path = data_path / source_name
        if source_path.exists():
            print(f"  Loading {source_name}...")
            records = loader.load(str(source_path))
            # Limit records for testing
            records = records[:max_records_per_source]
            all_records.extend(records)
            print(f"    Loaded {len(records)} records")
        else:
            print(f"  Skipping {source_name} (path not found: {source_path})")

    print(f"  Total records: {len(all_records)}")

    # Step 3: Extract persons for entity resolution
    print("\n[3/6] Running entity resolution...")
    for record in all_records:
        if record.get("author_raw"):
            resolver.add_raw_person({
                "name": record["author_raw"],
                "source_system": record["source_system"],
                "email": "",  # Would need to parse from raw data
                "slack_handle": record["author_raw"] if record["source_system"] == "slack" else "",
                "github_username": record["author_raw"] if record["source_system"] == "github" else "",
            })

    canonical_persons = resolver.resolve()
    print(f"  Resolved {len(canonical_persons)} canonical persons")

    # Write persons to graph
    writer.batch_write_persons(canonical_persons)

    # Step 4: Extract claims using Claude
    print("\n[4/6] Extracting claims with Claude...")
    extracted_claims = extractor.extract_batch(all_records)
    print(f"  Extracted {len(extracted_claims)} claims")

    # Create evidence map (source_record_id -> node ID)
    evidence_map = {}
    for record in all_records:
        evidence_map[record.get("id", "")] = record.get("id", "")

    # Create claim nodes
    claim_nodes = extractor.create_claim_nodes(extracted_claims, evidence_map)

    # Create decision nodes
    decision_nodes, claim_decision_links = extractor.create_decision_nodes(claim_nodes)
    print(f"  Created {len(decision_nodes)} decisions")

    # Step 5: Link contradictions
    print("\n[5/6] Linking contradictions...")
    link_results = linker.link(claim_nodes)
    print(f"  Found {len(link_results['contradictions'])} contradictions")
    print(f"  Found {len(link_results['supersessions'])} supersessions")

    # Step 6: Write to graph
    print("\n[6/6] Writing to HydraDB...")
    writer.batch_write_claims(claim_nodes)
    writer.batch_write_decisions(decision_nodes)
    writer.write_claim_decision_links(claim_decision_links)

    if link_results["contradictions"]:
        writer.write_contradictions(link_results["contradictions"])
    if link_results["supersessions"]:
        writer.write_supersessions(link_results["supersessions"])

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"  Persons: {len(canonical_persons)}")
    print(f"  Claims: {len(claim_nodes)}")
    print(f"  Decisions: {len(decision_nodes)}")
    print(f"  Contradictions: {len(link_results['contradictions'])}")
    print("=" * 60)

    writer.close()


if __name__ == "__main__":
    import sys

    data_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    graph_uri = os.getenv("HYDRADB_BOLT_URI", "neo4j://localhost:7687")
    auth_token = os.getenv("HYDRADB_AUTH_TOKEN", "local-development-token-32-bytes")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)

    run_pipeline(data_dir, graph_uri, auth_token, anthropic_api_key)
