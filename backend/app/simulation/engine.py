
from datetime import datetime

from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.simulation_result import SimulationResult


class SimulationEngine:
    """Evaluates recovery plans against shipment requirements."""

    def evaluate_plan(
        self,
        shipment: Shipment,
        plan: RecoveryPlan,
        current_time: datetime,
    ) -> SimulationResult:

        assumptions = [
            "Travel time is an estimate supplied by the scenario.",
            "Arrival time is estimated from the simulation current time.",
            "Additional cost is supplied by the recovery plan.",
            "Vehicle and inventory details are supplied by the scenario "
            "and have not been independently verified.",
        ]

        warnings = []
        reasons = []
        inventory_remaining = None

        elapsed_minutes = max(
            0,
            int(
                (current_time - shipment.departure_time).total_seconds()
                / 60
            ),
        )

        estimated_arrival_minutes = (
            elapsed_minutes + plan.estimated_travel_minutes
        )

        deadline_minutes = int(
            (
                shipment.deadline - shipment.departure_time
            ).total_seconds()
            / 60
        )

        delay_minutes = max(
            0,
            estimated_arrival_minutes - deadline_minutes,
        )

        if delay_minutes > 0:
            warnings.append(
                f"Estimated arrival is {delay_minutes} minutes "
                "after the delivery deadline."
            )

        # Check alternate vehicle requirements.
        if plan.strategy == "alternate_vehicle":

            if not plan.alternate_vehicle_id:
                reasons.append(
                    "No alternate vehicle has been identified."
                )

            if plan.alternate_vehicle_available is None:
                reasons.append(
                    "Alternate vehicle availability is unknown."
                )
            elif not plan.alternate_vehicle_available:
                reasons.append(
                    "The alternate vehicle is unavailable."
                )

            if plan.alternate_vehicle_eligible is None:
                reasons.append(
                    "Alternate vehicle eligibility is unknown."
                )
            elif not plan.alternate_vehicle_eligible:
                reasons.append(
                    "The alternate vehicle is not eligible "
                    "to transport this shipment."
                )

            if plan.alternate_vehicle_capacity_units is None:
                reasons.append(
                    "Alternate vehicle carrying capacity is unknown."
                )
            elif (
                plan.alternate_vehicle_capacity_units
                < shipment.quantity
            ):
                reasons.append(
                    "The alternate vehicle cannot carry the "
                    "required shipment quantity."
                )

            if not reasons:
                warnings.append(
                    "Vehicle availability, eligibility, and capacity "
                    "were provided by the scenario and must be "
                    "verified before dispatch."
                )

        # Check nearby inventory requirements.
        elif plan.strategy == "use_nearby_inventory":

            if not plan.inventory_location:
                reasons.append(
                    "No nearby inventory location has been identified."
                )

            if plan.inventory_units_available is None:
                reasons.append(
                    "Nearby inventory availability is unknown."
                )
            else:
                inventory_remaining = (
                    plan.inventory_units_available - shipment.quantity
                )

                if inventory_remaining < 0:
                    reasons.append(
                        "Nearby inventory is insufficient "
                        "for this shipment."
                    )
                elif plan.inventory_min_reserve is None:
                    reasons.append(
                        "Minimum inventory reserve is unknown."
                    )
                elif (
                    inventory_remaining
                    < plan.inventory_min_reserve
                ):
                    reasons.append(
                        "Using this inventory would breach the "
                        "minimum reserve requirement."
                    )

        feasible = len(reasons) == 0

        risk_level = "unknown"

        warnings.append(
            "Risk remains unknown until validated risk inputs and "
            "downstream consequences are evaluated."
        )

        if feasible:
            warnings.append(
                "Basic feasibility checks passed; this does not confirm "
                "operational availability or overall safety."
            )

        return SimulationResult(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name,
            feasible=feasible,
            feasibility_reasons=reasons,
            estimated_arrival_minutes=estimated_arrival_minutes,
            delay_minutes=delay_minutes,
            additional_cost=plan.additional_cost,
            inventory_remaining=inventory_remaining,
            risk_level=risk_level,
            assumptions=assumptions,
            warnings=warnings,
        )
