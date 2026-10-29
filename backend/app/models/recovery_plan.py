
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class RecoveryPlan(BaseModel):
    """Represents a proposed response to a supply-chain disruption."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(min_length=1)
    plan_name: str = Field(min_length=1)

    strategy: Literal[
        "reroute_original_vehicle",
        "alternate_vehicle",
        "use_nearby_inventory",
    ]

    estimated_travel_minutes: int = Field(ge=0)
    additional_cost: float = Field(ge=0)

    # Alternate vehicle details
    alternate_vehicle_id: str | None = None
    alternate_vehicle_available: bool | None = None
    alternate_vehicle_eligible: bool | None = None
    alternate_vehicle_capacity_units: int | None = Field(
        default=None,
        ge=0,
    )

    # Nearby inventory details
    inventory_location: str | None = None
    inventory_units_available: int | None = Field(
        default=None,
        ge=0,
    )
    inventory_min_reserve: int | None = Field(
        default=None,
        ge=0,
    )

    description: str = ""
