from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey
)

from app.models.base import Base


class UserRole(Base):

    __tablename__ = "user_roles"
    __table_args__ = {"schema": "fui"}

    user_id = Column(
        BigInteger,
        ForeignKey("fui.users.id"),
        primary_key=True
    )

    role_id = Column(
        BigInteger,
        ForeignKey("fui.roles.id"),
        primary_key=True
    )
