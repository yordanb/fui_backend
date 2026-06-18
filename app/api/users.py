from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import hash_password
from datetime import datetime
from app.schemas.user import UserStatusUpdate
from app.schemas.user import UserUpdate
from app.core.audit import write_audit_log
from app.schemas.user import UserPasswordReset

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    return (
        db.query(User)
        .order_by(User.username)
        .all()
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.post(
    "/",
    response_model=UserResponse
)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    existing_user = (
        db.query(User)
        .filter(
            User.username == request.username
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    roles = (
    db.query(Role)
    .filter(
        Role.id.in_(request.role_ids)
    )
    .all()
    )

    if len(roles) != len(request.role_ids):
        raise HTTPException(
             status_code=400,
             detail="One or more role IDs are invalid"
        )

    user = User(
        username=request.username,
        fullname=request.fullname,
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
        is_active=request.is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(user)
    db.flush()

    for role_id in request.role_ids:

        db.add(
            UserRole(
                user_id=user.id,
                role_id=role_id
            )
        )

    write_audit_log(
    db=db,
    table_name="users",
    record_id=user.id,
    action="CREATE",
    user_id=current_user.id,
    old_value=None,
    new_value={
        "username": user.username,
        "fullname": user.fullname,
        "email": user.email,
        "is_active": user.is_active
        }
    )

    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_user_status(
    user_id: int,
    request: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_data = {"is_active": user.is_active}

    user.is_active = request.is_active
    user.updated_at = datetime.utcnow()

    new_data = {
    "is_active": request.is_active
    }

    action = (
        "ACTIVATE"
        if request.is_active
        else "DEACTIVATE"
    )

    write_audit_log(
        db=db,
        table_name="users",
        record_id=user.id,
        action=action,
        user_id=current_user.id,
        old_value=old_data,
        new_value=new_data
    )

    db.commit()
    db.refresh(user)

    return user

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_email = (
        db.query(User)
        .filter(
            User.email == request.email,
            User.id != user_id
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    roles = (
        db.query(Role)
        .filter(
            Role.id.in_(request.role_ids)
        )
        .all()
    )

    if len(roles) != len(request.role_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more role IDs are invalid"
        )

    old_data = {
    "fullname": user.fullname,
    "email": user.email,
    "is_active": user.is_active
    }

    user.fullname = request.fullname
    user.email = request.email
    user.is_active = request.is_active
    user.updated_at = datetime.utcnow()

    db.query(UserRole).filter(
        UserRole.user_id == user.id
    ).delete()

    for role_id in request.role_ids:

        db.add(
            UserRole(
                user_id=user.id,
                role_id=role_id
            )
        )

    new_data = {
        "fullname": user.fullname,
        "email": user.email,
        "is_active": user.is_active,
        "role_ids": request.role_ids
    }

    write_audit_log(
        db=db,
        table_name="users",
        record_id=user.id,
        action="UPDATE",
        user_id=current_user.id,
        old_value=old_data,
        new_value=new_data
    )

    db.commit()
    db.refresh(user)

    return user

@router.put(
    "/{user_id}/password"
)
def reset_user_password(
    user_id: int,
    request: UserPasswordReset,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["ADMIN_TE"])
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password_hash = hash_password(
        request.password
    )

    user.updated_at = datetime.utcnow()

    write_audit_log(
        db=db,
        table_name="users",
        record_id=user.id,
        action="RESET_PASSWORD",
        user_id=current_user.id,
        old_value=None,
        new_value=None
    )

    db.commit()

    return {
        "message": "Password reset successfully"
    }
