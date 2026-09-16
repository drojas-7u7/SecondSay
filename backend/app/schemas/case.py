from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.llm import LLMResult


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

