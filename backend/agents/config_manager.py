from .config import DEFAULT_CONFIG
from .tools.memory import MemoryStore, get_memory_store


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """Load and save platform configuration with MemoryStore overrides.

    Starts with DEFAULT_CONFIG from config.py, then deep-merges any
    previously saved user configuration from the MemoryStore.
    """
    def __init__(
        self,
        user_id: str = "default",
        memory_store: MemoryStore | None = None,
    ):
        self.user_id = user_id
        self.store = memory_store or get_memory_store()

    def get_config(self) -> dict:
        """Return the merged configuration (defaults + user overrides)."""
        config = dict(DEFAULT_CONFIG)
        saved = self.store.get_user_config(self.user_id)
        if saved:
            config = _deep_merge(config, saved)
        return config

    def save_config(self, config_data: dict) -> None:
        """Persist user configuration overrides to the MemoryStore."""
        self.store.save_user_config(self.user_id, config_data)
