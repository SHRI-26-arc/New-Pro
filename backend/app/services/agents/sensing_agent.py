
from typing import Any


class SensingAgent:
    """
    Classifies disruption information supplied by a scenario.
    Does not independently monitor live external systems.
    """

    def assess(
        self,
        disruption: dict[str, Any] | None,
    ) -> dict[str, Any]:

        if not disruption:
            return {
                "agent": "sensing_agent",
                "status": "insufficient_information",
                "disruption_detected": False,
                "disruption_type": None,
                "severity": "unknown",
                "findings": [
                    "No disruption information was supplied."
                ],
                "data_source": "not_provided",
                "live_monitoring": False,
            }

        disruption_type = disruption.get("disruption_type")
        description = disruption.get("description")
        severity = disruption.get("severity")

        findings = []

        if not disruption_type:
            findings.append("Disruption type is missing.")

        if not description:
            findings.append("Disruption description is missing.")

        if severity not in {
            "low",
            "medium",
            "high",
            "critical",
        }:
            findings.append(
                "Disruption severity is missing or invalid."
            )

        if findings:
            status = "requires_review"
            detected = False
            severity = "unknown"
        else:
            status = "scenario_disruption_assessed"
            detected = True
            findings.append(
                "Disruption details were classified using "
                "scenario-provided information."
            )

        return {
            "agent": "sensing_agent",
            "status": status,
            "disruption_detected": detected,
            "disruption_type": disruption_type,
            "description": description,
            "severity": severity,
            "findings": findings,
            "data_source": "scenario_supplied",
            "live_monitoring": False,
        }
