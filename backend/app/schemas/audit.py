from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.triage import TriageDecision, Urgency


class DiscrepancyImpact(StrEnum):
    LOW = "BAJO"
    MEDIUM = "MEDIO"
    HIGH = "ALTO"
    CRITICAL = "CRÍTICO"


class ChangedField(StrEnum):
    CATEGORY = "categoría"
    URGENCY = "urgencia"
    DEPARTMENT = "departamento"


class HumanReview(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    final_category: str = Field(min_length=1)
    final_urgency: Urgency
    final_department: str = Field(min_length=1)
    review_note: str | None = Field(default=None, min_length=1)
    discrepancy_impact: DiscrepancyImpact | None = None


class AuditResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_discrepancy: bool
    changed_fields: list[ChangedField]
    ai_decision: TriageDecision
    human_review: HumanReview



class AuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ai_decision_id: UUID
    human_review: HumanReview
