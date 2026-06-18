from datetime import datetime

ALLOWED_TRANSITIONS = {
    "DRAFT": ["SUBMITTED"],
    "SUBMITTED": ["REVIEWED"],
    "REVIEWED": ["APPROVED"],
    "APPROVED": ["EXECUTED"],
    "EXECUTED": ["CLOSED"],
    "CLOSED": []
}


def can_transition(
    current_status: str,
    new_status: str
) -> bool:

    return (
        new_status
        in ALLOWED_TRANSITIONS.get(
            current_status,
            []
        )
    )


def apply_status_timestamp(
    fui,
    new_status: str
):

    now = datetime.utcnow()

    if new_status == "SUBMITTED":
        fui.submitted_at = now

    elif new_status == "APPROVED":
        fui.approved_at = now

    elif new_status == "CLOSED":
        fui.closed_at = now
