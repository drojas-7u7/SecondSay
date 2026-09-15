import pytest
from pydantic import ValidationError

from app.schemas.triage import TriageDecision, Urgency


def test_valid_triage_decision() -> None:
    decision = TriageDecision(
        category="Daños por agua",
        urgency=Urgency.HIGH,
        summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
        department="Siniestros",
        justification=(
            "La decisión se basa únicamente en la información disponible del caso."
        ),
    )

    assert decision.category == "Daños por agua"
    assert decision.urgency == Urgency.HIGH
    assert decision.department == "Siniestros"


def test_summary_requires_exactly_ten_words() -> None:
    with pytest.raises(ValidationError):
        TriageDecision(
            category="Daños por agua",
            urgency=Urgency.MEDIUM,
            summary="La fuga requiere revisión urgente",
            department="Siniestros",
            justification=(
                "La decisión se basa únicamente en la información disponible del caso."
            ),
        )


def test_urgency_rejects_invalid_value() -> None:
    with pytest.raises(ValidationError):
        TriageDecision(
            category="Daños por agua",
            urgency="MUY_ALTA",
            summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
            department="Siniestros",
            justification=(
                "La decisión se basa únicamente en la información disponible del caso."
            ),
        )


def test_triage_decision_rejects_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        TriageDecision(
            category="Daños por agua",
            urgency=Urgency.HIGH,
            summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
            department="Siniestros",
            justification=(
                "La decisión se basa únicamente en la información disponible del caso."
            ),
            unexpected_field="No permitido",
        )
