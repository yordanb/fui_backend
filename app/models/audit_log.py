from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP
)

from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "fui"}

    id = Column(
        BigInteger,
        primary_key=True
    )
    table_name = Column(String)
    record_id = Column(BigInteger)
    action = Column(String)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    user_id = Column(BigInteger)
    created_at = Column(TIMESTAMP)
