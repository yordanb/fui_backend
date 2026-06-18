from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class FuiRecommendation(Base):
    __tablename__ = "fui_recommendation"
    __table_args__ = {"schema": "fui"}

    id = Column(BigInteger, primary_key=True, index=True)

    fui_id = Column(
        BigInteger,
        ForeignKey("fui.fui_header.id"),
        nullable=False
    )

    recommendation_no = Column(Integer)

    recommendation_type = Column(String(100))

    instruction = Column(Text)

    reason = Column(Text)

    source = Column(String(255))

    status = Column(String(50))

    created_at = Column(DateTime)

    fui = relationship(
        "FuiHeader",
        back_populates="recommendations"
    )
