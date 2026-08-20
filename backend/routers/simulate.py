"""
BLACKOUT Simulate Router - POST /simulate endpoint
"""

from fastapi import APIRouter
from schemas import SimulateRequest, SimulateResponse
from db import get_driver
from services.blast_radius import simulate_removal

router = APIRouter(prefix="/simulate", tags=["simulate"])


@router.post("", response_model=SimulateResponse)
async def simulate(request: SimulateRequest):
    """Simulate removing a node from the graph."""
    driver = get_driver()
    try:
        result = await simulate_removal(
            target_type=request.targetType,
            target_id=request.targetId,
            driver=driver,
        )
        return SimulateResponse(**result)
    finally:
        driver.close()
