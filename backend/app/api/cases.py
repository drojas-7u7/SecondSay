from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.providers.base import LLMProvider
from app.providers.factory import build_llm_provider
from app.schemas.case import CaseCreate
from app.schemas.llm import LLMResult
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


@router.post("/triage", response_model=LLMResult)
def triage_case(
    case: CaseCreate,
    triage_service: Annotated[
        TriageService,
        Depends(get_triage_service),
    ],
) -> LLMResult:
    return triage_service.triage(case)
