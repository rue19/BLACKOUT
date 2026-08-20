"""
BLACKOUT Recover Router - POST /recover endpoint
"""

from fastapi import APIRouter
from schemas import RecoverRequest, RecoverResponse, RecoveryAction
from services.blast_radius import simulate_removal
from services.recovery_optimizer import optimize_recovery, generate_candidate_actions
from db import get_driver

router = APIRouter(prefix="/recover", tags=["recover"])


@router.post("", response_model=RecoverResponse)
async def recover(request: RecoverRequest):
    """Generate a ranked recovery plan for a simulated removal."""
    driver = get_driver()
    try:
        result = await simulate_removal(
            target_type=request.targetType,
            target_id=request.targetId,
            driver=driver,
        )
    finally:
        driver.close()

    orphaned_claims = result.get("orphanedClaims", [])
    candidate_actions = generate_candidate_actions(orphaned_claims)
    plan = optimize_recovery(orphaned_claims, candidate_actions)

    return RecoverResponse(
        plan=[RecoveryAction(**action) for action in plan]
    )
