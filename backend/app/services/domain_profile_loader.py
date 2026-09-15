from pathlib import Path
from typing import Any

import yaml


class DomainProfileLoader:
    def __init__(self, profiles_dir: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[3]

        self.profiles_dir = profiles_dir or project_root / "domain-profiles"

    def load(self, profile_id: str) -> dict[str, Any]:
        profile_dir = self.profiles_dir / profile_id

        if not profile_dir.is_dir():
            raise ValueError(f"Perfil de dominio desconocido: {profile_id}")

        return {
            "profile": self._load_yaml(profile_dir / "profile.yaml"),
            "rules": self._load_yaml(profile_dir / "rules.yaml"),
            "anti_bias": self._load_yaml(profile_dir / "anti_bias.yaml"),
            "few_shots": self._load_yaml(profile_dir / "few_shots.yaml"),
        }

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"No se encuentra el archivo de perfil: {path}")

        with path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise TypeError(f"El archivo YAML no contiene un objeto válido: {path}")

        return data
