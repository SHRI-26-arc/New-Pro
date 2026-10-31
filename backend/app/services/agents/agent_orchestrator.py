from backend.app.services.agents.sensing_agent import SensingAgent
from backend.app.services.agents.logistics_agent import LogisticsAgent
from backend.app.services.agents.inventory_agent import InventoryAgent
from backend.app.services.agents.scenario_planning_agent import ScenarioPlanningAgent
from backend.app.services.agents.compliance_agent import ComplianceAgent


class AgentOrchestrator:

    def __init__(self):
        self.sensing_agent = SensingAgent()
        self.logistics_agent = LogisticsAgent()
        self.inventory_agent = InventoryAgent()
        self.scenario_agent = ScenarioPlanningAgent()
        self.compliance_agent = ComplianceAgent()

    def run(self, shipment, plans, current_time, disruption=None):

        # 1. Sensing Agent
        sensing_result = self.sensing_agent.assess(disruption)

        # 2. Logistics Agent
        logistics_result = self.logistics_agent.assess(
            shipment, plans
        )

        # 3. Inventory Agent
        inventory_result = self.inventory_agent.assess(
            shipment, plans
        )

        # 4. Scenario Planning Agent
        simulation_results = self.scenario_agent.assess(
            shipment=shipment,
            plans=plans,
            current_time=current_time,
            sensing_assessment=sensing_result,
        )

        scenario_result = {
            "agent": "scenario_planning_agent",
            "status": "simulation_completed",
            "plans_evaluated": len(simulation_results),
            "simulation_results": [
                result.model_dump()
                for result in simulation_results
            ],
            "data_source": "scenario_supplied",
            "simulation_engine": "FORESIGHTX SimulationEngine",
        }

        # 5. Compliance Agent
        compliance_result = self.compliance_agent.assess(
            sensing_assessment=sensing_result,
            logistics_assessment=logistics_result,
            inventory_assessment=inventory_result,
            simulation_results=simulation_results,
        )

        return {
            "workflow": "FORESIGHTX multi-agent assessment",
            "agents_executed": [
                "sensing_agent",
                "logistics_agent",
                "inventory_agent",
                "scenario_planning_agent",
                "compliance_agent",
            ],
            "sensing": sensing_result,
            "logistics": logistics_result,
            "inventory": inventory_result,
            "scenario_planning": scenario_result,
            "compliance": compliance_result,
        }