from fastapi import HTTPException


ANALYSIS_EDITABLE_STATUS = [
    "DRAFT",
    "SUBMITTED",
    "REVIEWED"
]


def validate_analysis_editable(fui):
    if fui.status not in ANALYSIS_EDITABLE_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis locked because FUI status is {fui.status}"
        )
