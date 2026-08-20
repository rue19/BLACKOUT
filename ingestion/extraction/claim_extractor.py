"""
BLACKOUT Claim Extractor - LLM-assisted Claim/Decision extraction using Claude
"""

import json
import anthropic
from typing import Any
from .prompts import EXTRACTION_PROMPT


class ClaimExtractor:
    """Extract claims and decisions from unstructured text using Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def extract_from_text(
        self, text: str, source_system: str, record_id: str
    ) -> list[dict[str, Any]]:
        """Extract claims from a single text document."""
        if not text or len(text.strip()) < 50:
            return []

        prompt = EXTRACTION_PROMPT.format(
            source_system=source_system, content=text[:8000]  # Limit to avoid token limits
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse JSON response
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            claims = json.loads(response_text.strip())

            # Add source metadata
            for claim in claims:
                claim["source_system"] = source_system
                claim["source_record_id"] = record_id

            return claims

        except json.JSONDecodeError:
            print(f"Failed to parse Claude response for {record_id}")
            return []
        except Exception as e:
            print(f"Error extracting claims from {record_id}: {e}")
            return []

    def extract_batch(
        self, records: list[dict[str, Any]], batch_size: int = 10
    ) -> list[dict[str, Any]]:
        """Extract claims from a batch of records."""
        all_claims = []

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            for record in batch:
                text = record.get("text", "")
                source_system = record.get("source_system", "unknown")
                record_id = record.get("id", "")

                claims = self.extract_from_text(text, source_system, record_id)
                all_claims.extend(claims)

        return all_claims

    def create_claim_nodes(
        self, extracted_claims: list[dict[str, Any]], evidence_map: dict[str, str]
    ) -> list[dict[str, Any]]:
        """
        Convert extracted claims to graph-ready claim nodes.

        Args:
            extracted_claims: Claims from extract_batch
            evidence_map: Mapping from source_record_id to evidence node ID
        """
        claim_nodes = []

        for i, claim in enumerate(extracted_claims):
            claim_id = f"claim-{claim.get('source_record_id', '')}-{i}"

            claim_nodes.append({
                "id": claim_id,
                "text_summary": claim.get("claim_text", ""),
                "extracted_at": claim.get("timestamp"),
                "status": "active",
                "evidence_id": evidence_map.get(claim.get("source_record_id", ""), ""),
                "author_raw": claim.get("author_raw", ""),
                "type": claim.get("type", "claim"),
                "supersedes_hint": claim.get("supersedes_hint", False),
            })

        return claim_nodes

    def create_decision_nodes(
        self, claim_nodes: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """
        Group claims by topic to create Decision nodes.

        Returns:
            Tuple of (decision_nodes, claim_decision_links)
        """
        decisions = []
        links = []

        # Group by simple topic
        topic_claims: dict[str, list[dict[str, Any]]] = {}
        for claim in claim_nodes:
            if claim.get("type") == "decision":
                topic = self._simple_topic(claim.get("text_summary", ""))
                topic_claims.setdefault(topic, []).append(claim)

        for topic, claims in topic_claims.items():
            if len(claims) >= 1:  # Even single claims can be decisions
                decision_id = f"decision-{topic}"
                decisions.append({
                    "id": decision_id,
                    "title": f"Decision: {topic.replace('_', ' ').title()}",
                    "decided_at": claims[0].get("extracted_at"),
                })

                for claim in claims:
                    links.append({
                        "claim_id": claim["id"],
                        "decision_id": decision_id,
                    })

        return decisions, links

    def _simple_topic(self, text: str) -> str:
        """Extract a simple topic from claim text."""
        text_lower = text.lower()

        topics = {
            "pricing": ["price", "pricing", "cost", "discount", "rate"],
            "policy": ["policy", "rule", "guideline", "procedure"],
            "architecture": ["architecture", "system", "design", "infrastructure"],
            "ownership": ["owner", "responsible", "accountable", "lead"],
            "timeline": ["deadline", "timeline", "schedule", "date"],
        }

        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                return topic

        return "general"
