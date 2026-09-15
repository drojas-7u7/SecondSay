from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class InputType(StrEnum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"


class CaseCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    content: str = Field(min_length=1)
    input_type: InputType = InputType.TEXT
    domain_profile: str = Field(default="insurance", min_length=1)
    external_id: str | None = None
