
from datetime import datetime, timedelta

from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.simulation.engine import SimulationEngine
from backend.app.decision_engine import DecisionEngine
from backend.app.models.simulation_result import SimulationResult



def test_late_plan_is_flagged_without_automatic_rejection():
    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="TRK-104",
        product_name="Temperature-sensitive IV medicine",
        origin="Distribution Center",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-1",
        plan_name="Reroute original vehicle",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=300,
        additional_cost=500,
    )

    result = SimulationEngine().evaluate_plan(
        shipment=shipment,
        plan=plan,
        current_time=departure,
    )

    assert result.estimated_arrival_minutes == 300
    assert result.delay_minutes == 60
    assert result.feasible is True
    assert result.risk_level == "unknown"
    assert any(
        "after the delivery deadline" in warning
        for warning in result.warnings
    )

def test_alternate_vehicle_requires_vehicle_id():
    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="TRK-104",
        product_name="Temperature-sensitive IV medicine",
        origin="Distribution Center",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-2",
        plan_name="Use alternate vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=120,
        additional_cost=800,
    )

    result = SimulationEngine().evaluate_plan(
        shipment=shipment,
        plan=plan,
        current_time=departure,
    )

    assert result.feasible is False
    assert any(
        "alternate vehicle" in reason.lower()
        for reason in result.feasibility_reasons
    )

def test_inventory_plan_rejected_when_reserve_would_be_breached():
    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="TRK-104",
        product_name="Temperature-sensitive IV medicine",
        origin="Distribution Center",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-3",
        plan_name="Use nearby inventory",
        strategy="use_nearby_inventory",
        estimated_travel_minutes=30,
        additional_cost=300,
        inventory_location="Nearby Depot",
        inventory_units_available=250,
        inventory_min_reserve=75,
    )

    result = SimulationEngine().evaluate_plan(
        shipment=shipment,
        plan=plan,
        current_time=departure,
    )

    assert result.inventory_remaining == 50
    assert result.feasible is False
    assert any(
        "reserve requirement" in reason.lower()
        for reason in result.feasibility_reasons
    )


def test_inventory_plan_passes_when_reserve_is_preserved():
    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="TRK-104",
        product_name="Temperature-sensitive IV medicine",
        origin="Distribution Center",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-4",
        plan_name="Use sufficient nearby inventory",
        strategy="use_nearby_inventory",
        estimated_travel_minutes=30,
        additional_cost=300,
        inventory_location="Nearby Depot",
        inventory_units_available=300,
        inventory_min_reserve=75,
    )

    result = SimulationEngine().evaluate_plan(
        shipment=shipment,
        plan=plan,
        current_time=departure,
    )

    assert result.inventory_remaining == 100
    assert result.feasible is True

def test_alternate_vehicle_rejected_when_unavailable():
    engine = SimulationEngine()

    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="SHIP-101",
        product_name="IV Medicine",
        origin="Depot A",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-UNAVAILABLE",
        plan_name="Unavailable vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=120,
        additional_cost=500,
        alternate_vehicle_id="VAN-204",
        alternate_vehicle_available=False,
        alternate_vehicle_eligible=True,
        alternate_vehicle_capacity_units=250,
    )

    result = engine.evaluate_plan(shipment, plan, departure)

    assert result.feasible is False
    assert any(
        "unavailable" in reason.lower()
        for reason in result.feasibility_reasons
    )


def test_alternate_vehicle_rejected_when_capacity_is_insufficient():
    engine = SimulationEngine()

    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="SHIP-102",
        product_name="IV Medicine",
        origin="Depot A",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-LOW-CAPACITY",
        plan_name="Insufficient vehicle capacity",
        strategy="alternate_vehicle",
        estimated_travel_minutes=120,
        additional_cost=500,
        alternate_vehicle_id="VAN-205",
        alternate_vehicle_available=True,
        alternate_vehicle_eligible=True,
        alternate_vehicle_capacity_units=150,
    )

    result = engine.evaluate_plan(shipment, plan, departure)

    assert result.feasible is False
    assert any(
        "cannot carry" in reason.lower()
        for reason in result.feasibility_reasons
    )


