import pytest
from pydantic import ValidationError

from app.schemas.case import CaseCreate, InputType


def test_valid_text_case() -> None:
    case = CaseCreate(
        content="Water leak has damaged the kitchen and neighboring property.",
        input_type=InputType.TEXT,
        domain_profile="insurance",
        external_id="CLAIM-001",
    )

    assert case.content.startswith("Water leak")
    assert case.input_type == InputType.TEXT
    assert case.domain_profile == "insurance"
    assert case.external_id == "CLAIM-001"


def test_text_is_default_input_type() -> None:
    case = CaseCreate(
        content="Customer reports damage caused by a water leak."
    )

    assert case.input_type == InputType.TEXT


def test_empty_content_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CaseCreate(content="")


def test_unknown_input_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CaseCreate(
            content="Valid incident description.",
            input_type="AUDIO",
        )
