from fastapi import APIRouter

from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision, Urgency

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])


@router.post("/triage", response_model=TriageDecision)
def triage_case(case: CaseCreate) -> TriageDecision:
    return TriageDecision(
        category="General incident",
        urgency=Urgency.MEDIUM,
        summary="Incoming case requires structured review before final human validation today",
        department="Claims",
    )
