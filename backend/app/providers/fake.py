from app.providers.base import LLMProvider
from app.schemas.triage import TriageDecision, Urgency


class FakeLLMProvider(LLMProvider):
    def generate(self, prompt: str) -> TriageDecision:
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
