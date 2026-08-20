"""
BLACKOUT Recovery Optimizer - Greedy set-cover for recovery plan

Generates ranked recovery actions based on blast radius analysis.
"""

from typing import Any


def optimize_recovery(
    orphaned_claims: list[dict[str, Any]],
    candidate_actions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Greedy set-cover algorithm for recovery plan.

    Args:
        orphaned_claims: List of orphaned claim dicts with 'id' field
        candidate_actions: List of candidate repair actions, each with:
            - action: str (description of the action)
            - covers: set of claim IDs this action would restore
            - description: str (human-readable description)

    Returns:
        Ranked list of actions to take, sorted by impact
    """
    remaining = set(c["id"] for c in orphaned_claims)
    plan = []

    while remaining and candidate_actions:
        best = None
        best_coverage = 0

        for action in candidate_actions:
            coverage = len(action.get("covers", set()) & remaining)
            if coverage > best_coverage:
                best = action
                best_coverage = coverage

        if best is None or best_coverage == 0:
            break

        plan.append({
            "action": best["action"],
            "description": best["description"],
            "claimsRestored": best_coverage,
            "claimsCovered": list(best.get("covers", set()) & remaining),
        })

        remaining -= best.get("covers", set())
        candidate_actions.remove(best)

    return plan


def generate_candidate_actions(orphaned_claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate candidate recovery actions for orphaned claims."""
    actions = []

    for claim in orphaned_claims:
        claim_text = claim.get("text_summary", "")[:60]
        claim_id = claim.get("id", "unknown")

        # Action 1: Document the claim in Confluence
        actions.append({
            "action": f"Document in Confluence",
            "description": f"Create a Confluence page documenting: '{claim_text}...' to add a second evidence source",
            "covers": {claim_id},
        })

        # Action 2: Schedule cross-training session
        actions.append({
            "action": f"Schedule cross-training",
            "description": f"Have another team member learn this knowledge area to create redundancy",
            "covers": {claim_id},
        })

        # Action 3: Add backup assignment
        actions.append({
            "action": f"Assign knowledge backup",
            "description": f"Formally assign a backup person for this knowledge area",
            "covers": {claim_id},
        })

    return actions
