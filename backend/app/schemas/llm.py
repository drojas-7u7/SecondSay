from pydantic import BaseModel, ConfigDict, Field

from app.schemas.triage import TriageDecision


class LLMExecutionMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    latency_ms: float = Field(ge=0)
    estimated_cost: float = Field(ge=0)


class LLMResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: TriageDecision
    metrics: LLMExecutionMetrics
