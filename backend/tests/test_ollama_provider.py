import json

import httpx
import pytest

from app.providers.ollama import OllamaProvider, OllamaProviderError
from app.schemas.triage import Urgency


def test_ollama_provider_returns_structured_result() -> None:
    base_url = "http://127.0.0.1:11434"

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == f"{base_url}/api/generate"

        payload = json.loads(request.content)

        assert payload["model"] == "qwen3:4b-instruct"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0
        assert payload["format"]["additionalProperties"] is False

        response_content = json.dumps(
            {
                "category": "Daños por agua",
                "urgency": "ALTA",
                "summary": (
                    "La fuga afecta vivienda vecina y requiere inspección urgente hoy"
                ),
                "department": "Siniestros",
                "justification": (
                    "La información disponible requiere una revisión prioritaria."
                ),
            },
            ensure_ascii=False,
        )

        return httpx.Response(
            status_code=200,
            json={
                "model": "qwen3:4b-instruct",
                "response": response_content,
                "done": True,
                "prompt_eval_count": 100,
                "eval_count": 40,
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = OllamaProvider(
        model="qwen3:4b-instruct",
        base_url=base_url,
        client=client,
    )

    result = provider.generate("Caso de prueba")

    assert result.decision.category == "Daños por agua"
    assert result.decision.urgency == Urgency.HIGH
    assert result.decision.department == "Siniestros"

    assert result.metrics.provider == "ollama"
    assert result.metrics.model == "qwen3:4b-instruct"
    assert result.metrics.input_tokens == 100
    assert result.metrics.output_tokens == 40
    assert result.metrics.latency_ms >= 0
    assert result.metrics.estimated_cost == 0.0



def test_ollama_provider_rejects_invalid_structured_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "model": "qwen3:4b-instruct",
                "response": '{"category": "Daños por agua"}',
                "done": True,
                "prompt_eval_count": 10,
                "eval_count": 5,
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = OllamaProvider(
        model="qwen3:4b-instruct",
        base_url="http://127.0.0.1:11434",
        client=client,
    )

    with pytest.raises(OllamaProviderError):
        provider.generate("Caso de prueba")


def test_ollama_provider_retries_invalid_structured_response() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        payload = json.loads(request.content)

        if attempts == 1:
            return httpx.Response(
                status_code=200,
                json={
                    "model": "qwen3:4b-instruct",
                    "response": json.dumps(
                        {
                            "category": "Daños por agua",
                            "urgency": "ALTA",
                            "summary": (
                                "Fuga de agua en cocina afecta piso inferior y zona vecinal"
                            ),
                            "department": "Siniestros",
                            "justification": (
                                "La fuga requiere revisión prioritaria del siniestro."
                            ),
                        },
                        ensure_ascii=False,
                    ),
                    "done": True,
                    "prompt_eval_count": 100,
                    "eval_count": 40,
                },
            )

        assert "CORRECCIÓN OBLIGATORIA" in payload["prompt"]

        return httpx.Response(
            status_code=200,
            json={
                "model": "qwen3:4b-instruct",
                "response": json.dumps(
                    {
                        "category": "Daños por agua",
                        "urgency": "ALTA",
                        "summary": (
                            "La fuga afecta vivienda vecina y requiere inspección urgente hoy"
                        ),
                        "department": "Siniestros",
                        "justification": (
                            "La fuga requiere revisión prioritaria del siniestro."
                        ),
                    },
                    ensure_ascii=False,
                ),
                "done": True,
                "prompt_eval_count": 110,
                "eval_count": 38,
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))

    provider = OllamaProvider(
        model="qwen3:4b-instruct",
        base_url="http://127.0.0.1:11434",
        client=client,
    )

    result = provider.generate("Caso de prueba")

    assert attempts == 2
    assert result.decision.summary == (
        "La fuga afecta vivienda vecina y requiere inspección urgente hoy"
    )
