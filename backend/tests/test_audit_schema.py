from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.audit import (
    AuditRequest,
    AuditResult,
    ChangedField,
    DiscrepancyImpact,
    HumanReview,
)
from app.schemas.triage import TriageDecision, Urgency


def build_ai_decision() -> TriageDecision:
    return TriageDecision(
        category="Daños por agua",
        urgency=Urgency.MEDIUM,
        summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
        department="Siniestros",
        justification=(
            "La información disponible requiere revisión estructurada del siniestro."
        ),
    )


def test_human_review_accepts_valid_review() -> None:
    review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.HIGH,
        final_department="Responsabilidad Civil",
        review_note="Existe afectación a una vivienda de un tercero.",
        discrepancy_impact=DiscrepancyImpact.HIGH,
    )

    assert review.final_category == "Daños por agua"
    assert review.final_urgency == Urgency.HIGH
    assert review.final_department == "Responsabilidad Civil"
    assert review.discrepancy_impact == DiscrepancyImpact.HIGH


def test_human_review_strips_surrounding_whitespace() -> None:
    review = HumanReview(
        final_category="  Daños por agua  ",
        final_urgency=Urgency.HIGH,
        final_department="  Responsabilidad Civil  ",
        review_note="  Revisión necesaria por afectación a terceros.  ",
    )

    assert review.final_category == "Daños por agua"
    assert review.final_department == "Responsabilidad Civil"
    assert review.review_note == "Revisión necesaria por afectación a terceros."


def test_human_review_rejects_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        HumanReview(
            final_category="Daños por agua",
            final_urgency=Urgency.HIGH,
            final_department="Siniestros",
            unexpected_field="No permitido",
        )


def test_audit_result_accepts_discrepancy() -> None:
    decision = build_ai_decision()

    review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.HIGH,
        final_department="Responsabilidad Civil",
        discrepancy_impact=DiscrepancyImpact.HIGH,
    )

    result = AuditResult(
        has_discrepancy=True,
        changed_fields=[
            ChangedField.URGENCY,
            ChangedField.DEPARTMENT,
        ],
        ai_decision=decision,
        human_review=review,
    )

    assert result.has_discrepancy is True
    assert result.changed_fields == [
        ChangedField.URGENCY,
        ChangedField.DEPARTMENT,
    ]


def test_audit_request_groups_decision_id_and_human_review() -> None:
    ai_decision_id = uuid4()

    review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.HIGH,
        final_department="Responsabilidad Civil",
        review_note="Existe afectación a terceros.",
        discrepancy_impact=DiscrepancyImpact.HIGH,
    )

    request = AuditRequest(
        ai_decision_id=ai_decision_id,
        human_review=review,
    )

    assert request.ai_decision_id == ai_decision_id
    assert request.human_review == review
