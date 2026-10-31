
from fastapi import FastAPI, HTTPException

from backend.app.models.simulation_request import SimulationRequest
from backend.app.models.simulation_result import SimulationResult
from backend.app.decision_engine import DecisionEngine

from backend.app.database.hana_repository import save_simulation
from backend.app.database.audit_repository import save_agent_audit_logs

from backend.app.services.agents.agent_orchestrator import AgentOrchestrator
from backend.app.models.decision_review import DecisionReviewRequest
from backend.app.database.review_repository import save_human_review


app = FastAPI(
    title="FORESIGHTX API",
    description="Supply-chain recovery decision support",
    version="0.4.0",
)

agent_orchestrator = AgentOrchestrator()
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
    """Coordinate agents, evaluate recovery plans and compare outcomes."""

    # 1. Execute the five-agent workflow
    agent_results = agent_orchestrator.run(
        shipment=request.shipment,
        plans=request.plans,
        current_time=request.current_time,
        disruption=(
            request.disruption.model_dump()
            if request.disruption is not None
            else None
        ),
    )

    # 2. Retrieve typed simulation results
    results = [
        SimulationResult.model_validate(item)
        for item in agent_results["scenario_planning"]["simulation_results"]
    ]

    # 3. Rank recovery plans
    decision = decision_engine.rank_plans(
        results,
        request.plans,
    )

    # 4. Save simulation and decision data to SAP HANA
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

    # 5. Save agent execution audit records
    audit_persistence = save_agent_audit_logs(
        shipment_id=request.shipment.shipment_id,
        agent_workflow=agent_results,
    )

    # 6. Return the complete assessment
    return {
        "shipment_id": request.shipment.shipment_id,
        "agent_workflow": agent_results,
        "simulation_results": [
            result.model_dump()
            for result in results
        ],
        "decision": decision,
        "persistence": persistence,
        "audit_persistence": audit_persistence,
    }
@app.post(
    "/decisions/review",
    tags=["Decision Passport"],
)
def review_decision(request: DecisionReviewRequest):
    """Record a human approval or rejection."""

    try:
        result = save_human_review(
            shipment_id=request.shipment_id,
            decision_id=request.decision_id,
            selected_plan_id=request.selected_plan_id,
            action=request.action,
            reviewer_role=request.reviewer_role,
            comments=request.comments,
            uncertainty_acknowledged=(
                request.uncertainty_acknowledged
            ),
        )

        return {
            "message": "Human review recorded successfully.",
            "review": result,
            "automatic_execution": False,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to save the human review.",
        )
