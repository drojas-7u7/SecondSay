from abc import ABC, abstractmethod

from app.schemas.case import CaseCreate
from app.schemas.triage import TriageDecision


class LLMProvider(ABC):
    @abstractmethod
    def triage(self, case: CaseCreate) -> TriageDecision:
        """Generate a structured triage decision for a case."""
        raise NotImplementedError
