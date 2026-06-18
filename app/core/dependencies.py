from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.core.jwt import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user

def require_roles(allowed_roles: List[str]):

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

        from app.models.user_role import UserRole
        from app.models.role import Role

        roles = (
            db.query(Role.role_name)
            .join(
                UserRole,
                UserRole.role_id == Role.id
            )
            .filter(
                UserRole.user_id == current_user.id
            )
            .all()
        )

        user_roles = [
            r.role_name
            for r in roles
        ]

        if not any(
            role in user_roles
            for role in allowed_roles
        ):
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_checker
