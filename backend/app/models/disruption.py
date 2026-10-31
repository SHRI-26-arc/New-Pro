
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class Disruption(BaseModel):
    """Scenario-supplied supply-chain disruption information."""

    model_config = ConfigDict(extra="forbid")

    disruption_type: str = Field(min_length=2)
    description: str = Field(min_length=5)
    severity: Literal["low", "medium", "high", "critical"]
    affected_location: str | None = None
    reported_at: str | None = None
    data_source: str = "scenario_supplied"
