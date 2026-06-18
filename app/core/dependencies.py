from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.jwt import decode_access_token
from app.models.user import User

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials
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

    # Sprint 1 Active User Validation
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive"
        )

    return user


# =====================================================
# ROLE CHECKER
# =====================================================

def require_roles(*allowed_roles):

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
            row.role_name
            for row in roles
        ]

        has_access = any(
            role in user_roles
            for role in allowed_roles
        )

        if not has_access:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_checker
