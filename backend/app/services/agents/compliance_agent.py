
class ComplianceAgent:
    """
    Reviews simulation and agent assessments.
    Flags incomplete information and enforces human review.
    """

    def assess(
        self,
        sensing_assessment: dict,
        logistics_assessment: dict,
        inventory_assessment: dict,
        simulation_results: list,
    ) -> dict:

        review_reasons = []
        plan_reviews = []

        # Review disruption information.
        if sensing_assessment.get("status") != (
            "scenario_disruption_assessed"
        ):
            review_reasons.append(
                "Disruption information is incomplete or unverified."
            )

        # Review logistics assessments.
        for assessment in logistics_assessment.get(
            "assessments", []
        ):
            if assessment["status"] == "requires_review":
                review_reasons.append(
                    f"Logistics review required for "
                    f"{assessment['plan_id']}."
                )

        # Review inventory assessments.
        for assessment in inventory_assessment.get(
            "assessments", []
        ):
            if assessment["status"] == "requires_review":
                review_reasons.append(
                    f"Inventory review required for "
                    f"{assessment['plan_id']}."
                )

        # Review simulation results.
        for result in simulation_results:
            if result.risk_level == "unknown":
                review_reasons.append(
                    f"Risk level is unknown for {result.plan_id}."
                )

            if result.data_freshness_status != "fresh":
                review_reasons.append(
                    f"Data freshness requires review for "
                    f"{result.plan_id}."
                )

            if not result.feasible:
                plan_reviews.append({
                    "plan_id": result.plan_id,
                    "status": "infeasible",
                    "reason": result.feasibility_reasons,
                })
            else:
                plan_reviews.append({
                    "plan_id": result.plan_id,
                    "status": "requires_human_approval",
                    "reason": [
                        "Feasibility checks do not establish "
                        "operational safety."
                    ],
                })

        return {
            "agent": "compliance_agent",
            "status": "human_review_required",
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "review_reasons": list(dict.fromkeys(review_reasons)),
            "plan_reviews": plan_reviews,
            "risk_uncertainty_preserved": True,
        }
