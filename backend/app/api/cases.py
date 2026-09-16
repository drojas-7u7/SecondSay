from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db_session
from app.providers.base import LLMProvider
from app.providers.factory import build_llm_provider
from app.repositories import CaseRepository
from app.schemas.case import CaseCreate, CaseTriageResponse
from app.services.prompt_builder import PromptBuilder
from app.services.triage import TriageService

router = APIRouter(prefix="/api/v1/cases", tags=["Casos"])


def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())


def get_triage_service(
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> TriageService:
    return TriageService(
        provider=provider,
        prompt_builder=PromptBuilder(),
    )


@router.post("/triage", response_model=CaseTriageResponse)
def triage_case(
    case: CaseCreate,
    triage_service: Annotated[
        TriageService,
        Depends(get_triage_service),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> CaseTriageResponse:
    result = triage_service.triage(case)

    case_record, decision_record = CaseRepository().create_with_decision(
        session=session,
        case=case,
        result=result,
    )
    session.commit()

    return CaseTriageResponse(
        case_id=case_record.id,
        ai_decision_id=decision_record.id,
        decision=result.decision,
        metrics=result.metrics,
    )
