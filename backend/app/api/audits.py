from fastapi import APIRouter

from app.domain.audit import AuditEngine
from app.schemas.audit import AuditRequest, AuditResult

router = APIRouter(prefix="/api/v1/audits", tags=["Auditorías"])

audit_engine = AuditEngine()


@router.post("/review", response_model=AuditResult)
def review_ai_decision(request: AuditRequest) -> AuditResult:
    return audit_engine.audit(
        ai_decision=request.ai_decision,
        human_review=request.human_review,
    )
