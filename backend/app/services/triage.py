from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision
from app.services.prompt_builder import PromptBuilder


class TriageService:
    def __init__(
        self,
        provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder

    def triage(self, case: CaseCreate) -> TriageDecision:
        prompt = self.prompt_builder.build(case)
        return self.provider.generate(prompt)
