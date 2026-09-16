from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.case import CaseCreate, CaseTriageResponse, InputType
from app.schemas.llm import LLMExecutionMetrics
from app.schemas.triage import TriageDecision, Urgency


def test_valid_text_case() -> None:
    case = CaseCreate(
        content="Water leak has damaged the kitchen and neighboring property.",
        input_type=InputType.TEXT,
        domain_profile="insurance",
        external_id="CLAIM-001",
    )

    assert case.content.startswith("Water leak")
    assert case.input_type == InputType.TEXT
    assert case.domain_profile == "insurance"
    assert case.external_id == "CLAIM-001"


def test_text_is_default_input_type() -> None:
    case = CaseCreate(
        content="Customer reports damage caused by a water leak."
    )

    assert case.input_type == InputType.TEXT


def test_empty_content_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CaseCreate(content="")


def test_unknown_input_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CaseCreate(
            content="Valid incident description.",
            input_type="AUDIO",
        )


def test_case_triage_response_includes_persistence_ids() -> None:
    case_id = uuid4()
    ai_decision_id = uuid4()

    response = CaseTriageResponse(
        case_id=case_id,
        ai_decision_id=ai_decision_id,
        decision=TriageDecision(
            category="Daños por agua",
            urgency=Urgency.MEDIUM,
            summary="La fuga afecta vivienda vecina y requiere inspección urgente hoy",
            department="Siniestros",
            justification="La incidencia requiere revisión técnica del daño comunicado.",
        ),
        metrics=LLMExecutionMetrics(
            provider="fake",
            model="deterministic-demo",
            input_tokens=10,
            output_tokens=20,
            latency_ms=15.5,
            estimated_cost=0.0,
        ),
    )

    assert response.case_id == case_id
    assert response.ai_decision_id == ai_decision_id
    assert response.decision.urgency == Urgency.MEDIUM

