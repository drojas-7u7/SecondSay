from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision, Urgency


class TriageService:
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
