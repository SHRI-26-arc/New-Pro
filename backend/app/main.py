
from fastapi import FastAPI

from backend.app.models.simulation_request import SimulationRequest
from backend.app.models.simulation_result import SimulationResult
from backend.app.simulation.engine import SimulationEngine


app = FastAPI(
    title="FORESIGHTX API",
    description="Supply-chain recovery decision support",
    version="0.2.0",
)

simulation_engine = SimulationEngine()


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
    response_model=list[SimulationResult],
    tags=["Simulation"],
)
def simulate_recovery_plans(request: SimulationRequest):
    """Evaluate each proposed recovery plan for a shipment."""

    results = []

    for plan in request.plans:
        result = simulation_engine.evaluate_plan(
            shipment=request.shipment,
            plan=plan,
            current_time=request.current_time,
        )
        results.append(result)

    return results
