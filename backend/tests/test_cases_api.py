from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_triage_case_endpoint() -> None:
    response = client.post(
        "/api/v1/cases/triage",
        json={
            "content": "Hay una fuga de agua que ha dañado la cocina y la vivienda vecina.",
            "input_type": "TEXT",
            "domain_profile": "insurance",
            "external_id": "CLAIM-001",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "decision": {
            "category": "Incidente general",
            "urgency": "MEDIA",
            "summary": (
                "El caso requiere revisión estructurada antes de validación humana final"
            ),
            "department": "Siniestros",
            "justification": (
                "El caso necesita revisión estructurada antes de una decisión humana final."
            ),
        },
        "metrics": {
            "provider": "fake",
            "model": "deterministic-demo",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0.0,
            "estimated_cost": 0.0,
        },
    }
