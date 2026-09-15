from app.providers.base import LLMProvider
from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision, Urgency


class FakeLLMProvider(LLMProvider):
    def generate(self, prompt: str) -> LLMResult:
        decision = TriageDecision(
            category="Incidente general",
            urgency=Urgency.MEDIUM,
            summary=(
                "El caso requiere revisión estructurada antes de validación humana final"
            ),
            department="Siniestros",
            justification=(
                "El caso necesita revisión estructurada antes de una decisión humana final."
            ),
        )

        metrics = LLMExecutionMetrics(
            provider="fake",
            model="deterministic-demo",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0,
            estimated_cost=0.0,
        )

        return LLMResult(
            decision=decision,
            metrics=metrics,
        )
