from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.schemas.user import UserResponse, UserResponseWithRoles, UserCreate
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import hash_password
from datetime import datetime
from app.schemas.user import UserStatusUpdate
from app.schemas.user import UserUpdate
from app.core.audit import write_audit_log
from app.schemas.user import UserPasswordReset

router = APIRouter(prefix="/api/users", tags=["Users"])


# READ: all roles
@router.get("/", response_model=list[UserResponseWithRoles])
def get_users(db: Session = Depends(get_db), current_user=Depends(require_roles("TE", "ADMIN_TE", "EXECUTOR"))):
    users = db.query(User).order_by(User.username).all()
    result = []
    for u in users:
        roles = db.query(Role.role_name).join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == u.id).all()
        result.append({"id": u.id, "username": u.username, "fullname": u.fullname, "email": u.email, "is_active": u.is_active, "created_at": u.created_at, "updated_at": u.updated_at, "roles": [r.role_name for r in roles]})
    return result


@router.get("/{user_id}", response_model=UserResponseWithRoles)
def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles("TE", "ADMIN_TE", "EXECUTOR"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = db.query(Role.role_name).join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == user.id).all()
    return {"id": user.id, "username": user.username, "fullname": user.fullname, "email": user.email, "is_active": user.is_active, "created_at": user.created_at, "updated_at": user.updated_at, "roles": [r.role_name for r in roles]}


# WRITE: TE only
@router.post("/", response_model=UserResponse)
def create_user(request: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    roles = db.query(Role).filter(Role.id.in_(request.role_ids)).all()
    if len(roles) != len(request.role_ids):
        raise HTTPException(status_code=400, detail="One or more role IDs are invalid")
    user = User(username=request.username, fullname=request.fullname, email=request.email, password_hash=hash_password(request.password), is_active=request.is_active, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(user)
    db.flush()
    for role_id in request.role_ids:
        db.add(UserRole(user_id=user.id, role_id=role_id))
    write_audit_log(db=db, table_name="users", record_id=user.id, action="CREATE", user_id=current_user.id, old_value=None, new_value={"username": user.username, "fullname": user.fullname, "email": user.email, "is_active": user.is_active})
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: int, request: UserStatusUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old = {"is_active": user.is_active}
    user.is_active = request.is_active
    user.updated_at = datetime.utcnow()
    write_audit_log(db=db, table_name="users", record_id=user.id, action="ACTIVATE" if request.is_active else "DEACTIVATE", user_id=current_user.id, old_value=old, new_value={"is_active": request.is_active})
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(User).filter(User.email == request.email, User.id != user_id).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    roles_db = db.query(Role).filter(Role.id.in_(request.role_ids)).all()
    if len(roles_db) != len(request.role_ids):
        raise HTTPException(status_code=400, detail="One or more role IDs are invalid")
    old = {"fullname": user.fullname, "email": user.email, "is_active": user.is_active}
    user.fullname = request.fullname
    user.email = request.email
    user.is_active = request.is_active
    user.updated_at = datetime.utcnow()
    db.query(UserRole).filter(UserRole.user_id == user.id).delete()
    for rid in request.role_ids:
        db.add(UserRole(user_id=user.id, role_id=rid))
    write_audit_log(db=db, table_name="users", record_id=user.id, action="UPDATE", user_id=current_user.id, old_value=old, new_value={"fullname": user.fullname, "email": user.email, "is_active": user.is_active, "role_ids": request.role_ids})
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("TE")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.query(UserRole).filter(UserRole.user_id == user.id).delete()
    db.delete(user)
    write_audit_log(db=db, table_name="users", record_id=user.id, action="DELETE", user_id=current_user.id, old_value={"username": user.username}, new_value=None)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/password")
def reset_user_password(user_id: int, request: UserPasswordReset, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(request.password)
    user.updated_at = datetime.utcnow()
    write_audit_log(db=db, table_name="users", record_id=user.id, action="RESET_PASSWORD", user_id=current_user.id, old_value=None, new_value=None)
    db.commit()
    return {"message": "Password reset successfully"}

from app.models.user_permission import UserPermission
from pydantic import BaseModel

class PermissionUpdate(BaseModel):
    feature_key: str
    is_enabled: bool

@router.get("/{user_id}/permissions")
def get_user_permissions(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    perms = db.query(UserPermission).filter(UserPermission.user_id == user_id).all()
    return {p.feature_key: p.is_enabled for p in perms}

@router.put("/{user_id}/permissions")
def update_user_permissions(user_id: int, request: PermissionUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("TE"))):
    perm = db.query(UserPermission).filter(UserPermission.user_id == user_id, UserPermission.feature_key == request.feature_key).first()
    if not perm:
        perm = UserPermission(user_id=user_id, feature_key=request.feature_key, is_enabled=request.is_enabled)
        db.add(perm)
    else:
        perm.is_enabled = request.is_enabled
    db.commit()
    return {"message": "updated"}
