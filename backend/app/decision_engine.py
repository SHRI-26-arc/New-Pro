
from backend.app.models.simulation_result import SimulationResult


class DecisionEngine:
    """Ranks recovery plans using transparent downstream impact rules."""

    def calculate_downstream_impact(
        self,
        plan,
    ) -> dict:
        """
        Calculate a preliminary 0-100 downstream impact score.

        Delay: 5 points per 30 minutes, capped at 40.
        Priority: low=5, medium=10, high=20, critical=30.
        Known downstream reserve breach: 30 points.

        Missing information is reported separately and is not
        treated as evidence of low risk.
        """

        delay_points = 0
        priority_points = 0
        reserve_breach_points = 0
        missing_information = []
        warnings = []

        if not plan.downstream_impact_assessed:
            missing_information.append(
                "Downstream impact has not been explicitly assessed."
            )
            
        if plan.affects_other_shipment:
            delay_points = min(
                40,
                (plan.downstream_delay_minutes / 30) * 5,
            )

            priority_scores = {
                "low": 5,
                "medium": 10,
                "high": 20,
                "critical": 30,
            }

            if plan.downstream_priority is None:
                missing_information.append(
                    "Affected shipment priority is unknown."
                )
            else:
                priority_points = priority_scores[
                    plan.downstream_priority
                ]

            if not plan.affected_shipment_id:
                missing_information.append(
                    "Affected shipment ID is unknown."
                )

            if not plan.affected_destination:
                missing_information.append(
                    "Affected destination is unknown."
                )

            if plan.downstream_delay_minutes > 0:
                warnings.append(
                    f"Potential downstream delay: "
                    f"{plan.downstream_delay_minutes} minutes."
                )

            if plan.downstream_priority in ("high", "critical"):
                warnings.append(
                    "The affected shipment has high or critical "
                    "priority and requires human review."
                )

        if plan.downstream_reserve_breach:
            reserve_breach_points = 30
            warnings.append(
                "The plan causes a downstream inventory reserve breach."
            )

        score = min(
            100,
            round(
                delay_points
                + priority_points
                + reserve_breach_points
            ),
        )

        return {
            "score": score,
            "score_band": (
                "low" if score < 25
                else "moderate" if score < 50
                else "high" if score < 75
                else "very_high"
            ),
            "components": {
                "delay_points": round(delay_points, 2),
                "priority_points": priority_points,
                "reserve_breach_points": reserve_breach_points,
            },
            "missing_information": missing_information,
            "warnings": warnings,
            "score_complete": len(missing_information) == 0,
            "scoring_note": (
                "Prototype heuristic, not a validated clinical "
                "or operational risk measure."
            ),
        }

    def rank_plans(
        self,
        results: list[SimulationResult],
        plans: list | None = None,
    ) -> dict:
        """Exclude infeasible plans and rank remaining candidates."""

        if not results:
            return {
                "status": "no_plans",
                "recommended_plan_id": None,
                "recommendation_reason": (
                    "No recovery plans were provided."
                ),
                "ranked_plans": [],
                "human_approval_required": True,
            }

        plan_by_id = {
            plan.plan_id: plan
            for plan in (plans or [])
        }

        candidates = []
        excluded = []
        review_required = []

        for result in results:
            plan = plan_by_id.get(result.plan_id)
            reasons = list(result.feasibility_reasons)

            if plan is None:
                impact = {
                    "score": 0,
                    "score_band": "unknown",
                    "components": {},
                    "missing_information": [
                        "Recovery-plan inputs are unavailable; "
                        "downstream impact could not be calculated."
                    ],
                    "warnings": [
                        "Do not interpret the missing score as zero risk."
                    ],
                    "score_complete": False,
                    "scoring_note": (
                        "Impact score unavailable because plan inputs "
                        "were not supplied to the decision engine."
                    ),
                }
            else:
                impact = self.calculate_downstream_impact(plan)

                if plan.downstream_reserve_breach:
                    reasons.append(
                        "The plan causes a downstream inventory "
                        "reserve breach."
                    )

            entry = {
                "plan_id": result.plan_id,
                "plan_name": result.plan_name,
                "feasible": result.feasible and not reasons,
                "delay_minutes": result.delay_minutes,
                "additional_cost": result.additional_cost,
                "risk_level": result.risk_level,
                "data_freshness_status": result.data_freshness_status,
                "reasons": reasons,
                "downstream_impact": impact,
                "downstream_warnings": impact["warnings"],
            }

            if not result.feasible or reasons:
                excluded.append(entry)
            elif (
                not impact["score_complete"]
                or result.data_freshness_status != "fresh"
            ):
                review_required.append(entry)
            else:
                candidates.append(entry)

        if not candidates and review_required:
            return {
                "status": "human_review_required",
                "recommended_plan_id": None,
                "recommendation_reason": (
                    "No fully assessed candidate is available for "
                    "automatic recommendation. Human review is required."
                ),
                "ranked_plans": [],
                "excluded_plans": excluded,
                "review_required_plans": review_required,
                "human_approval_required": True,
                "warning": (
                    "Missing or incomplete downstream information must "
                    "not be interpreted as evidence of low risk."
                ),
            }

        if not candidates:
            return {
                "status": "no_feasible_option",
                "recommended_plan_id": None,
                "recommendation_reason": (
                    "No plan passed the feasibility and downstream "
                    "reserve checks. Human review is required."
                ),
                "ranked_plans": [],
                "excluded_plans": excluded,
                "human_approval_required": True,
                "warning": (
                    "Do not dispatch based on this result alone."
                ),
            }

        # Lower downstream impact is preferred. Then compare delivery
        # delay, additional cost, and plan ID for deterministic ranking.
        candidates.sort(
            key=lambda item: (
                item["downstream_impact"]["score"],
                item["delay_minutes"],
                item["additional_cost"],
                item["plan_id"],
            )
        )

        for rank, item in enumerate(candidates, start=1):
            item["rank"] = rank

        best = candidates[0]
        impact = best["downstream_impact"]
        
        reason = (
            f"{best['plan_name']} is the highest-ranked eligible candidate "
            "based on the available scenario inputs. "
            "Its overall risk level remains unknown and requires "
            "human assessment before action."
        )

        if not impact["score_complete"]:
            reason += (
                " Its impact score is incomplete because information "
                "is missing; human review is required."
            )

        return {
            "status": "candidate_selected",
            "recommended_plan_id": best["plan_id"],
            "recommendation_reason": reason,
            "ranking_rule": (
                "Lowest downstream impact score first, then lowest "
                "delivery delay, lowest additional cost, and plan ID."
            ),
            "ranked_plans": candidates,
            "excluded_plans": excluded,
            "review_required_plans": review_required,
            "human_approval_required": True,
            "warning": (
                "Scores are preliminary heuristics based on supplied "
                "scenario inputs. They are not validated risk "
                "measurements, and missing data does not mean safety."
            ),
        }
