from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DecisionReviewRequest(BaseModel):
    """Human approval or rejection of a FORESIGHTX decision."""

    model_config = ConfigDict(extra="forbid")

    shipment_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    selected_plan_id: str = Field(min_length=1)

    action: Literal["approve", "reject"]
    uncertainty_acknowledged: bool = False

    reviewer_role: str = Field(
        default="control_tower_analyst",
        min_length=2,
    )

    comments: str | None = None