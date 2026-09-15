import pytest

from app.services.domain_profile_loader import DomainProfileLoader


def test_load_insurance_domain_profile() -> None:
    loader = DomainProfileLoader()

    data = loader.load("insurance")

    assert data["profile"]["id"] == "insurance"
    assert data["profile"]["name"] == "Seguros"
    assert data["rules"]["rules"]
    assert data["anti_bias"]["principles"]
    assert data["few_shots"]["examples"]


def test_unknown_domain_profile_is_rejected() -> None:
    loader = DomainProfileLoader()

    with pytest.raises(
        ValueError,
        match="Perfil de dominio desconocido",
    ):
        loader.load("unknown-profile")
