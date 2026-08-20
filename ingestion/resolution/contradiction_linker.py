"""
BLACKOUT Contradiction Linker - Link CONTRADICTS and SUPERSEDES edges between claims
"""

from typing import Any


class ContradictionLinker:
    """Link claims that contradict or supersede each other."""

    def __init__(self):
        self.contradictions: list[dict[str, str]] = []
        self.supersessions: list[dict[str, str]] = []

    def link(self, claims: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
        """
        Analyze claims and link contradictions/supersessions.

        Returns:
            Dict with 'contradictions' and 'supersessions' lists
        """
        # Group claims by topic (using simple keyword matching for now)
        topic_groups: dict[str, list[dict[str, Any]]] = {}

        for claim in claims:
            # Simple topic extraction from claim text
            topic = self._extract_topic(claim.get("text_summary", ""))
            topic_groups.setdefault(topic, []).append(claim)

        # Within each topic group, find contradictions and supersessions
        for topic, group in topic_groups.items():
            for i, claim1 in enumerate(group):
                for claim2 in group[i + 1:]:
                    self._analyze_pair(claim1, claim2)

        return {
            "contradictions": self.contradictions,
            "supersessions": self.supersessions,
        }

    def _extract_topic(self, text: str) -> str:
        """Extract a simple topic from claim text."""
        text_lower = text.lower()

        # Topic keywords
        topics = {
            "pricing": ["price", "pricing", "cost", "discount", "rate"],
            "policy": ["policy", "rule", "guideline", "procedure"],
            "architecture": ["architecture", "system", "design", "infrastructure"],
            "ownership": ["owner", "responsible", "accountable", "lead"],
            "timeline": ["deadline", "timeline", "schedule", "date"],
            "decision": ["decision", "decided", "agreed", "approved"],
        }

        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                return topic

        return "general"

    def _analyze_pair(self, claim1: dict[str, Any], claim2: dict[str, Any]):
        """Analyze a pair of claims for contradiction or supersession."""
        text1 = claim1.get("text_summary", "").lower()
        text2 = claim2.get("text_summary", "").lower()

        # Check for supersession language
        supersession_keywords = [
            "updated", "corrected", "revised", "supersedes", "replaces",
            "new policy", "changed to", "now", "previously", "was",
        ]

        has_supersession1 = any(kw in text1 for kw in supersession_keywords)
        has_supersession2 = any(kw in text2 for kw in supersession_keywords)

        # If one claims to update the other
        if has_supersession1 and not has_supersession2:
            self.supersessions.append({
                "newer_id": claim1["id"],
                "older_id": claim2["id"],
            })
            return
        elif has_supersession2 and not has_supersession1:
            self.supersessions.append({
                "newer_id": claim2["id"],
                "older_id": claim1["id"],
            })
            return

        # Check for contradiction (opposite values on same topic)
        contradiction_pairs = [
            ("yes", "no"), ("true", "false"), ("approved", "rejected"),
            ("increase", "decrease"), ("allow", "deny"), ("should", "should not"),
            ("will", "will not"), ("can", "cannot"),
        ]

        for pos, neg in contradiction_pairs:
            if (pos in text1 and neg in text2) or (neg in text1 and pos in text2):
                self.contradictions.append({
                    "claim1_id": claim1["id"],
                    "claim2_id": claim2["id"],
                })
                return

        # Check for conflicting numbers
        import re
        numbers1 = set(re.findall(r'\d+\.?\d*', text1))
        numbers2 = set(re.findall(r'\d+\.?\d*', text2))

        # If same topic but different specific numbers (and both have numbers)
        if numbers1 and numbers2 and numbers1 != numbers2:
            # Simple heuristic: if numbers are different and topic is specific
            if len(numbers1) == 1 and len(numbers2) == 1:
                self.contradictions.append({
                    "claim1_id": claim1["id"],
                    "claim2_id": claim2["id"],
                })
