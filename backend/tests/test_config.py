from pathlib import Path

from pydantic import SecretStr

from app.core.config import ENV_FILE, Settings


def test_env_file_points_to_project_root() -> None:
    assert ENV_FILE.name == ".env"
    assert ENV_FILE.parent == Path(__file__).resolve().parents[2]


def test_settings_accept_cloud_llm_configuration() -> None:
    settings = Settings(
        cloud_llm_provider="groq",
        cloud_llm_api_key=SecretStr("test-key"),
        cloud_llm_model="openai/gpt-oss-20b",
    )

    assert settings.cloud_llm_provider == "groq"
    assert settings.cloud_llm_model == "openai/gpt-oss-20b"
    assert settings.cloud_llm_api_key.get_secret_value() == "test-key"

def test_settings_accept_database_configuration() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://secondsay:test-password@localhost:5432/secondsay",
    )

    assert (
        settings.database_url
        == "postgresql+psycopg://secondsay:test-password@localhost:5432/secondsay"
    )

