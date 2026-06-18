from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.audit import write_audit_log
from app.models.fui_header import FuiHeader
from app.models.fui_analysis import FuiAnalysis
from app.schemas.fui_analysis import (
    FuiAnalysisCreate,
    FuiAnalysisUpdate,
    FuiAnalysisResponse
)
from datetime import datetime
from app.utils.workflow import validate_analysis_editable

router = APIRouter(
    prefix="/api",
    tags=["FUI Analysis"]
)

# =====================================================
# WORKFLOW VALIDATION
# =====================================================





# =====================================================
# CREATE ANALYSIS
# =====================================================

@router.post(
    "/fui/{fui_id}/analysis",
    response_model=FuiAnalysisResponse
)
def create_analysis(
    fui_id: int,
    payload: FuiAnalysisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    fui = (
        db.query(FuiHeader)
        .filter(FuiHeader.id == fui_id)
        .first()
    )
    
    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    validate_analysis_editable(fui)

    analysis = FuiAnalysis(
        fui_id=fui_id,
        analysis_type=payload.analysis_type,
        problem_description=payload.problem_description,
        root_cause=payload.root_cause,
        impact_analysis=payload.impact_analysis,
        corrective_action=payload.corrective_action,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    write_audit_log(
        db=db,
        table_name="fui_analysis",
        record_id=analysis.id,
        action="CREATE_ANALYSIS",
        user_id=current_user.id,
        old_value=None,
        new_value={
            "fui_id": analysis.fui_id,
            "analysis_type": analysis.analysis_type,
            "problem_description": analysis.problem_description
        }
    )

    return analysis


# =====================================================
# GET ALL ANALYSIS BY FUI
# =====================================================

@router.get(
    "/fui/{fui_id}/analysis",
    response_model=list[FuiAnalysisResponse]
)
def get_analysis_by_fui(
    fui_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    fui = (
        db.query(FuiHeader)
        .filter(FuiHeader.id == fui_id)
        .first()
    )
    
    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    analyses = (
        db.query(FuiAnalysis)
        .filter(FuiAnalysis.fui_id == fui_id)
        .order_by(FuiAnalysis.id.desc())
        .all()
    )

    return analyses


# =====================================================
# GET ANALYSIS DETAIL
# =====================================================

@router.get(
    "/analysis/{analysis_id}",
    response_model=FuiAnalysisResponse
)
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analysis = (
        db.query(FuiAnalysis)
        .filter(FuiAnalysis.id == analysis_id)
        .first()
    )
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return analysis


# =====================================================
# UPDATE ANALYSIS
# =====================================================

@router.put(
    "/analysis/{analysis_id}",
    response_model=FuiAnalysisResponse
)
def update_analysis(
    analysis_id: int,
    payload: FuiAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analysis = (
        db.query(FuiAnalysis)
        .filter(FuiAnalysis.id == analysis_id)
        .first()
    )
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    fui = (
        db.query(FuiHeader)
        .filter(FuiHeader.id == analysis.fui_id)
        .first()
    )

    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    validate_analysis_editable(fui)

    old_value = {
        "analysis_type": analysis.analysis_type,
        "problem_description": analysis.problem_description,
        "root_cause": analysis.root_cause,
        "impact_analysis": analysis.impact_analysis,
        "corrective_action": analysis.corrective_action
    }

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(analysis, field, value)

    analysis.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(analysis)

    write_audit_log(
        db=db,
        table_name="fui_analysis",
        record_id=analysis.id,
        action="UPDATE_ANALYSIS",
        user_id=current_user.id,
        old_value=old_value,
        new_value={
            "analysis_type": analysis.analysis_type,
            "problem_description": analysis.problem_description,
            "root_cause": analysis.root_cause,
            "impact_analysis": analysis.impact_analysis,
            "corrective_action": analysis.corrective_action
        }
    )

    return analysis
