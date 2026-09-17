from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CaseRecord(Base):
    __tablename__ = "cases"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    input_type: Mapped[str] = mapped_column(String(20))
    domain_profile: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class AIDecisionRecord(Base):
    __tablename__ = "ai_decisions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
    )
    category: Mapped[str] = mapped_column(String(255))
    urgency: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    department: Mapped[str] = mapped_column(String(255))
    justification: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(255))
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    latency_ms: Mapped[float] = mapped_column(Float)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(14, 10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class AuditRecord(Base):
    __tablename__ = "audits"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    ai_decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("ai_decisions.id", ondelete="CASCADE"),
        index=True,
    )
    final_category: Mapped[str] = mapped_column(String(255))
    final_urgency: Mapped[str] = mapped_column(String(20))
    final_department: Mapped[str] = mapped_column(String(255))
    review_note: Mapped[str | None] = mapped_column(Text)
    discrepancy_impact: Mapped[str | None] = mapped_column(String(20))
    has_discrepancy: Mapped[bool] = mapped_column(Boolean)
    changed_fields: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
