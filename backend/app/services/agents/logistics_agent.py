
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.shipment import Shipment


class LogisticsAgent:
    """
    Assesses transport-related information
    supplied in recovery plans.

    This agent does not access live GPS or traffic feeds.
    """

    def assess(
        self,
        shipment: Shipment,
        plans: list[RecoveryPlan],
    ) -> dict:

        assessments = []

        for plan in plans:
            findings = []
            status = "requires_review"

            if plan.strategy == "reroute_original_vehicle":
                findings.append(
                    "Original vehicle rerouting is proposed."
                )

                status = "scenario_data_only"

            elif plan.strategy == "alternate_vehicle":

                if not plan.alternate_vehicle_id:
                    findings.append(
                        "Alternate vehicle ID is missing."
                    )

                if plan.alternate_vehicle_available is None:
                    findings.append(
                        "Vehicle availability is unknown."
                    )
                elif not plan.alternate_vehicle_available:
                    findings.append(
                        "Alternate vehicle is reported unavailable."
                    )

                if plan.alternate_vehicle_eligible is None:
                    findings.append(
                        "Vehicle eligibility is unknown."
                    )
                elif not plan.alternate_vehicle_eligible:
                    findings.append(
                        "Vehicle eligibility check failed."
                    )

                if plan.alternate_vehicle_capacity_units is None:
                    findings.append(
                        "Vehicle capacity is unknown."
                    )
                elif (
                    plan.alternate_vehicle_capacity_units
                    < shipment.quantity
                ):
                    findings.append(
                        "Vehicle capacity is insufficient."
                    )

                if not findings:
                    findings.append(
                        "Supplied vehicle details pass basic checks; "
                        "physical availability must still be verified."
                    )
                    status = "basic_checks_passed"

            else:
                findings.append(
                    "This recovery strategy does not specify "
                    "an alternate transport vehicle."
                )

                status = "not_applicable"

            assessments.append({
                "agent": "logistics_agent",
                "plan_id": plan.plan_id,
                "strategy": plan.strategy,
                "status": status,
                "findings": findings,
                "estimated_travel_minutes": (
                    plan.estimated_travel_minutes
                ),
                "additional_cost": plan.additional_cost,
                "data_source": "scenario_supplied",
            })

        return {
            "agent": "logistics_agent",
            "assessment_count": len(assessments),
            "assessments": assessments,
            "live_data_verified": False,
        }
