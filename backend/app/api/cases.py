from fastapi import APIRouter

from app.providers.fake import FakeLLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision
from app.services.triage import TriageService

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])

provider = FakeLLMProvider()
triage_service = TriageService(provider=provider)


@router.post("/triage", response_model=TriageDecision)
def triage_case(case: CaseCreate) -> TriageDecision:
    return triage_service.triage(case)
