"""
BLACKOUT API Schemas - Pydantic request/response models
"""

from pydantic import BaseModel
from typing import Optional, Any


class SimulateRequest(BaseModel):
    targetType: str  # "person", "source", or "document"
    targetId: str


class SimulateResponse(BaseModel):
    orphanedClaims: list[dict[str, Any]]
    unverifiableDecisions: list[dict[str, Any]]
    atRiskSystems: list[dict[str, Any]]
    resilienceScoreBefore: float
    resilienceScoreAfter: float


class RecoverRequest(BaseModel):
    targetType: str  # "person", "source", or "document"
    targetId: str


class RecoveryAction(BaseModel):
    action: str
    description: str
    claimsRestored: int
    claimsCovered: list[str]


class RecoverResponse(BaseModel):
    plan: list[RecoveryAction]


class CrossTrainingResponse(BaseModel):
    recommendations: list[dict[str, Any]]


class ResilienceResponse(BaseModel):
    score: float
    breakdown: dict[str, Any]
