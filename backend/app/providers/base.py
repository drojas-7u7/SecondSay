from abc import ABC, abstractmethod

from app.schemas.llm import LLMResult


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot produce a valid result."""


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> LLMResult:
        """Generate a structured LLM result from a prompt."""
        raise NotImplementedError
