from collections.abc import Iterator
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db_session
from app.main import app
from app.models import AuditRecord, Base
from app.providers.fake import FakeLLMProvider
from app.repositories import CaseRepository
from app.schemas.case import CaseCreate

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


def create_persisted_decision() -> str:
    with session_factory() as session:
        _, decision_record = CaseRepository().create_with_decision(
            session=session,
            case=CaseCreate(content="Hay una fuga de agua en la cocina."),
            result=FakeLLMProvider().generate("test prompt"),
        )
        session.commit()

        return str(decision_record.id)


def test_review_ai_decision_endpoint_persists_discrepancy() -> None:
    ai_decision_id = create_persisted_decision()
    app.dependency_overrides[get_db_session] = override_db_session

    try:
        response = client.post(
            "/api/v1/audits/review",
            json={
                "ai_decision_id": ai_decision_id,
                "human_review": {
                    "final_category": "Incidente general",
                    "final_urgency": "ALTA",
                    "final_department": "Responsabilidad Civil",
                    "review_note": "Existe afectación a terceros.",
                    "discrepancy_impact": "ALTO",
                },
            },
        )
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200

    body = response.json()

    assert body["has_discrepancy"] is True
    assert body["changed_fields"] == [
        "urgencia",
        "departamento",
    ]
    assert body["ai_decision"]["urgency"] == "MEDIA"
    assert body["human_review"]["final_urgency"] == "ALTA"
    assert body["human_review"]["discrepancy_impact"] == "ALTO"

    with session_factory() as session:
        stored_audit = session.scalar(
            select(AuditRecord).where(
                AuditRecord.ai_decision_id == UUID(ai_decision_id)
            )
        )

        assert stored_audit is not None
        assert stored_audit.has_discrepancy is True


def test_review_ai_decision_endpoint_returns_404_for_unknown_decision() -> None:
    app.dependency_overrides[get_db_session] = override_db_session

    try:
        response = client.post(
            "/api/v1/audits/review",
            json={
                "ai_decision_id": str(uuid4()),
                "human_review": {
                    "final_category": "Incidente general",
                    "final_urgency": "MEDIA",
                    "final_department": "Siniestros",
                    "discrepancy_impact": None,
                },
            },
        )
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No se encontró la decisión de IA indicada."
    }
