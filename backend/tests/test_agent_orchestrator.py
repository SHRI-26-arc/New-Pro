from datetime import datetime, timezone

from backend.app.services.agents.agent_orchestrator import AgentOrchestrator
from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan


def test_all_agents_execute_successfully():

    shipment = Shipment(
        shipment_id="FX-AGENT-TEST-001",
        product_name="Temperature-sensitive IV Medicine",
        origin="Bengaluru Warehouse",
        destination="Apollo Hospital Bengaluru",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=datetime(2026, 10, 31, 8, 0, tzinfo=timezone.utc),
        deadline=datetime(2026, 10, 31, 14, 0, tzinfo=timezone.utc),
        priority="critical",
    )

    plans = [
        RecoveryPlan(
            plan_id="PLAN-001",
            plan_name="Original Vehicle Reroute",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=120,
            additional_cost=500,
            data_updated_at=datetime.now(timezone.utc),
        )
    ]

    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        shipment=shipment,
        plans=plans,
        current_time=datetime(2026, 10, 31, 9, 0, tzinfo=timezone.utc),
    )

    assert len(result["agents_executed"]) == 5

    assert result["sensing"]["agent"] == "sensing_agent"
    assert result["logistics"]["agent"] == "logistics_agent"
    assert result["inventory"]["agent"] == "inventory_agent"
    assert result["scenario_planning"]["agent"] == "scenario_planning_agent"
    assert result["compliance"]["status"] == "human_review_required"

    assert result["compliance"]["human_approval_required"] is True
    assert result["compliance"]["automatic_execution_allowed"] is False

    assert result["scenario_planning"]["plans_evaluated"] == 1