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

    cloud_llm_provider: str = ""
    cloud_llm_api_key: SecretStr = SecretStr("")
    cloud_llm_model: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
