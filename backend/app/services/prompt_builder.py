import json

from app.schemas.case import CaseCreate
from app.services.domain_profile_loader import DomainProfileLoader


class PromptBuilder:
    def __init__(
        self,
        profile_loader: DomainProfileLoader | None = None,
    ) -> None:
        self.profile_loader = profile_loader or DomainProfileLoader()

    def build(self, case: CaseCreate) -> str:
        domain = self.profile_loader.load(case.domain_profile)

        profile = domain["profile"]
        rules = domain["rules"]["rules"]
        anti_bias = domain["anti_bias"]["principles"]
        examples = domain["few_shots"]["examples"]

        categories = "\n".join(
            f"- {category}" for category in profile["categories"]
        )
        urgencies = "\n".join(
            f"- {urgency}" for urgency in profile["urgencies"]
        )
        departments = "\n".join(
            f"- {department}" for department in profile["departments"]
        )

        domain_rules = "\n".join(
            f"- {rule['description'].strip()}" for rule in rules
        )
        anti_bias_rules = "\n".join(
            f"- {principle['instruction'].strip()}"
            for principle in anti_bias
        )

        few_shots = "\n\n".join(
            (
                f"Ejemplo {index}\n"
                f"Entrada:\n{example['input'].strip()}\n"
                "Salida esperada:\n"
                f"{json.dumps(example['output'], ensure_ascii=False, indent=2)}"
            )
            for index, example in enumerate(examples, start=1)
        )

        return (
            "Eres un asistente de inteligencia artificial especializado "
            "en triaje de casos.\n\n"
            f"Perfil de dominio: {profile['name']}\n"
            f"{profile['description'].strip()}\n\n"
            "OBJETIVO\n"
            "Analiza el caso recibido y devuelve una decisión estructurada.\n"
            "RAZONAMIENTO INTERNO (CHAIN-OF-THOUGHT / COT)\n"
            "Antes de responder, analiza internamente paso a paso los hechos "
            "relevantes del caso para determinar categoría, urgencia y departamento.\n"
            "No expongas la cadena de razonamiento completa. Devuelve únicamente "
            "los campos solicitados y una justificación breve y auditable que resuma "
            "los factores determinantes de la decisión.\n\n"
            "CATEGORÍAS PERMITIDAS\n"
            f"{categories}\n\n"
            "URGENCIAS PERMITIDAS\n"
            f"{urgencies}\n\n"
            "DEPARTAMENTOS PERMITIDOS\n"
            f"{departments}\n\n"
            "REGLAS DEL DOMINIO\n"
            f"{domain_rules}\n\n"
            "REGLAS ANTI-SESGO\n"
            f"{anti_bias_rules}\n\n"
            "EJEMPLOS FEW-SHOT\n"
            f"{few_shots}\n\n"
            "CASO A ANALIZAR\n"
            f"{case.content}\n\n"
            "FORMATO DE SALIDA OBLIGATORIO\n"
            "Devuelve exclusivamente un objeto estructurado con estas claves:\n"
            "- category\n"
            "- urgency\n"
            "- summary\n"
            "- department\n"
            "- justification\n\n"
            "La categoría debe pertenecer a las categorías permitidas.\n"
            "La urgencia debe pertenecer a las urgencias permitidas.\n"
            "El departamento debe pertenecer a los departamentos permitidos.\n"
            "El resumen debe contener exactamente 10 palabras.\n"
            "Todos los valores destinados al usuario deben estar en castellano.\n"
            "La justificación debe ser breve, clara y basada únicamente "
            "en la información disponible.\n"
            "No inventes información ausente en el caso."
        )
