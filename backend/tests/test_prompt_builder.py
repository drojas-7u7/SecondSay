from app.schemas.case import CaseCreate
from app.services.prompt_builder import PromptBuilder


def test_prompt_builder_includes_case_and_output_rules() -> None:
    case = CaseCreate(
        content="Hay una fuga de agua que ha dañado la cocina y la vivienda vecina."
    )

    prompt = PromptBuilder().build(case)

    assert case.content in prompt
    assert "category" in prompt
    assert "urgency" in prompt
    assert "summary" in prompt
    assert "department" in prompt
    assert "justification" in prompt
    assert "exactamente 10 palabras" in prompt
    assert "castellano" in prompt
