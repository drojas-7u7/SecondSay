from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.audit import ChangedField, DiscrepancyImpact
from app.schemas.llm import LLMResult
from app.schemas.triage import Urgency


class InputType(StrEnum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1)
    input_type: InputType = InputType.TEXT
    domain_profile: str = Field(default="insurance", min_length=1)
    external_id: str | None = None


class CaseTriageResponse(LLMResult):
    case_id: UUID
    ai_decision_id: UUID


class CaseHistoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    ai_decision_id: UUID
    created_at: datetime
    external_id: str | None
    category: str
    urgency: Urgency
    department: str
    provider: str
    model: str
    latency_ms: float
    estimated_cost: float
    has_discrepancy: bool | None = None
    discrepancy_impact: DiscrepancyImpact | None = None
    changed_fields: list[ChangedField] = Field(default_factory=list)
    audited_at: datetime | None = None

