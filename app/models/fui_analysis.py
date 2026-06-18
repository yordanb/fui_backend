from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class FuiAnalysis(Base):
    __tablename__ = "fui_analysis"
    __table_args__ = {"schema": "fui"}

    id = Column(BigInteger, primary_key=True, index=True)

    fui_id = Column(
        BigInteger,
        ForeignKey("fui.fui_header.id"),
        nullable=False
    )

    analysis_type = Column(Text)
    problem_description = Column(Text, nullable=False)
    root_cause = Column(Text)
    impact_analysis = Column(Text)
    corrective_action = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    fui = relationship(
        "FuiHeader",
        back_populates="analyses"
    )
