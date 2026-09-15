import pytest
from pydantic import ValidationError

from app.schemas.llm import LLMExecutionMetrics, LLMResult
from app.schemas.triage import TriageDecision, Urgency


def build_decision() -> TriageDecision:
    return TriageDecision(
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


def test_llm_result_accepts_valid_metrics() -> None:
    result = LLMResult(
        decision=build_decision(),
        metrics=LLMExecutionMetrics(
            provider="fake",
            model="fake-model",
            input_tokens=100,
            output_tokens=40,
            latency_ms=125.5,
            estimated_cost=0.0,
        ),
    )

    assert result.decision.urgency == Urgency.MEDIUM
    assert result.metrics.provider == "fake"
    assert result.metrics.input_tokens == 100
    assert result.metrics.estimated_cost == 0.0


def test_llm_metrics_reject_negative_values() -> None:
    with pytest.raises(ValidationError):
        LLMExecutionMetrics(
            provider="fake",
            model="fake-model",
            input_tokens=-1,
            output_tokens=40,
            latency_ms=125.5,
            estimated_cost=0.0,
        )


def test_llm_metrics_reject_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        LLMExecutionMetrics(
            provider="fake",
            model="fake-model",
            input_tokens=100,
            output_tokens=40,
            latency_ms=125.5,
            estimated_cost=0.0,
            unexpected_field="not-allowed",
        )
