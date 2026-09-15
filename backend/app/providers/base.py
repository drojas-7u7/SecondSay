from abc import ABC, abstractmethod

from app.schemas.triage import TriageDecision


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> TriageDecision:
        """Generate a structured triage decision from a prompt."""
        raise NotImplementedError
