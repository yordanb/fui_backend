from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey
)

from app.models.base import Base


class FuiHeader(Base):
    __tablename__ = "fui_header"
    __table_args__ = {"schema": "fui"}

    id = Column(BigInteger, primary_key=True, index=True)

    fui_number = Column(String(50), nullable=False, unique=True)
    unit_number = Column(String(50), nullable=False)

    priority_level = Column(String(20))
    status = Column(String(20), nullable=False)

    created_by = Column(
        BigInteger,
        ForeignKey("fui.users.id"),
        nullable=False
    )

    created_at = Column(DateTime)
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    closed_at = Column(DateTime)

    analyses = relationship(
        "FuiAnalysis",
        back_populates="fui",
        cascade="all, delete-orphan"
    )

    recommendations = relationship(
        "FuiRecommendation",
        back_populates="fui",
        cascade="all, delete-orphan"
    )