def test_alternate_vehicle_passes_basic_checks():
    engine = SimulationEngine()

    departure = datetime(2026, 10, 29, 10, 0)

    shipment = Shipment(
        shipment_id="SHIP-103",
        product_name="IV Medicine",
        origin="Depot A",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=departure,
        deadline=departure + timedelta(hours=4),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-VALID",
        plan_name="Eligible alternate vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=120,
        additional_cost=500,
        alternate_vehicle_id="VAN-206",
        alternate_vehicle_available=True,
        alternate_vehicle_eligible=True,
        alternate_vehicle_capacity_units=250,
    )

    result = engine.evaluate_plan(shipment, plan, departure)

    assert result.feasible is True
    assert result.feasibility_reasons == []
    assert result.risk_level == "unknown"

def test_decision_engine_ranks_by_delay_then_cost():
    engine = DecisionEngine()

    results = [
        SimulationResult(
            plan_id="PLAN-B",
            plan_name="Cheaper but slower",
            feasible=True,
            feasibility_reasons=[],
            estimated_arrival_minutes=300,
            delay_minutes=60,
            additional_cost=100,
            risk_level="unknown",
            data_freshness_status="fresh",
        ),
        SimulationResult(
            plan_id="PLAN-A",
            plan_name="Faster but more expensive",
            feasible=True,
            feasibility_reasons=[],
            estimated_arrival_minutes=240,
            delay_minutes=0,
            additional_cost=500,
            risk_level="unknown",
            data_freshness_status="fresh",
        ),
        SimulationResult(
            plan_id="PLAN-C",
            plan_name="Same delay, lower cost",
            feasible=True,
            feasibility_reasons=[],
            estimated_arrival_minutes=240,
            delay_minutes=0,
            additional_cost=300,
            risk_level="unknown",
            data_freshness_status="fresh",
        ),
    ]
    plans = [
        RecoveryPlan(
            plan_id="PLAN-B",
            plan_name="Cheaper but slower",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=300,
            additional_cost=100,
            downstream_impact_assessed=True,
        ),
        RecoveryPlan(
            plan_id="PLAN-A",
            plan_name="Faster but more expensive",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=240,
            additional_cost=500,
            downstream_impact_assessed=True,
        ),
        RecoveryPlan(
            plan_id="PLAN-C",
            plan_name="Same delay, lower cost",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=240,
            additional_cost=300,
            downstream_impact_assessed=True,
        ),
    ]

    decision = engine.rank_plans(results, plans)

    assert decision["status"] == "candidate_selected"
    assert decision["recommended_plan_id"] == "PLAN-C"
    assert decision["ranked_plans"][0]["plan_id"] == "PLAN-C"
    assert decision["ranked_plans"][1]["plan_id"] == "PLAN-A"
    assert decision["ranked_plans"][2]["plan_id"] == "PLAN-B"
    assert decision["human_approval_required"] is True


def test_decision_engine_never_recommends_infeasible_plan():
    engine = DecisionEngine()

    results = [
        SimulationResult(
            plan_id="PLAN-FAST",
            plan_name="Fast but infeasible",
            feasible=False,
            feasibility_reasons=["Vehicle is unavailable."],
            estimated_arrival_minutes=120,
            delay_minutes=0,
            additional_cost=50,
            risk_level="unknown",
            data_freshness_status="fresh",
        ),
        SimulationResult(
            plan_id="PLAN-SLOW",
            plan_name="Feasible but late",
            feasible=True,
            feasibility_reasons=[],
            estimated_arrival_minutes=300,
            delay_minutes=60,
            additional_cost=200,
            risk_level="unknown",
            data_freshness_status="fresh",
        ),
    ]

    plans = [
        RecoveryPlan(
            plan_id="PLAN-FAST",
            plan_name="Fast but infeasible",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=120,
            additional_cost=50,
            downstream_impact_assessed=True,
        ),
        RecoveryPlan(
            plan_id="PLAN-SLOW",
            plan_name="Feasible but late",
            strategy="reroute_original_vehicle",
            estimated_travel_minutes=300,
            additional_cost=200,
            downstream_impact_assessed=True,
        ),
    ]

    decision = engine.rank_plans(results, plans)

    assert decision["recommended_plan_id"] == "PLAN-SLOW"
    assert decision["excluded_plans"][0]["plan_id"] == "PLAN-FAST"


