from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision, Urgency
from app.services.prompt_builder import PromptBuilder
from app.services.triage import TriageService


class StubLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self.received_prompt: str | None = None

    def generate(self, prompt: str) -> TriageDecision:
        self.received_prompt = prompt

        return TriageDecision(
            category="Water damage",
            urgency=Urgency.HIGH,
            summary="Water damage affects neighboring property requiring immediate specialist review today",
            department="Claims",
            justification=(
                "Neighboring property damage increases the need for specialist review."
            ),
        )


def test_triage_service_builds_prompt_and_delegates_to_provider() -> None:
    provider = StubLLMProvider()
    service = TriageService(
        provider=provider,
        prompt_builder=PromptBuilder(),
    )

    case = CaseCreate(
        content="Water leak has affected the neighboring property."
    )

    decision = service.triage(case)

    assert provider.received_prompt is not None
    assert case.content in provider.received_prompt
    assert decision.category == "Water damage"
    assert decision.urgency == Urgency.HIGH
    assert decision.department == "Claims"
