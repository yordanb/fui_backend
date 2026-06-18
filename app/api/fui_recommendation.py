from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.fui_header import FuiHeader
from app.models.fui_recommendation import FuiRecommendation

from app.schemas.fui_recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse
)

from app.core.dependencies import get_current_user
from app.core.audit import write_audit_log


router = APIRouter(
    prefix="/api",
    tags=["FUI Recommendation"]
)


EDITABLE_STATUSES = [
    "DRAFT",
    "SUBMITTED",
    "REVIEWED",
    "APPROVED"
]


def validate_recommendation_editable(fui: FuiHeader):
    """
    Recommendation can be edited only until APPROVED.
    Once EXECUTED or CLOSED, recommendation becomes locked.
    """

    if fui.status not in EDITABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Recommendation locked because FUI status is {fui.status}"
        )


@router.post(
    "/fui/{fui_id}/recommendation",
    response_model=RecommendationResponse
)
def create_recommendation(
    fui_id: int,
    payload: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Create recommendation for FUI
    """

    fui = db.query(FuiHeader).filter(
        FuiHeader.id == fui_id
    ).first()

    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    validate_recommendation_editable(fui)

    recommendation = FuiRecommendation(
        fui_id=fui_id,
        recommendation_type=payload.recommendation_type,
        instruction=payload.instruction,
        reason=payload.reason,
        source=payload.source
    )

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    write_audit_log(
        db=db,
        user_id=current_user.id,
        table_name="fui_recommendations",
        record_id=recommendation.id,
        action="CREATE_RECOMMENDATION",
        old_value=None,
        new_value={
            "fui_id": recommendation.fui_id,
            "recommendation_type": recommendation.recommendation_type,
            "instruction": recommendation.instruction
        }
    )

    return recommendation


@router.get(
    "/fui/{fui_id}/recommendation",
    response_model=list[RecommendationResponse]
)
def get_recommendations_by_fui(
    fui_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get all recommendations for a specific FUI
    """

    fui = db.query(FuiHeader).filter(
        FuiHeader.id == fui_id
    ).first()

    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    recommendations = db.query(
        FuiRecommendation
    ).filter(
        FuiRecommendation.fui_id == fui_id
    ).order_by(
        FuiRecommendation.id.asc()
    ).all()

    return recommendations


@router.get(
    "/recommendation/{recommendation_id}",
    response_model=RecommendationResponse
)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get recommendation by ID
    """

    recommendation = db.query(
        FuiRecommendation
    ).filter(
        FuiRecommendation.id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return recommendation


@router.put(
    "/recommendation/{recommendation_id}",
    response_model=RecommendationResponse
)
def update_recommendation(
    recommendation_id: int,
    payload: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update recommendation
    """

    recommendation = db.query(
        FuiRecommendation
    ).filter(
        FuiRecommendation.id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    fui = db.query(FuiHeader).filter(
        FuiHeader.id == recommendation.fui_id
    ).first()

    if not fui:
        raise HTTPException(
            status_code=404,
            detail="FUI not found"
        )

    validate_recommendation_editable(fui)

    old_values = {
        "recommendation_type": recommendation.recommendation_type,
        "instruction": recommendation.instruction,
        "reason": recommendation.reason,
        "source": recommendation.source
    }

    recommendation.recommendation_type = (
        payload.recommendation_type
    )

    recommendation.instruction = (
        payload.instruction
    )

    recommendation.reason = (
        payload.reason
    )

    recommendation.source = (
        payload.source
    )

    db.commit()
    db.refresh(recommendation)

    write_audit_log(
        db=db,
        user_id=current_user.id,
        table_name="fui_recommendations",
        record_id=recommendation.id,
        action="UPDATE_RECOMMENDATION",
        old_value=old_values,
        new_value={
            "recommendation_type": recommendation.recommendation_type,
            "instruction": recommendation.instruction,
            "reason": recommendation.reason,
            "source": recommendation.source
        }
    )

    return recommendation
