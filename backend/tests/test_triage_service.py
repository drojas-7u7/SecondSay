from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision, Urgency
from app.services.triage import TriageService


class StubLLMProvider(LLMProvider):
    def triage(self, case: CaseCreate) -> TriageDecision:
        return TriageDecision(
            category="Water damage",
            urgency=Urgency.HIGH,
            summary="Water damage affects neighboring property requiring immediate specialist review today",
            department="Claims",
        )


def test_triage_service_delegates_to_provider() -> None:
    service = TriageService(provider=StubLLMProvider())

    decision = service.triage(
        CaseCreate(
            content="Water leak has affected the neighboring property.",
        )
    )

    assert decision.category == "Water damage"
    assert decision.urgency == Urgency.HIGH
    assert decision.department == "Claims"