def test_decision_engine_returns_no_feasible_option():
    engine = DecisionEngine()

    results = [
        SimulationResult(
            plan_id="PLAN-1",
            plan_name="Unavailable vehicle",
            feasible=False,
            feasibility_reasons=["Vehicle is unavailable."],
            estimated_arrival_minutes=120,
            delay_minutes=0,
            additional_cost=100,
            risk_level="unknown",
        ),
    ]

    decision = engine.rank_plans(results)

    assert decision["status"] == "no_feasible_option"
    assert decision["recommended_plan_id"] is None
    assert decision["human_approval_required"] is True

def test_critical_downstream_delay_adds_warning():
    from backend.app.decision_engine import DecisionEngine

    plan = RecoveryPlan(
        plan_id="PLAN-CRITICAL",
        plan_name="Use Alternate Vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=150,
        additional_cost=1200,
        alternate_vehicle_id="VAN-02",
        alternate_vehicle_available=True,
        alternate_vehicle_eligible=True,
        alternate_vehicle_capacity_units=300,
        affects_other_shipment=True,
        affected_shipment_id="MED-002",
        affected_destination="Hospital B",
        downstream_delay_minutes=90,
        downstream_priority="critical",
        downstream_impact_assessed=True,
    )

    result = SimulationResult(
        plan_id="PLAN-CRITICAL",
        plan_name="Use Alternate Vehicle",
        feasible=True,
        feasibility_reasons=[],
        estimated_arrival_minutes=225,
        delay_minutes=0,
        additional_cost=1200,
        risk_level="unknown",
        data_freshness_status="fresh",
    )

    decision = DecisionEngine().rank_plans(
        [result],
        [plan],
    )

    assert decision["recommended_plan_id"] == "PLAN-CRITICAL"

    ranked_plan = decision["ranked_plans"][0]

    assert any(
        "90 minutes" in warning
        for warning in ranked_plan["downstream_warnings"]
    )

    assert any(
        "critical priority" in warning
        for warning in ranked_plan["downstream_warnings"]
    )


def test_downstream_reserve_breach_excludes_plan():
    from backend.app.decision_engine import DecisionEngine

    plan = RecoveryPlan(
        plan_id="PLAN-BREACH",
        plan_name="Use Nearby Inventory",
        strategy="use_nearby_inventory",
        estimated_travel_minutes=60,
        additional_cost=800,
        inventory_location="Regional Hospital Depot",
        inventory_units_available=260,
        inventory_min_reserve=100,
        downstream_reserve_breach=True,
    )

    result = SimulationResult(
        plan_id="PLAN-BREACH",
        plan_name="Use Nearby Inventory",
        feasible=True,
        feasibility_reasons=[],
        estimated_arrival_minutes=135,
        delay_minutes=0,
        additional_cost=800,
        risk_level="unknown",
    )

    decision = DecisionEngine().rank_plans(
        [result],
        [plan],
    )

    assert decision["status"] == "no_feasible_option"
    assert decision["recommended_plan_id"] is None
    assert decision["human_approval_required"] is True
    assert any(
        "downstream inventory reserve breach" in reason
        for reason in decision["excluded_plans"][0]["reasons"]
    )


