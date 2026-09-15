from app.providers.base import LLMProvider
from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision, Urgency


class FakeLLMProvider(LLMProvider):
    def triage(self, case: CaseCreate) -> TriageDecision:
        return TriageDecision(
            category="General incident",
            urgency=Urgency.MEDIUM,
            summary=(
                "Incoming case requires structured review before final "
                "human validation today"
            ),
            department="Claims",
        )
