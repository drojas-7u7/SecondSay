import pytest

from app.domain.audit import AuditEngine, AuditEngineError
from app.schemas.audit import ChangedField, DiscrepancyImpact, HumanReview
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


def test_audit_engine_detects_agreement() -> None:
    ai_decision = build_ai_decision()

    human_review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.MEDIUM,
        final_department="Siniestros",
        review_note="La decisión inicial se mantiene.",
    )

    result = AuditEngine().audit(
        ai_decision=ai_decision,
        human_review=human_review,
    )

    assert result.has_discrepancy is False
    assert result.changed_fields == []
    assert result.human_review.discrepancy_impact is None


def test_audit_engine_detects_changed_fields() -> None:
    ai_decision = build_ai_decision()

    human_review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.HIGH,
        final_department="Responsabilidad Civil",
        review_note="Existe afectación a terceros.",
        discrepancy_impact=DiscrepancyImpact.HIGH,
    )

    result = AuditEngine().audit(
        ai_decision=ai_decision,
        human_review=human_review,
    )

    assert result.has_discrepancy is True
    assert result.changed_fields == [
        ChangedField.URGENCY,
        ChangedField.DEPARTMENT,
    ]
    assert result.human_review.discrepancy_impact == DiscrepancyImpact.HIGH


def test_audit_engine_requires_impact_for_discrepancy() -> None:
    ai_decision = build_ai_decision()

    human_review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.HIGH,
        final_department="Siniestros",
    )

    with pytest.raises(AuditEngineError):
        AuditEngine().audit(
            ai_decision=ai_decision,
            human_review=human_review,
        )


def test_audit_engine_rejects_impact_without_discrepancy() -> None:
    ai_decision = build_ai_decision()

    human_review = HumanReview(
        final_category="Daños por agua",
        final_urgency=Urgency.MEDIUM,
        final_department="Siniestros",
        discrepancy_impact=DiscrepancyImpact.LOW,
    )

    with pytest.raises(AuditEngineError):
        AuditEngine().audit(
            ai_decision=ai_decision,
            human_review=human_review,
        )
