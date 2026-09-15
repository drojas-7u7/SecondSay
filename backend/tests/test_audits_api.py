from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_review_ai_decision_endpoint_detects_discrepancy() -> None:
    response = client.post(
        "/api/v1/audits/review",
        json={
            "ai_decision": {
                "category": "Daños por agua",
                "urgency": "MEDIA",
                "summary": (
                    "La fuga afecta vivienda vecina y requiere inspección urgente hoy"
                ),
                "department": "Siniestros",
                "justification": (
                    "La información disponible requiere revisión estructurada "
                    "del siniestro."
                ),
            },
            "human_review": {
                "final_category": "Daños por agua",
                "final_urgency": "ALTA",
                "final_department": "Responsabilidad Civil",
                "review_note": "Existe afectación a terceros.",
                "discrepancy_impact": "ALTO",
            },
        },
    )

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
