
from backend.app.decision_engine import DecisionEngine
from backend.app.models.simulation_result import SimulationResult
from backend.app.models.recovery_plan import RecoveryPlan


def test_recommendation_does_not_claim_unknown_risk_is_low():
    engine = DecisionEngine()

    plan = RecoveryPlan(
        plan_id="PLAN-TEST",
        plan_name="Test Recovery Plan",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=60,
        additional_cost=500,
        downstream_impact_assessed=True,
    )

    result = SimulationResult(
        plan_id="PLAN-TEST",
        plan_name="Test Recovery Plan",
        feasible=True,
        estimated_arrival_minutes=60,
        delay_minutes=0,
        additional_cost=500,
        risk_level="unknown",
        data_freshness_status="fresh",
    )

    decision = engine.rank_plans(
        results=[result],
        plans=[plan],
    )

    reason = decision["recommendation_reason"].lower()

    assert decision["recommended_plan_id"] == "PLAN-TEST"
    assert "unknown" in reason
    assert "human assessment" in reason
    assert "low risk" not in reason
