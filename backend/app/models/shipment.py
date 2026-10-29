
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, model_validator


class Shipment(BaseModel):
    """Represents a shipment that may be affected by a disruption."""

    model_config = ConfigDict(extra="forbid")

    shipment_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)

    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)

    quantity: int = Field(gt=0)

    temperature_min_c: float
    temperature_max_c: float

    departure_time: datetime
    deadline: datetime

    priority: Literal["low", "medium", "high", "critical"]

    @model_validator(mode="after")
    def check_temperature_range(self):
        if self.temperature_min_c > self.temperature_max_c:
            raise ValueError(
                "Minimum temperature cannot exceed maximum temperature"
            )

        if self.deadline < self.departure_time:
            raise ValueError(
                "Deadline cannot be earlier than departure time"
            )

        return self
