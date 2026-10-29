
from datetime import datetime, timedelta

from backend.app.models.shipment import Shipment
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.simulation.engine import SimulationEngine



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
