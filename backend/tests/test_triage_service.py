from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision, Urgency
from app.services.prompt_builder import PromptBuilder
from app.services.triage import TriageService


class StubLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self.received_prompt: str | None = None

    def generate(self, prompt: str) -> LLMResult:
        self.received_prompt = prompt

        decision = TriageDecision(
            category="Water damage",
            urgency=Urgency.HIGH,
            summary=(
                "Water damage affects neighboring property requiring immediate specialist review today"
            ),
            department="Claims",
            justification=(
                "Neighboring property damage increases the need for specialist review."
            ),
        )

        metrics = LLMExecutionMetrics(
            provider="stub",
            model="stub-model",
            input_tokens=100,
            output_tokens=40,
            latency_ms=125.5,
            estimated_cost=0.0,
        )

        return LLMResult(
            decision=decision,
            metrics=metrics,
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

    result = service.triage(case)

    assert provider.received_prompt is not None
    assert case.content in provider.received_prompt
    assert result.decision.category == "Water damage"
    assert result.decision.urgency == Urgency.HIGH
    assert result.decision.department == "Claims"
    assert result.metrics.provider == "stub"
    assert result.metrics.input_tokens == 100
