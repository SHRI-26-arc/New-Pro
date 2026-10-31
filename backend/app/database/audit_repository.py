
import json
from uuid import uuid4

from backend.app.database.hana_connection import get_hana_connection


def save_agent_audit_logs(
    shipment_id: str,
    agent_workflow: dict,
):
    """Save agent execution records in SAP HANA."""

    connection = None
    cursor = None
    saved_count = 0

    agent_names = [
        "sensing",
        "logistics",
        "inventory",
        "scenario_planning",
        "compliance",
    ]

    try:
        connection = get_hana_connection()
        cursor = connection.cursor()

        for agent_key in agent_names:
            assessment = agent_workflow.get(agent_key)

            if not assessment:
                continue

            agent_name = assessment.get(
                "agent",
                f"{agent_key}_agent",
            )

            status = assessment.get(
                "status",
                "unknown",
            )

            data_source = assessment.get(
                "data_source",
                "scenario_supplied",
            )

            cursor.execute(
                """
                INSERT INTO FORESIGHTX_AUDIT_LOG (
                    AUDIT_ID,
                    SHIPMENT_ID,
                    PLAN_ID,
                    AGENT_NAME,
                    EVENT_TYPE,
                    STATUS,
                    DETAILS,
                    DATA_SOURCE
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    shipment_id,
                    None,
                    agent_name,
                    "agent_assessment",
                    status,
                    json.dumps(assessment, default=str),
                    data_source,
                ),
            )

            saved_count += 1

        connection.commit()

        return {
            "saved": True,
            "shipment_id": shipment_id,
            "audit_records_saved": saved_count,
        }

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
