
from datetime import datetime
from typing import Any

from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.simulation_result import SimulationResult
from backend.app.simulation.engine import SimulationEngine


class ScenarioPlanningAgent:
    """Evaluates recovery plans using scenario and disruption information."""

    def __init__(self):
        self.simulation_engine = SimulationEngine()

    def assess(
        self,
        shipment: Shipment,
        plans: list[RecoveryPlan],
        current_time: datetime,
        sensing_assessment: dict[str, Any] | None = None,
    ) -> list[SimulationResult]:

        results = []

        disruption_detected = (
            sensing_assessment is not None
            and sensing_assessment.get("disruption_detected") is True
        )

        for plan in plans:
            result = self.simulation_engine.evaluate_plan(
                shipment=shipment,
                plan=plan,
                current_time=current_time,
            )

            if disruption_detected:
                result.assumptions.append(
                    "A disruption was identified by the Sensing Agent. "
                    "The plan-specific disruption delay is scenario-supplied "
                    "and is not calculated from disruption severity."
                )

            results.append(result)

        return results
