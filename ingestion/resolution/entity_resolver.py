"""
BLACKOUT Entity Resolution - Person canonicalization across sources
"""

from rapidfuzz import fuzz
from typing import Any


class EntityResolver:
    """Resolve person references across multiple sources into canonical Person nodes."""

    def __init__(self, merge_threshold: float = 0.75):
        self.merge_threshold = merge_threshold
        self.raw_persons: list[dict[str, Any]] = []
        self.canonical_persons: list[dict[str, Any]] = []

    def add_raw_person(self, person: dict[str, Any]):
        """Add a raw person reference from any source."""
        self.raw_persons.append(person)

    def _compute_similarity(self, p1: dict[str, Any], p2: dict[str, Any]) -> float:
        """Compute similarity score between two person references."""
        score = 0.0
        weight_sum = 0.0

        # Exact email match (highest weight)
        if p1.get("email") and p2.get("email"):
            if p1["email"].lower() == p2["email"].lower():
                return 1.0

        # Name token similarity (weight: 0.4)
        if p1.get("name") and p2.get("name"):
            name_sim = fuzz.token_sort_ratio(p1["name"].lower(), p2["name"].lower()) / 100
            score += name_sim * 0.4
            weight_sum += 0.4

        # Slack handle / GitHub username match (weight: 0.3)
        for key in ["slack_handle", "github_username"]:
            if p1.get(key) and p2.get(key):
                if p1[key].lower() == p2[key].lower():
                    score += 0.3
                    weight_sum += 0.3
                    break

        # Email prefix match against name tokens (weight: 0.3)
        if p1.get("email") and p2.get("name"):
            prefix = p1["email"].split("@")[0].lower()
            name_tokens = p2["name"].lower().split()
            if any(token in prefix for token in name_tokens):
                score += 0.3
                weight_sum += 0.3
        elif p2.get("email") and p1.get("name"):
            prefix = p2["email"].split("@")[0].lower()
            name_tokens = p1["name"].lower().split()
            if any(token in prefix for token in name_tokens):
                score += 0.3
                weight_sum += 0.3

        return score / weight_sum if weight_sum > 0 else 0.0

    def _blocking(self) -> list[list[dict[str, Any]]]:
        """Group raw persons by potential matches to avoid O(n^2) comparison."""
        blocks: dict[str, list[dict[str, Any]]] = {}

        for person in self.raw_persons:
            # Block by email domain
            email = person.get("email", "")
            if "@" in email:
                domain = email.split("@")[1].lower()
                blocks.setdefault(f"domain:{domain}", []).append(person)

            # Block by normalized name tokens
            name = person.get("name", "")
            if name:
                tokens = sorted(set(name.lower().split()))
                if tokens:
                    blocks.setdefault(f"tokens:{'_'.join(tokens[:2])}", []).append(person)

            # Block by source system (for same-source dedup)
            source = person.get("source_system", "")
            if source and name:
                blocks.setdefault(f"source:{source}:{name.lower()}", []).append(person)

        return list(blocks.values())

    def resolve(self) -> list[dict[str, Any]]:
        """Run entity resolution and return canonical persons."""
        blocks = self._blocking()
        merge_map: dict[int, int] = {}  # person_index -> canonical_index

        for block in blocks:
            for i, p1 in enumerate(block):
                idx1 = self.raw_persons.index(p1)
                if idx1 in merge_map:
                    continue

                for p2 in block:
                    idx2 = self.raw_persons.index(p2)
                    if idx1 == idx2 or idx2 in merge_map:
                        continue

                    sim = self._compute_similarity(p1, p2)
                    if sim >= self.merge_threshold:
                        # Merge into the first one found
                        if idx1 not in merge_map:
                            merge_map[idx1] = idx1
                        merge_map[idx2] = idx1

        # Group persons by canonical ID
        groups: dict[int, list[dict[str, Any]]] = {}
        for idx, person in enumerate(self.raw_persons):
            canonical_idx = merge_map.get(idx, idx)
            groups.setdefault(canonical_idx, []).append(person)

        # Build canonical person nodes
        self.canonical_persons = []
        for canonical_idx, group in groups.items():
            primary = group[0]
            aliases = list(set(
                p.get("name", "") for p in group if p.get("name")
            ))

            # Compute confidence based on number of matching sources
            confidence = min(1.0, 0.5 + 0.1 * len(group))

            canonical = {
                "canonical_id": primary.get("email") or primary.get("slack_handle") or primary.get("name", "").replace(" ", "_").lower(),
                "name": primary.get("name", ""),
                "aliases": aliases,
                "resolved_confidence": confidence,
                "source_systems": list(set(p.get("source_system", "") for p in group)),
            }
            self.canonical_persons.append(canonical)

        return self.canonical_persons

    def get_canonical_id(self, raw_ref: dict[str, Any]) -> str | None:
        """Get canonical ID for a raw person reference after resolve() has been called."""
        for person in self.raw_persons:
            if (person.get("email") == raw_ref.get("email") or
                person.get("slack_handle") == raw_ref.get("slack_handle") or
                person.get("name") == raw_ref.get("name")):
                # Find which canonical this maps to
                idx = self.raw_persons.index(person)
                for canonical in self.canonical_persons:
                    if person.get("email", "").split("@")[0] in canonical.get("canonical_id", ""):
                        return canonical["canonical_id"]
        return None
