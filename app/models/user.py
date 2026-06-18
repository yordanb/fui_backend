from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    TIMESTAMP
)

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "fui"}

    id = Column(BigInteger, primary_key=True)

    username = Column(String)
    fullname = Column(String)
    email = Column(String)

    password_hash = Column(String)

    is_active = Column(Boolean)

    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
