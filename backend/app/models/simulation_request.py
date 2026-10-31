
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.disruption import Disruption


class SimulationRequest(BaseModel):
    """Input required to evaluate recovery plans."""

    model_config = ConfigDict(extra="forbid")

    shipment: Shipment
    plans: list[RecoveryPlan] = Field(min_length=1)
    current_time: datetime
    disruption: Disruption | None = None
