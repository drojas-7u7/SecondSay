import pytest
from pydantic import SecretStr

from app.core.config import Settings
from app.providers.factory import build_llm_provider
from app.providers.fake import FakeLLMProvider
from app.providers.groq import GroqProvider


def test_provider_factory_uses_fake_provider_by_default() -> None:
    settings = Settings(
        cloud_llm_provider="",
        cloud_llm_api_key=SecretStr(""),
        cloud_llm_model="",
    )

    provider = build_llm_provider(settings)

    assert isinstance(provider, FakeLLMProvider)


def test_provider_factory_builds_fake_provider() -> None:
    settings = Settings(
        cloud_llm_provider="fake",
        cloud_llm_api_key=SecretStr(""),
        cloud_llm_model="",
    )

    provider = build_llm_provider(settings)

    assert isinstance(provider, FakeLLMProvider)


def test_provider_factory_builds_groq_provider() -> None:
    settings = Settings(
        cloud_llm_provider="groq",
        cloud_llm_api_key=SecretStr("test-key"),
        cloud_llm_model="openai/gpt-oss-20b",
    )

    provider = build_llm_provider(settings)

    assert isinstance(provider, GroqProvider)
    assert provider.model == "openai/gpt-oss-20b"


def test_provider_factory_rejects_unknown_provider() -> None:
    settings = Settings(
        cloud_llm_provider="unknown",
        cloud_llm_api_key=SecretStr("test-key"),
        cloud_llm_model="some-model",
    )

    with pytest.raises(ValueError):
        build_llm_provider(settings)


def test_provider_factory_builds_local_provider() -> None:
    settings = Settings(
        llm_mode="local",
        cloud_llm_provider="",
        cloud_llm_api_key=SecretStr(""),
        cloud_llm_model="",
        local_llm_provider="ollama",
        local_llm_model="qwen3:4b-instruct",
        local_llm_base_url="http://127.0.0.1:11434",
    )

    provider = build_llm_provider(settings)

    assert provider.__class__.__name__ == "OllamaProvider"
