from app.schemas.case import CaseCreate


class PromptBuilder:
    def build(self, case: CaseCreate) -> str:
        return (
            "Eres un asistente de inteligencia artificial especializado en triaje.\n\n"
            "Analiza el siguiente caso y devuelve una decisión estructurada.\n\n"
            f"Caso:\n{case.content}\n\n"
            "Devuelve los siguientes campos:\n"
            "- category\n"
            "- urgency\n"
            "- summary\n"
            "- department\n"
            "- justification\n\n"
            "El resumen debe contener exactamente 10 palabras.\n"
            "La categoría, el resumen, el departamento y la justificación "
            "deben estar redactados en castellano.\n"
            "La justificación debe ser breve, clara y basada únicamente "
            "en la información disponible en el caso."
        )
