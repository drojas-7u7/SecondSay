from time import perf_counter

import httpx
from pydantic import ValidationError

from app.providers.base import LLMProvider
from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision

MAX_VALIDATION_ATTEMPTS = 2


class OllamaProviderError(RuntimeError):
    """Raised when Ollama cannot produce a valid triage result."""


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str,
        base_url: str,
        client: httpx.Client | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("Ollama model is required.")

        if not base_url.strip():
            raise ValueError("Ollama base URL is required.")

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    def generate(self, prompt: str) -> LLMResult:
        started_at = perf_counter()
        current_prompt = prompt
        total_input_tokens = 0
        total_output_tokens = 0
        last_validation_error: ValidationError | None = None

        for attempt in range(MAX_VALIDATION_ATTEMPTS):
            body = self._generate_response(current_prompt)

            try:
                input_tokens = int(body["prompt_eval_count"])
                output_tokens = int(body["eval_count"])
                response_content = body["response"]
            except (KeyError, TypeError, ValueError) as exc:
                raise OllamaProviderError(
                    "Ollama returned an invalid response."
                ) from exc

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            try:
                decision = TriageDecision.model_validate_json(response_content)
            except ValidationError as exc:
                last_validation_error = exc

                if attempt == MAX_VALIDATION_ATTEMPTS - 1:
                    break

                current_prompt = self._build_correction_prompt(prompt)
                continue

            latency_ms = (perf_counter() - started_at) * 1000

            metrics = LLMExecutionMetrics(
                provider="ollama",
                model=self.model,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                latency_ms=latency_ms,
                estimated_cost=0.0,
            )

            return LLMResult(
                decision=decision,
                metrics=metrics,
            )

        raise OllamaProviderError(
            "Ollama returned an invalid response."
        ) from last_validation_error

    def _generate_response(self, prompt: str) -> dict[str, object]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": TriageDecision.model_json_schema(),
            "options": {
                "temperature": 0,
            },
        }

        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError("Ollama request failed.") from exc

        if not isinstance(body, dict):
            raise OllamaProviderError("Ollama returned an invalid response.")

        return body

    @staticmethod
    def _build_correction_prompt(prompt: str) -> str:
        return (
            f"{prompt}\n\n"
            "CORRECCIÓN OBLIGATORIA\n"
            "La respuesta anterior no cumplió todas las restricciones del "
            "esquema. Genera de nuevo la respuesta completa.\n"
            "Respeta estrictamente todos los campos y valores permitidos.\n"
            "El campo summary debe contener exactamente 10 palabras."
        )
