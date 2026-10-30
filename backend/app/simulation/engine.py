
from datetime import datetime, timedelta

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

        # Check whether recovery-plan data is recent enough.
        data_freshness_status = "unknown"

        if plan.data_updated_at is None:
            warnings.append(
                "Recovery-plan data freshness is unknown "
                "because no update timestamp was provided."
            )
        else:
            updated_at = plan.data_updated_at
            reference_time = current_time

            # Normalize timezone handling for comparison.
            if updated_at.tzinfo is None and reference_time.tzinfo is not None:
                updated_at = updated_at.replace(tzinfo=reference_time.tzinfo)
            elif updated_at.tzinfo is not None and reference_time.tzinfo is None:
                reference_time = reference_time.replace(tzinfo=updated_at.tzinfo)

            data_age = reference_time - updated_at

            if data_age < timedelta(0):
                warnings.append(
                    "Data update timestamp is in the future; "
                    "freshness cannot be verified."
                )
            elif data_age <= timedelta(minutes=30):
                data_freshness_status = "fresh"
            else:
                data_freshness_status = "stale"
                warnings.append(
                    "Recovery-plan data is older than 30 minutes "
                    "and requires verification."
                )

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
            data_freshness_status=data_freshness_status,
            assumptions=assumptions,
            warnings=warnings,
        )
