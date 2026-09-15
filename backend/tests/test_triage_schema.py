import pytest
from pydantic import ValidationError

from app.schemas.triage import TriageDecision, Urgency


def test_valid_triage_decision() -> None:
    decision = TriageDecision(
        category="Water damage",
        urgency=Urgency.HIGH,
        summary="Water leak affects neighbor property and requires urgent inspection today",
        department="Claims",
    )

    assert decision.category == "Water damage"
    assert decision.urgency == Urgency.HIGH


def test_summary_requires_exactly_ten_words() -> None:
    with pytest.raises(ValidationError):
        TriageDecision(
            category="Water damage",
            urgency=Urgency.MEDIUM,
            summary="This summary has fewer than exactly ten required words",
            department="Claims",
        )


def test_urgency_rejects_invalid_value() -> None:
    with pytest.raises(ValidationError):
        TriageDecision(
            category="Water damage",
            urgency="VERY_HIGH",
            summary="Water leak affects neighbor property and requires urgent inspection today",
            department="Claims",
        )
