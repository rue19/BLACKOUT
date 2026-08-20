"""
BLACKOUT Hero Scenarios - Hand-authored guaranteed-to-land demo scenarios

Uses GraphWriter with integer IDs (HydraDB requirement).
"""

from ingestion.graph_writer import GraphWriter
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent.parent / ".env")


def seed_hero_scenarios(graph_uri: str, auth_token: str):
    """Seed the hero scenarios into HydraDB."""
    writer = GraphWriter(graph_uri, auth_token)

    print("Seeding hero scenarios...")

    # === Scenario 1: Single source of truth ===
    print("  [1/4] Payments decision (single source of truth)")
    writer.batch_write_persons([{"canonical_id": "sam@acme.com", "name": "Sam Ratnaparkhi"}])
    writer.batch_write_messages([{
        "id": "hero-slack-payments-001",
        "source_system": "slack",
        "text": "Decision: We are switching to Stripe for payment processing. Current PayPal integration will be deprecated by Q2.",
    }])
    writer.batch_write_decisions([{"id": "hero-decision-payments", "title": "Payment Processor Migration to Stripe"}])
    writer.batch_write_claims([{
        "id": "hero-claim-payments",
        "text_summary": "Acme Corp will migrate from PayPal to Stripe for payment processing by Q2 2026",
        "status": "active",
    }])
    writer.write_author_edges("sam@acme.com", ["hero-slack-payments-001"])
    writer.write_supports_edges("hero-slack-payments-001", ["hero-claim-payments"])
    writer.write_partof_edges(["hero-claim-payments"], "hero-decision-payments")

    # === Scenario 2: Contradiction between two sources ===
    print("  [2/4] Pricing contradiction (two sources)")
    writer.batch_write_persons([{"canonical_id": "priya@acme.com", "name": "Priya Patel"}])
    writer.batch_write_documents([{
        "id": "hero-doc-pricing",
        "title": "Pricing Strategy 2026",
        "source_system": "confluence",
    }])
    writer.batch_write_claims([{
        "id": "hero-claim-pricing-confluence",
        "text_summary": "Enterprise tier pricing is $500/month per seat",
        "status": "active",
    }])
    writer.batch_write_messages([{
        "id": "hero-slack-pricing-001",
        "source_system": "slack",
        "text": "Quick update: Enterprise pricing is now $450/month per seat, effective March 1.",
    }])
    writer.batch_write_claims([{
        "id": "hero-claim-pricing-slack",
        "text_summary": "Enterprise tier pricing is $450/month per seat",
        "status": "active",
    }])
    writer.batch_write_decisions([{"id": "hero-decision-pricing", "title": "Enterprise Pricing Strategy"}])
    writer.write_author_edges("priya@acme.com", ["hero-doc-pricing"], target_label="Document")
    writer.write_supports_edges("hero-doc-pricing", ["hero-claim-pricing-confluence"])
    writer.write_supports_edges("hero-slack-pricing-001", ["hero-claim-pricing-slack"])
    writer.write_contradictions([("hero-claim-pricing-confluence", "hero-claim-pricing-slack")])
    writer.write_partof_edges(["hero-claim-pricing-confluence"], "hero-decision-pricing")
    writer.write_partof_edges(["hero-claim-pricing-slack"], "hero-decision-pricing")

    # === Scenario 3: Person removal drops resilience score ===
    print("  [3/4] Alex's architecture decisions (unique knowledge)")
    writer.batch_write_persons([{"canonical_id": "alex@acme.com", "name": "Alex Chen"}])
    arch_messages = []
    for i in range(1, 6):
        msg_id = f"hero-slack-arch-{i:03d}"
        arch_messages.append({
            "id": msg_id,
            "source_system": "slack",
            "text": f"Architecture decision {i}: System component {i} will use "
                    + ["PostgreSQL", "Redis", "Kafka", "Kubernetes", "Prometheus"][i - 1],
        })
    writer.batch_write_messages(arch_messages)
    writer.write_author_edges("alex@acme.com", [m["id"] for m in arch_messages])

    # === Scenario 4: BACKUP_FOR relationship ===
    print("  [4/4] Jordan as backup for Sam")
    writer.batch_write_persons([{"canonical_id": "jordan@acme.com", "name": "Jordan Kim"}])
    writer.write_backup_for_edges([("jordan@acme.com", "sam@acme.com")])

    writer.close()
    print("Hero scenarios seeded successfully!")


if __name__ == "__main__":
    graph_uri = os.getenv("HYDRADB_BOLT_URI", "bolt://127.0.0.1:7687")
    auth_token = os.getenv("HYDRADB_AUTH_TOKEN", "local-dev-auth-token-32-characters-long")
    seed_hero_scenarios(graph_uri, auth_token)
