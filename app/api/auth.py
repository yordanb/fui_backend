from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, MeResponse
from app.core.security import verify_password
from app.core.dependencies import get_db, get_current_user
from app.models.user_role import UserRole
from app.models.role import Role
from app.core.jwt import create_access_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post(
    "/login",
    response_model=TokenResponse
)

def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Cek status user
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    token = create_access_token(
        {
            "sub": user.username
        }
    )

    return TokenResponse(
        access_token=token
    )
    # NOTE: Jangan lupa tambahkan logic return token di akhir fungsi login jika diperlukan, misalnya:
    # token = create_access_token(data={"sub": user.username})
    # return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=MeResponse
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    return {
        "id": current_user.id,
        "username": current_user.username,
        "fullname": current_user.fullname,
        "email": current_user.email,
        "roles": [r.role_name for r in roles]
    }
