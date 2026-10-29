
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class SimulationResult(BaseModel):
    """Calculated outcome of evaluating one recovery plan."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(min_length=1)
    plan_name: str = Field(min_length=1)

    feasible: bool
    feasibility_reasons: list[str] = Field(default_factory=list)

    estimated_arrival_minutes: int = Field(ge=0)
    delay_minutes: int = Field(ge=0)

    additional_cost: float = Field(ge=0)

    inventory_remaining: int | None = Field(default=None, ge=0)

    risk_level: Literal["low", "medium", "high", "critical", "unknown"]

    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
