import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("INVENTORY_AGENT_SERVICE_NAME", "Inventory Agent")
    host: str = os.getenv("INVENTORY_AGENT_HOST", "0.0.0.0")
    port: int = int(os.getenv("INVENTORY_AGENT_PORT", "8000"))
    seed_examples: bool = _env_bool("INVENTORY_AGENT_SEED_EXAMPLES", True)


settings = Settings()
