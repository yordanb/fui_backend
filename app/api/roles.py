from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.role import Role

router = APIRouter(
    prefix="/api/roles",
    tags=["Roles"]
)


@router.get("/")
def get_roles(
    db: Session = Depends(get_db)
):

    roles = (
        db.query(Role)
        .order_by(Role.role_name)
        .all()
    )

    return roles
