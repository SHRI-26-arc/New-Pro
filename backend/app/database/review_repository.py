
import json
from uuid import uuid4

from backend.app.database.hana_connection import get_hana_connection


def save_human_review(
    shipment_id: str,
    decision_id: str,
    selected_plan_id: str,
    action: str,
    reviewer_role: str,
    comments: str | None = None,
    uncertainty_acknowledged: bool = False,
):
    """Save a human review and append an audit event."""

    connection = None
    cursor = None
    review_id = str(uuid4())

    try:
        connection = get_hana_connection()
        cursor = connection.cursor()

        # 0. Prevent duplicate reviews for the same decision.
        cursor.execute(
            """
            SELECT REVIEW_ID
            FROM FORESIGHTX_HUMAN_REVIEWS
            WHERE DECISION_ID = ?
            """,
            (decision_id,),
        )
        if cursor.fetchone() is not None:
            raise ValueError(
                "This decision has already been reviewed."
            )

        # 1. Verify the decision belongs to this shipment.
        cursor.execute(
            """
            SELECT DECISION_ID
            FROM FORESIGHTX_DECISIONS
            WHERE DECISION_ID = ? AND SHIPMENT_ID = ?
            """,
            (decision_id, shipment_id),
        )

        if cursor.fetchone() is None:
            raise ValueError(
                "Decision not found for the supplied shipment."
            )

        # 2. Verify the plan belongs to this shipment.
        cursor.execute(
            """
            SELECT PLAN_ID
            FROM FORESIGHTX_RECOVERY_PLANS
            WHERE PLAN_ID = ? AND SHIPMENT_ID = ?
            """,
            (selected_plan_id, shipment_id),
        )

        if cursor.fetchone() is None:
            raise ValueError(
                "Selected plan does not belong to this shipment."
            )

        # 3. Check plan feasibility and risk.
        cursor.execute(
            """
            SELECT FEASIBLE, RISK_LEVEL
            FROM FORESIGHTX_RECOVERY_PLANS
            WHERE PLAN_ID = ? AND SHIPMENT_ID = ?
            """,
            (selected_plan_id, shipment_id),
        )

        plan_record = cursor.fetchone()

        if plan_record is None:
            raise ValueError(
                "Selected plan could not be verified."
            )

        feasible, risk_level = plan_record

        if action == "approve" and feasible not in (True, 1):
            raise ValueError(
                "A plan that is not confirmed feasible "
                "cannot be approved."
            )

        if (
            action == "approve"
            and risk_level == "unknown"
            and not uncertainty_acknowledged
        ):
            raise ValueError(
                "Unknown risk must be explicitly acknowledged "
                "before approval."
            )

        # 4. Save the human review.
        cursor.execute(
            """
            INSERT INTO FORESIGHTX_HUMAN_REVIEWS (
                REVIEW_ID,
                DECISION_ID,
                SHIPMENT_ID,
                SELECTED_PLAN_ID,
                ACTION,
                REVIEWER_ROLE,
                COMMENTS,
                UNCERTAINTY_ACKNOWLEDGED
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                decision_id,
                shipment_id,
                selected_plan_id,
                action,
                reviewer_role,
                comments,
                uncertainty_acknowledged,
            ),
        )

        # 5. Append the human action to the audit trail.
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
                selected_plan_id,
                "human_reviewer",
                "human_decision",
                action,
                json.dumps(
                    {
                        "review_id": review_id,
                        "decision_id": decision_id,
                        "selected_plan_id": selected_plan_id,
                        "reviewer_role": reviewer_role,
                        "comments": comments,
                        "uncertainty_acknowledged": (
                            uncertainty_acknowledged
                        ),
                    },
                    default=str,
                ),
                "human_input",
            ),
        )

        connection.commit()

        return {
            "saved": True,
            "review_id": review_id,
            "decision_id": decision_id,
            "shipment_id": shipment_id,
            "selected_plan_id": selected_plan_id,
            "action": action,
            "uncertainty_acknowledged": uncertainty_acknowledged,
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
