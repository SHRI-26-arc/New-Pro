
from typing import Literal
from datetime import datetime

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
    # Additional delay caused by the disruption.
    # None means unknown; 0 means explicitly no additional delay.
    disruption_delay_minutes: int | None = Field(
        default=None,
        ge=0,
    )
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

    # Downstream impact: effects on other shipments or hospitals
    affects_other_shipment: bool = False
    downstream_impact_assessed: bool = False
    affected_shipment_id: str | None = None
    affected_destination: str | None = None

    downstream_delay_minutes: int = Field(
        default=0,
        ge=0,
    )
    downstream_priority: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] | None = None

    # Set true only when the scenario establishes a reserve breach.
    downstream_reserve_breach: bool = False

    description: str = ""
    # Timestamp indicating when recovery-plan data was last updated.
    data_updated_at: datetime | None = None
