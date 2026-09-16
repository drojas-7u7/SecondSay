from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_mode: str = "cloud"

    cloud_llm_provider: str = ""
    cloud_llm_api_key: SecretStr = SecretStr("")
    cloud_llm_model: str = ""

    local_llm_provider: str = "ollama"
    local_llm_model: str = ""
    local_llm_base_url: str = "http://127.0.0.1:11434"

    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
