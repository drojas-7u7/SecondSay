from collections.abc import Iterator
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.cases import get_llm_provider
from app.core.database import get_db_session
from app.main import app
from app.models import AIDecisionRecord, Base, CaseRecord
from app.providers.fake import FakeLLMProvider

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(engine)
session_factory = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_db_session() -> Iterator[Session]:
    with session_factory() as session:
        yield session


client = TestClient(app)


def test_triage_case_endpoint_persists_case_and_decision() -> None:
    app.dependency_overrides[get_llm_provider] = FakeLLMProvider
    app.dependency_overrides[get_db_session] = override_db_session

    try:
        response = client.post(
            "/api/v1/cases/triage",
            json={
                "content": (
                    "Hay una fuga de agua que ha dañado la cocina "
                    "y la vivienda vecina."
                ),
                "input_type": "TEXT",
                "domain_profile": "insurance",
                "external_id": "CLAIM-001",
            },
        )
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200

    body = response.json()

    assert body["case_id"]
    assert body["ai_decision_id"]
    assert body["decision"] == {
        "category": "Incidente general",
        "urgency": "MEDIA",
        "summary": (
            "El caso requiere revisión estructurada antes de validación humana final"
        ),
        "department": "Siniestros",
        "justification": (
            "El caso necesita revisión estructurada antes de una decisión humana final."
        ),
    }
    assert body["metrics"] == {
        "provider": "fake",
        "model": "deterministic-demo",
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": 0.0,
        "estimated_cost": 0.0,
    }

    with session_factory() as session:
        stored_case = session.scalar(
            select(CaseRecord).where(CaseRecord.id == UUID(body["case_id"]))
        )
        stored_decision = session.scalar(
            select(AIDecisionRecord).where(
                AIDecisionRecord.id == UUID(body["ai_decision_id"])
            )
        )

        assert stored_case is not None
        assert stored_case.external_id == "CLAIM-001"
        assert stored_decision is not None
        assert stored_decision.case_id == stored_case.id
        assert stored_decision.urgency == "MEDIA"
