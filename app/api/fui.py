from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.audit import write_audit_log
from app.models.fui_header import FuiHeader
from app.schemas.fui import (
    FuiCreate,
    FuiUpdate,
    FuiResponse
)
from app.services.fui_number import generate_fui_number
from app.services.workflow import (
    can_transition,
    apply_status_timestamp
)
from app.core.dependencies import (
    get_current_user,
    require_roles
)

router = APIRouter()

# =====================================================
# Helper
# =====================================================

def get_fui_or_404(db: Session, fui_id: int):
    obj = (
        db.query(FuiHeader)
        .filter(FuiHeader.id == fui_id)
        .first()
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    return obj


def change_status(
    *,
    db: Session,
    fui: FuiHeader,
    new_status: str,
    action: str,
    user_id: int
):
    old_status = fui.status

    if not can_transition(old_status, new_status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from {old_status} to {new_status}"
        )

    fui.status = new_status

    apply_status_timestamp(fui, new_status)

    db.commit()
    db.refresh(fui)

    write_audit_log(
        db=db,
        table_name="fui_header",
        record_id=fui.id,
        action=action,
        user_id=user_id,
        old_value={"status": old_status},
        new_value={"status": new_status}
    )

    return fui


# =====================================================
# CREATE
# =====================================================

@router.post(
    "",
    response_model=FuiResponse
)
def create_fui(
    payload: FuiCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "ADMIN_TE",
            "TECHNICAL_EXPERT"
        )
    )
):
    obj = FuiHeader(
        fui_number=generate_fui_number(),
        unit_number=payload.unit_number,
        priority_level=payload.priority_level,
        status="DRAFT",
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    write_audit_log(
        db=db,
        table_name="fui_header",
        record_id=obj.id,
        action="CREATE_FUI",
        user_id=current_user.id,
        old_value=None,
        new_value={
            "fui_number": obj.fui_number,
            "status": obj.status
        }
    )

    return obj


# =====================================================
# LIST
# =====================================================

@router.get("")
def list_fui(
    status: str | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(FuiHeader)

    if status:
        query = query.filter(FuiHeader.status == status)

    total = query.count()

    rows = (
        query
        .order_by(FuiHeader.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": rows
    }


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/{id}",
    response_model=FuiResponse
)
def get_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_fui_or_404(db, id)


# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{id}",
    response_model=FuiResponse
)
def update_fui(
    id: int,
    payload: FuiUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "ADMIN_TE",
            "TECHNICAL_EXPERT"
        )
    )
):
    obj = get_fui_or_404(db, id)

    if obj.status != "DRAFT":
        raise HTTPException(
            status_code=400,
            detail="Only DRAFT can be edited"
        )

    old_value = {
        "unit_number": obj.unit_number,
        "priority_level": obj.priority_level
    }

    obj.unit_number = payload.unit_number
    obj.priority_level = payload.priority_level

    db.commit()
    db.refresh(obj)

    write_audit_log(
        db=db,
        table_name="fui_header",
        record_id=obj.id,
        action="UPDATE_FUI",
        user_id=current_user.id,
        old_value=old_value,
        new_value={
            "unit_number": obj.unit_number,
            "priority_level": obj.priority_level
        }
    )

    return obj


# =====================================================
# SUBMIT
# =====================================================

@router.post("/{id}/submit")
def submit_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "ADMIN_TE",
            "TECHNICAL_EXPERT"
        )
    )
):
    obj = get_fui_or_404(db, id)

    change_status(
        db=db,
        fui=obj,
        new_status="SUBMITTED",
        action="SUBMIT_FUI",
        user_id=current_user.id
    )

    return {"message": "FUI submitted successfully"}


# =====================================================
# REVIEW
# =====================================================

@router.post("/{id}/review")
def review_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN_TE"))
):
    obj = get_fui_or_404(db, id)

    change_status(
        db=db,
        fui=obj,
        new_status="REVIEWED",
        action="REVIEW_FUI",
        user_id=current_user.id
    )

    return {"message": "FUI reviewed successfully"}


# =====================================================
# APPROVE
# =====================================================

@router.post("/{id}/approve")
def approve_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN_TE"))
):
    obj = get_fui_or_404(db, id)

    change_status(
        db=db,
        fui=obj,
        new_status="APPROVED",
        action="APPROVE_FUI",
        user_id=current_user.id
    )

    return {"message": "FUI approved successfully"}


# =====================================================
# EXECUTE
# =====================================================

@router.post("/{id}/execute")
def execute_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("EXECUTOR"))
):
    obj = get_fui_or_404(db, id)

    change_status(
        db=db,
        fui=obj,
        new_status="EXECUTED",
        action="EXECUTE_FUI",
        user_id=current_user.id
    )

    return {"message": "FUI executed successfully"}


# =====================================================
# CLOSE
# =====================================================

@router.post("/{id}/close")
def close_fui(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN_TE"))
):
    obj = get_fui_or_404(db, id)

    change_status(
        db=db,
        fui=obj,
        new_status="CLOSED",
        action="CLOSE_FUI",
        user_id=current_user.id
    )

    return {"message": "FUI closed successfully"}


# =====================================================
# HISTORY
# =====================================================

@router.get("/{id}/history")
def get_history(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    get_fui_or_404(db, id)

    rows = db.execute(
        text(
            """
            SELECT *
            FROM fui.audit_logs
            WHERE table_name='fui_header'
              AND record_id=:id
            ORDER BY created_at
            """
        ),
        {"id": id}
    )

    return [
        dict(row._mapping)
        for row in rows
    ]

