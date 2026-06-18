from sqlalchemy import (
    Column,
    BigInteger,
    String
)

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "fui"}

    id = Column(BigInteger, primary_key=True)

    role_name = Column(String)

    description = Column(String)
