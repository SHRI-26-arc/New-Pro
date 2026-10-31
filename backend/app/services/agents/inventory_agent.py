
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.shipment import Shipment


class InventoryAgent:
    """
    Assesses inventory availability and reserve constraints
    using scenario-supplied information.
    """

    def assess(
        self,
        shipment: Shipment,
        plans: list[RecoveryPlan],
    ) -> dict:

        assessments = []

        for plan in plans:
            findings = []
            status = "not_applicable"
            inventory_remaining = None

            if plan.strategy == "use_nearby_inventory":
                status = "requires_review"

                if not plan.inventory_location:
                    findings.append(
                        "Inventory location is missing."
                    )

                if plan.inventory_units_available is None:
                    findings.append(
                        "Available inventory quantity is unknown."
                    )
                else:
                    inventory_remaining = (
                        plan.inventory_units_available
                        - shipment.quantity
                    )

                    if inventory_remaining < 0:
                        findings.append(
                            "Available inventory is insufficient."
                        )
                    elif plan.inventory_min_reserve is None:
                        findings.append(
                            "Minimum inventory reserve is unknown."
                        )
                    elif (
                        inventory_remaining
                        < plan.inventory_min_reserve
                    ):
                        findings.append(
                            "Proposed withdrawal would breach "
                            "the minimum inventory reserve."
                        )

                if not findings:
                    findings.append(
                        "Supplied inventory passes basic quantity "
                        "and reserve checks; physical stock must "
                        "still be verified."
                    )
                    status = "basic_checks_passed"

            else:
                findings.append(
                    "This recovery strategy does not use "
                    "nearby inventory."
                )

            assessments.append({
                "agent": "inventory_agent",
                "plan_id": plan.plan_id,
                "status": status,
                "inventory_location": plan.inventory_location,
                "inventory_units_available": (
                    plan.inventory_units_available
                ),
                "inventory_remaining": inventory_remaining,
                "minimum_reserve": plan.inventory_min_reserve,
                "findings": findings,
                "data_source": "scenario_supplied",
            })

        return {
            "agent": "inventory_agent",
            "assessment_count": len(assessments),
            "assessments": assessments,
            "live_inventory_verified": False,
        }
