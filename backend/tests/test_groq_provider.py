import json

import httpx
import pytest

from app.providers.groq import (
    GROQ_CHAT_COMPLETIONS_URL,
    SUPPORTED_MODEL,
    GroqProvider,
    GroqProviderError,
)
from app.schemas.triage import Urgency


def build_success_response() -> httpx.Response:
    content = json.dumps(
        {
            "category": "Daños por agua",
            "urgency": "ALTA",
            "summary": (
                "La fuga afecta vivienda vecina y requiere inspección urgente hoy"
            ),
            "department": "Siniestros",
            "justification": (
                "La información disponible indica daños que requieren revisión prioritaria."
            ),
        },
        ensure_ascii=False,
    )

    return httpx.Response(
        status_code=200,
        json={
            "choices": [
                {
                    "message": {
                        "content": content,
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 40,
            },
        },
    )


def test_groq_provider_returns_structured_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == GROQ_CHAT_COMPLETIONS_URL
        assert request.headers["authorization"] == "Bearer test-key"

        payload = json.loads(request.content)

        assert payload["model"] == SUPPORTED_MODEL
        assert payload["response_format"]["type"] == "json_schema"
        assert payload["response_format"]["json_schema"]["strict"] is True
        assert (
            payload["response_format"]["json_schema"]["schema"][
                "additionalProperties"
            ]
            is False
        )

        return build_success_response()

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
    )

    result = provider.generate("Caso de prueba")

    assert result.decision.category == "Daños por agua"
    assert result.decision.urgency == Urgency.HIGH
    assert result.decision.department == "Siniestros"

    assert result.metrics.provider == "groq"
    assert result.metrics.model == SUPPORTED_MODEL
    assert result.metrics.input_tokens == 100
    assert result.metrics.output_tokens == 40
    assert result.metrics.latency_ms >= 0
    assert result.metrics.estimated_cost == pytest.approx(0.0000195)


def test_groq_provider_rejects_invalid_structured_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"category": "Daños por agua"}',
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                },
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
    )

    with pytest.raises(GroqProviderError):
        provider.generate("Caso de prueba")


def test_groq_provider_retries_rate_limit_and_respects_retry_after() -> None:
    attempts = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                status_code=429,
                headers={"retry-after": "0.25"},
                json={"error": {"message": "Rate limit exceeded"}},
            )

        return build_success_response()

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
        sleeper=delays.append,
    )

    result = provider.generate("Caso de prueba")

    assert result.decision.category == "Daños por agua"
    assert attempts == 2
    assert delays == [0.25]


def test_groq_provider_uses_exponential_backoff_without_retry_after() -> None:
    attempts = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                status_code=503,
                json={"error": {"message": "Service unavailable"}},
            )

        return build_success_response()

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
        sleeper=delays.append,
    )

    provider.generate("Caso de prueba")

    assert attempts == 2
    assert delays == [0.5]


def test_groq_provider_stops_after_maximum_attempts() -> None:
    attempts = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status_code=429,
            json={"error": {"message": "Rate limit exceeded"}},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
        sleeper=delays.append,
    )

    with pytest.raises(GroqProviderError):
        provider.generate("Caso de prueba")

    assert attempts == 3
    assert delays == [0.5, 1.0]


def test_groq_provider_does_not_retry_unauthorized_request() -> None:
    attempts = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status_code=401,
            json={"error": {"message": "Unauthorized"}},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = GroqProvider(
        api_key="test-key",
        model=SUPPORTED_MODEL,
        client=client,
        sleeper=delays.append,
    )

    with pytest.raises(GroqProviderError):
        provider.generate("Caso de prueba")

    assert attempts == 1
    assert delays == []

