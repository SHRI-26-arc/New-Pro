import json
from uuid import uuid4

from backend.app.database.hana_connection import get_hana_connection


def save_simulation(
    shipment: dict,
    plans: list[dict],
    results: list[dict],
    decision: dict,
):
    """Save one FORESIGHTX simulation in SAP HANA."""

    connection = None
    cursor = None

    try:
        connection = get_hana_connection()
        cursor = connection.cursor()

        shipment_id = shipment["shipment_id"]

        # Match each plan with its simulation result.
        results_by_plan = {
            result["plan_id"]: result
            for result in results
        }

        # Remove previous records for this shipment so that
        # the same scenario can be run again safely.
        cursor.execute(
            """
            DELETE FROM FORESIGHTX_SIMULATION_RESULTS
            WHERE PLAN_ID IN (
                SELECT PLAN_ID
                FROM FORESIGHTX_RECOVERY_PLANS
                WHERE SHIPMENT_ID = ?
            )
            """,
            (shipment_id,),
        )

        cursor.execute(
            """
            DELETE FROM FORESIGHTX_RECOVERY_PLANS
            WHERE SHIPMENT_ID = ?
            """,
            (shipment_id,),
        )

        cursor.execute(
            """
            DELETE FROM FORESIGHTX_DECISIONS
            WHERE SHIPMENT_ID = ?
            """,
            (shipment_id,),
        )

        cursor.execute(
            """
            DELETE FROM FORESIGHTX_SHIPMENTS
            WHERE SHIPMENT_ID = ?
            """,
            (shipment_id,),
        )

        # 1. Save shipment.
        cursor.execute(
            """
            INSERT INTO FORESIGHTX_SHIPMENTS (
                SHIPMENT_ID, PRODUCT_NAME, ORIGIN, DESTINATION,
                QUANTITY, TEMPERATURE_MIN_C, TEMPERATURE_MAX_C,
                DEPARTURE_TIME, DEADLINE, PRIORITY
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                shipment_id,
                shipment["product_name"],
                shipment["origin"],
                shipment["destination"],
                shipment["quantity"],
                shipment["temperature_min_c"],
                shipment["temperature_max_c"],
                shipment["departure_time"],
                shipment["deadline"],
                shipment["priority"],
            ),
        )

        # 2. Save recovery plans.
        for plan in plans:
            result = results_by_plan.get(plan["plan_id"], {})

            cursor.execute(
                """
                INSERT INTO FORESIGHTX_RECOVERY_PLANS (
                    PLAN_ID, SHIPMENT_ID, PLAN_NAME, STRATEGY,
                    ESTIMATED_TRAVEL_MINUTES, ADDITIONAL_COST,
                    FEASIBLE, RISK_LEVEL, PLAN_PAYLOAD
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan["plan_id"],
                    shipment_id,
                    plan["plan_name"],
                    plan["strategy"],
                    plan["estimated_travel_minutes"],
                    plan["additional_cost"],
                    result.get("feasible"),
                    result.get("risk_level"),
                    json.dumps(plan, default=str),
                ),
            )

        # 3. Save simulation results.
        for result in results:
            cursor.execute(
                """
                INSERT INTO FORESIGHTX_SIMULATION_RESULTS (
                    RESULT_ID, PLAN_ID, ESTIMATED_ARRIVAL_MINUTES,
                    DELAY_MINUTES, ADDITIONAL_COST, RISK_LEVEL,
                    DATA_FRESHNESS_STATUS, RESULT_PAYLOAD
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    result["plan_id"],
                    result["estimated_arrival_minutes"],
                    result["delay_minutes"],
                    result["additional_cost"],
                    result["risk_level"],
                    result["data_freshness_status"],
                    json.dumps(result, default=str),
                ),
            )

        # 4. Save the decision.
        decision_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO FORESIGHTX_DECISIONS (
            DECISION_ID, SHIPMENT_ID, RECOMMENDED_PLAN_ID,
            DECISION_STATUS, RECOMMENDATION_REASON,
            HUMAN_APPROVAL_REQUIRED, DECISION_PAYLOAD
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                shipment_id,
                decision.get("recommended_plan_id"),
                decision.get("status", "human_review_required"),
                decision.get("recommendation_reason", ""),
                decision.get("human_approval_required", True),
                json.dumps(decision, default=str),
            ),
        )

        connection.commit()

        return {
            "saved": True,
            "shipment_id": shipment_id,
            "decision_id": decision_id,
            "plans_saved": len(plans),
            "results_saved": len(results),
            "decision_saved": True,
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