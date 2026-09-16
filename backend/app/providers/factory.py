from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeLLMProvider
from app.providers.groq import GroqProvider
from app.providers.ollama import OllamaProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    mode = settings.llm_mode.strip().lower()

    if mode == "local":
        provider_name = settings.local_llm_provider.strip().lower()

        if provider_name == "ollama":
            return OllamaProvider(
                model=settings.local_llm_model,
                base_url=settings.local_llm_base_url,
            )

        raise ValueError(
            f"Unsupported local LLM provider: {settings.local_llm_provider}"
        )

    if mode != "cloud":
        raise ValueError(f"Unsupported LLM mode: {settings.llm_mode}")

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
