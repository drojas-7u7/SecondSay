from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_triage_case_endpoint() -> None:
    response = client.post(
        "/api/v1/cases/triage",
        json={
            "content": "Water leak has damaged the kitchen and neighboring property.",
            "input_type": "TEXT",
            "domain_profile": "insurance",
            "external_id": "CLAIM-001",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "General incident",
        "urgency": "MEDIUM",
        "summary": (
            "Incoming case requires structured review before final "
            "human validation today"
        ),
        "department": "Claims",
    }
