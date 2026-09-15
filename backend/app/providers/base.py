from abc import ABC, abstractmethod

from app.schemas.llm import LLMResult


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> LLMResult:
        """Generate a structured LLM result from a prompt."""
        raise NotImplementedError
