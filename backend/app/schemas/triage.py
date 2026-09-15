from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Urgency(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TriageDecision(BaseModel):
    model_config = ConfigDict(strict=True)

    category: str = Field(min_length=1)
    urgency: Urgency
    summary: str
    department: str = Field(min_length=1)

    @field_validator("summary")
    @classmethod
    def summary_must_have_exactly_ten_words(cls, value: str) -> str:
        word_count = len(value.split())

        if word_count != 10:
            raise ValueError(
                f"summary must contain exactly 10 words; received {word_count}"
            )

        return value
