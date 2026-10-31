
from fastapi import FastAPI

from backend.app.models.simulation_request import SimulationRequest
from backend.app.models.simulation_result import SimulationResult
from backend.app.simulation.engine import SimulationEngine
from backend.app.decision_engine import DecisionEngine
from backend.app.database.hana_repository import save_simulation

app = FastAPI(
    title="FORESIGHTX API",
    description="Supply-chain recovery decision support",
    version="0.3.0",
)

simulation_engine = SimulationEngine()
decision_engine = DecisionEngine()


@app.get("/")
def root():
    return {
        "message": "FORESIGHTX backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "FORESIGHTX",
    }


@app.post(
    "/simulate",
    tags=["Simulation"],
)
def simulate_recovery_plans(request: SimulationRequest):
    """Evaluate recovery plans and compare their outcomes."""

    results: list[SimulationResult] = []

    for plan in request.plans:
        result = simulation_engine.evaluate_plan(
            shipment=request.shipment,
            plan=plan,
            current_time=request.current_time,
        )
        results.append(result)

    decision = decision_engine.rank_plans(
        results,
        request.plans,
    )
    persistence = save_simulation(
        shipment=request.shipment.model_dump(),
        plans=[
            plan.model_dump()
            for plan in request.plans
        ],
        results=[
            result.model_dump()
            for result in results
        ],
        decision=decision,
    )
    return {
        "shipment_id": request.shipment.shipment_id,
        "simulation_results": [
            result.model_dump() for result in results
        ],
        "decision": decision,
        "persistence": persistence,
    }
