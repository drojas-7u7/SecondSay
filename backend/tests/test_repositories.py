from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import AIDecisionRecord, AuditRecord, Base, CaseRecord
from app.repositories import AuditRepository, CaseRepository
from app.schemas.audit import (
    AuditResult,
    ChangedField,
    DiscrepancyImpact,
    HumanReview,
)
from app.schemas.case import CaseCreate
from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision, Urgency


def build_llm_result() -> LLMResult:
    return LLMResult(
        decision=TriageDecision(
            category="Daños por agua",
            urgency=Urgency.MEDIUM,
            summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
            department="Siniestros",
            justification="La incidencia requiere una revisión técnica del daño comunicado.",
        ),
        metrics=LLMExecutionMetrics(
            provider="fake",
            model="deterministic-demo",
            input_tokens=10,
            output_tokens=20,
            latency_ms=15.5,
            estimated_cost=0.0001,
        ),
    )


def test_case_repository_persists_case_and_ai_decision() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        case_record, decision_record = CaseRepository().create_with_decision(
            session=session,
            case=CaseCreate(
                content="Hay una fuga de agua en la cocina.",
                external_id="CASE-001",
            ),
            result=build_llm_result(),
        )
        session.commit()

        stored_case = session.scalar(
            select(CaseRecord).where(CaseRecord.id == case_record.id)
        )
        stored_decision = session.scalar(
            select(AIDecisionRecord).where(
                AIDecisionRecord.id == decision_record.id
            )
        )

        assert stored_case is not None
        assert stored_case.external_id == "CASE-001"
        assert stored_decision is not None
        assert stored_decision.case_id == stored_case.id
        assert stored_decision.urgency == "MEDIA"
        assert stored_decision.provider == "fake"

    engine.dispose()


def test_audit_repository_persists_human_review() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        _, decision_record = CaseRepository().create_with_decision(
            session=session,
            case=CaseCreate(content="Hay una fuga de agua en la cocina."),
            result=build_llm_result(),
        )

        audit_result = AuditResult(
            has_discrepancy=True,
            changed_fields=[
                ChangedField.URGENCY,
                ChangedField.DEPARTMENT,
            ],
            ai_decision=build_llm_result().decision,
            human_review=HumanReview(
                final_category="Daños por agua",
                final_urgency=Urgency.HIGH,
                final_department="Responsabilidad Civil",
                review_note="Hay terceros afectados.",
                discrepancy_impact=DiscrepancyImpact.HIGH,
            ),
        )

        audit_record = AuditRepository().create(
            session=session,
            ai_decision_id=decision_record.id,
            result=audit_result,
        )
        session.commit()

        stored_audit = session.scalar(
            select(AuditRecord).where(AuditRecord.id == audit_record.id)
        )

        assert stored_audit is not None
        assert stored_audit.ai_decision_id == decision_record.id
        assert stored_audit.final_urgency == "ALTA"
        assert stored_audit.has_discrepancy is True
        assert stored_audit.changed_fields == ["urgencia", "departamento"]
        assert stored_audit.discrepancy_impact == "ALTO"

    engine.dispose()
