from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeLLMProvider
from app.providers.groq import GroqProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    provider_name = settings.cloud_llm_provider.strip().lower()

    if provider_name in {"", "fake"}:
        return FakeLLMProvider()

    if provider_name == "groq":
        return GroqProvider(
            api_key=settings.cloud_llm_api_key.get_secret_value(),
            model=settings.cloud_llm_model,
        )

    raise ValueError(
        f"Unsupported cloud LLM provider: {settings.cloud_llm_provider}"
    )
