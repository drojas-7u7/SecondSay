from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.domain.audit import AuditEngine, AuditEngineError
from app.repositories import AuditRepository, CaseRepository
from app.schemas.audit import AuditRequest, AuditResult
from app.schemas.triage import TriageDecision, Urgency

router = APIRouter(prefix="/api/v1/audits", tags=["Auditorías"])

audit_engine = AuditEngine()


@router.post("/review", response_model=AuditResult)
def review_ai_decision(
    request: AuditRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> AuditResult:
    decision_record = CaseRepository().get_decision(
        session=session,
        ai_decision_id=request.ai_decision_id,
    )

    if decision_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la decisión de IA indicada.",
        )

    ai_decision = TriageDecision(
        category=decision_record.category,
        urgency=Urgency(decision_record.urgency),
        summary=decision_record.summary,
        department=decision_record.department,
        justification=decision_record.justification,
    )

    try:
        result = audit_engine.audit(
            ai_decision=ai_decision,
            human_review=request.human_review,
        )
    except AuditEngineError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La revisión humana tiene un impacto de discrepancia incoherente.",
        ) from exc

    AuditRepository().create(
        session=session,
        ai_decision_id=request.ai_decision_id,
        result=result,
    )
    session.commit()

    return result