def test_no_feasible_option_when_all_plans_are_excluded():
    from backend.app.decision_engine import DecisionEngine

    result = SimulationResult(
        plan_id="PLAN-INVALID",
        plan_name="Unavailable Vehicle",
        feasible=False,
        feasibility_reasons=["Vehicle is unavailable."],
        estimated_arrival_minutes=200,
        delay_minutes=0,
        additional_cost=500,
        risk_level="unknown",
    )

    decision = DecisionEngine().rank_plans([result], [])

    assert decision["status"] == "no_feasible_option"
    assert decision["recommended_plan_id"] is None
    assert decision["ranked_plans"] == []
    assert decision["human_approval_required"] is True

def test_downstream_impact_score_for_critical_delay():
    from backend.app.decision_engine import DecisionEngine
    from backend.app.models.recovery_plan import RecoveryPlan

    plan = RecoveryPlan(
        plan_id="PLAN-SCORE",
        plan_name="Alternate Vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=150,
        additional_cost=1200,
        alternate_vehicle_id="VAN-02",
        alternate_vehicle_available=True,
        alternate_vehicle_eligible=True,
        alternate_vehicle_capacity_units=300,
        affects_other_shipment=True,
        downstream_impact_assessed=True,
        affected_shipment_id="MED-002",
        affected_destination="Hospital B",
        downstream_delay_minutes=90,
        downstream_priority="critical",
    )

    impact = DecisionEngine().calculate_downstream_impact(plan)

    assert impact["score"] == 45
    assert impact["score_band"] == "moderate"
    assert impact["components"]["delay_points"] == 15
    assert impact["components"]["priority_points"] == 30
    assert impact["components"]["reserve_breach_points"] == 0
    assert impact["score_complete"] is True


def test_missing_downstream_priority_marks_score_incomplete():
    from backend.app.decision_engine import DecisionEngine
    from backend.app.models.recovery_plan import RecoveryPlan

    plan = RecoveryPlan(
        plan_id="PLAN-UNKNOWN",
        plan_name="Alternate Vehicle",
        strategy="alternate_vehicle",
        estimated_travel_minutes=150,
        additional_cost=1200,
        affects_other_shipment=True,
        affected_shipment_id="MED-002",
        affected_destination="Hospital B",
        downstream_delay_minutes=60,
        downstream_priority=None,
    )

    impact = DecisionEngine().calculate_downstream_impact(plan)

    assert impact["score_complete"] is False
    assert impact["score"] == 10
    assert any(
        "priority is unknown" in item
        for item in impact["missing_information"]
    )



def test_unassessed_plan_cannot_outrank_assessed_candidate():
    from backend.app.decision_engine import DecisionEngine
    from backend.app.models.recovery_plan import RecoveryPlan

    assessed_plan = RecoveryPlan(
        plan_id="PLAN-ASSESSED",
        plan_name="Assessed Recovery",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=180,
        additional_cost=500,
        downstream_impact_assessed=True,
    )

    unassessed_plan = RecoveryPlan(
        plan_id="PLAN-UNKNOWN",
        plan_name="Unknown Downstream Impact",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=60,
        additional_cost=100,
        downstream_impact_assessed=False,
    )

    assessed_result = SimulationResult(
        plan_id="PLAN-ASSESSED",
        plan_name="Assessed Recovery",
        feasible=True,
        feasibility_reasons=[],
        estimated_arrival_minutes=180,
        delay_minutes=30,
        additional_cost=500,
        risk_level="unknown",
        data_freshness_status="fresh",
    )

    unassessed_result = SimulationResult(
        plan_id="PLAN-UNKNOWN",
        plan_name="Unknown Downstream Impact",
        feasible=True,
        feasibility_reasons=[],
        estimated_arrival_minutes=60,
        delay_minutes=0,
        additional_cost=100,
        risk_level="unknown",
    )

    decision = DecisionEngine().rank_plans(
        [unassessed_result, assessed_result],
        [unassessed_plan, assessed_plan],
    )

    assert decision["status"] == "candidate_selected"
    assert decision["recommended_plan_id"] == "PLAN-ASSESSED"
    assert len(decision["ranked_plans"]) == 1
    assert (
        decision["review_required_plans"][0]["plan_id"]
        == "PLAN-UNKNOWN"
    )
    assert decision["human_approval_required"] is True

