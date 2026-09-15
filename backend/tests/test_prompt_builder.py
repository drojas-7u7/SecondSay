from app.schemas.case import CaseCreate
from app.services.prompt_builder import PromptBuilder


def test_prompt_builder_includes_domain_configuration() -> None:
    case = CaseCreate(
        content="Hay una fuga de agua que ha dañado la cocina y la vivienda vecina.",
        domain_profile="insurance",
    )

    prompt = PromptBuilder().build(case)

    assert case.content in prompt

    assert "Perfil de dominio: Seguros" in prompt
    assert "Daños por agua" in prompt
    assert "CRÍTICA" in prompt
    assert "Responsabilidad Civil" in prompt

    assert "REGLAS DEL DOMINIO" in prompt
    assert "terceras personas" in prompt

    assert "REGLAS ANTI-SESGO" in prompt
    assert "género" in prompt
    assert "barrio" in prompt

    assert "EJEMPLOS FEW-SHOT" in prompt
    assert "Fuga de agua causa daños propios y a terceros afectados" in prompt

    assert "category" in prompt
    assert "urgency" in prompt
    assert "summary" in prompt
    assert "department" in prompt
    assert "justification" in prompt

    assert "exactamente 10 palabras" in prompt
    assert "castellano" in prompt
    assert "No inventes información" in prompt
