from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint
from app.models.base import Base

class UserPermission(Base):
    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "feature_key", name="uq_user_feature"),
        {"schema": "fui"},
    )
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("fui.users.id", ondelete="CASCADE"), nullable=False)
    feature_key = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
