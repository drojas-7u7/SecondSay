from collections.abc import Callable
from time import perf_counter, sleep

import httpx

from app.providers.base import LLMProvider, LLMProviderError
from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

SUPPORTED_MODEL = "openai/gpt-oss-20b"

INPUT_PRICE_USD_PER_MILLION = 0.075
OUTPUT_PRICE_USD_PER_MILLION = 0.30

MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 0.5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GroqProviderError(LLMProviderError):
    """Raised when Groq cannot produce a valid triage result."""


class GroqProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        client: httpx.Client | None = None,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if not api_key.strip():
            raise ValueError("Groq API key is required.")

        if model != SUPPORTED_MODEL:
            raise ValueError(
                f"Unsupported Groq model: {model}. "
                f"Expected {SUPPORTED_MODEL}."
            )

        self.api_key = api_key
        self.model = model
        self.client = client or httpx.Client(timeout=30.0)
        self.sleeper = sleeper

    def generate(self, prompt: str) -> LLMResult:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "triage_decision",
                    "strict": True,
                    "schema": TriageDecision.model_json_schema(),
                },
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        started_at = perf_counter()

        response = self._post_with_retry(
            headers=headers,
            payload=payload,
        )

        latency_ms = (perf_counter() - started_at) * 1000

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            usage = body["usage"]

            decision = TriageDecision.model_validate_json(content)

            input_tokens = int(usage["prompt_tokens"])
            output_tokens = int(usage["completion_tokens"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise GroqProviderError(
                "Groq returned an invalid response."
            ) from exc

        estimated_cost = (
            input_tokens * INPUT_PRICE_USD_PER_MILLION
            + output_tokens * OUTPUT_PRICE_USD_PER_MILLION
        ) / 1_000_000

        metrics = LLMExecutionMetrics(
            provider="groq",
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            estimated_cost=estimated_cost,
        )

        return LLMResult(
            decision=decision,
            metrics=metrics,
        )

    def _post_with_retry(
        self,
        *,
        headers: dict[str, str],
        payload: dict[str, object],
    ) -> httpx.Response:
        last_error: httpx.HTTPError | None = None

        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.client.post(
                    GROQ_CHAT_COMPLETIONS_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                last_error = exc

                if (
                    exc.response.status_code not in RETRYABLE_STATUS_CODES
                    or attempt == MAX_ATTEMPTS - 1
                ):
                    break

                self.sleeper(
                    self._retry_delay_seconds(
                        response=exc.response,
                        attempt=attempt,
                    )
                )
            except httpx.RequestError as exc:
                last_error = exc

                if attempt == MAX_ATTEMPTS - 1:
                    break

                self.sleeper(self._exponential_backoff(attempt))

        raise GroqProviderError("Groq request failed.") from last_error

    @staticmethod
    def _exponential_backoff(attempt: int) -> float:
        return BASE_BACKOFF_SECONDS * (2**attempt)

    @classmethod
    def _retry_delay_seconds(
        cls,
        *,
        response: httpx.Response,
        attempt: int,
    ) -> float:
        retry_after = response.headers.get("retry-after")

        if retry_after is not None:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass

        return cls._exponential_backoff(attempt)