def test_no_recommendation_when_all_feasible_plans_are_unassessed():
    from backend.app.decision_engine import DecisionEngine
    from backend.app.models.recovery_plan import RecoveryPlan

    plan = RecoveryPlan(
        plan_id="PLAN-UNKNOWN",
        plan_name="Unassessed Recovery",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=120,
        additional_cost=300,
        downstream_impact_assessed=False,
    )

    result = SimulationResult(
        plan_id="PLAN-UNKNOWN",
        plan_name="Unassessed Recovery",
        feasible=True,
        feasibility_reasons=[],
        estimated_arrival_minutes=120,
        delay_minutes=0,
        additional_cost=300,
        risk_level="unknown",
    )

    decision = DecisionEngine().rank_plans([result], [plan])

    assert decision["status"] == "human_review_required"
    assert decision["recommended_plan_id"] is None
    assert decision["ranked_plans"] == []
    assert len(decision["review_required_plans"]) == 1
    assert decision["human_approval_required"] is True
from datetime import datetime, timedelta, timezone


def evaluate_data_freshness(data_updated_at):
    from backend.app.models.shipment import Shipment
    from backend.app.models.recovery_plan import RecoveryPlan
    from backend.app.simulation.engine import SimulationEngine

    current_time = datetime(
        2026, 10, 28, 10, 0, tzinfo=timezone.utc
    )

    shipment = Shipment(
        shipment_id="SHIP-TEST",
        product_name="Temperature-sensitive IV Medicine",
        origin="Warehouse A",
        destination="Hospital A",
        quantity=200,
        temperature_min_c=2,
        temperature_max_c=8,
        departure_time=datetime(
            2026, 10, 28, 9, 0, tzinfo=timezone.utc
        ),
        deadline=datetime(
            2026, 10, 28, 13, 0, tzinfo=timezone.utc
        ),
        priority="critical",
    )

    plan = RecoveryPlan(
        plan_id="PLAN-TEST",
        plan_name="Test Recovery Plan",
        strategy="reroute_original_vehicle",
        estimated_travel_minutes=120,
        additional_cost=500,
        downstream_impact_assessed=True,
        data_updated_at=data_updated_at,
    )

    return SimulationEngine().evaluate_plan(
        shipment=shipment,
        plan=plan,
        current_time=current_time,
    )


def test_fresh_data_is_detected():
    current_time = datetime(
        2026, 10, 28, 10, 0, tzinfo=timezone.utc
    )

    result = evaluate_data_freshness(
        current_time - timedelta(minutes=10)
    )

    assert result.data_freshness_status == "fresh"


def test_stale_data_is_detected():
    current_time = datetime(
        2026, 10, 28, 10, 0, tzinfo=timezone.utc
    )

    result = evaluate_data_freshness(
        current_time - timedelta(minutes=45)
    )

    assert result.data_freshness_status == "stale"
    assert any(
        "older than 30 minutes" in warning
        for warning in result.warnings
    )


def test_missing_timestamp_is_unknown():
    result = evaluate_data_freshness(None)

    assert result.data_freshness_status == "unknown"
    assert any(
        "freshness is unknown" in warning
        for warning in result.warnings
    )


def test_future_timestamp_is_unknown():
    current_time = datetime(
        2026, 10, 28, 10, 0, tzinfo=timezone.utc
    )

    result = evaluate_data_freshness(
        current_time + timedelta(minutes=5)
    )

    assert result.data_freshness_status == "unknown"
    assert any(
        "timestamp is in the future" in warning
        for warning in result.warnings
    )