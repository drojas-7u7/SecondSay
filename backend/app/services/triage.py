from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision


class TriageService:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def triage(self, case: CaseCreate) -> TriageDecision:
        return self.provider.triage(case)
