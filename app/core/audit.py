from datetime import datetime

from app.models.audit_log import AuditLog


def write_audit_log(
    db,
    table_name: str,
    record_id: int,
    action: str,
    user_id: int,
    old_value=None,
    new_value=None
):

    audit = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        user_id=user_id,
        created_at=datetime.utcnow()
    )

    db.add(audit)
    db.commit()

    return audit
