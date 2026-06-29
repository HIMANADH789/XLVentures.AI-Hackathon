import json
from datetime import datetime

try:
    import redis as redis_lib

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class MemoryStore:
    """Dual-backend persistent store for company profiles and user configs.

    Supports Redis (when available) with automatic fallback to an in-memory dict.
    Key namespaces:
      - company:<url>  -- company profiles and analysis results
      - user_config:<id> -- per-user platform configuration
    """
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._use_redis = False
        if HAS_REDIS:
            try:
                self._client = redis_lib.Redis(
                    host="localhost",
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                self._client.ping()
                self._use_redis = True
            except Exception:
                print("Redis not available, using in-memory storage")

    def _key(self, company_url: str) -> str:
        return f"company:{company_url}"

    def _user_config_key(self, user_id: str) -> str:
        return f"user_config:{user_id}"

    def save_company_profile(self, company_url: str, data: dict) -> None:
        """Persist a company profile, auto-adding timestamp and status.

        Derives status from is_qualified/approval_status:
          - rejected → "rejected"
          - is_qualified → "qualified"
          - otherwise → "not_qualified"
        """
        data = dict(data)
        data["timestamp"] = datetime.now().isoformat()
        if "is_qualified" in data and "approval_status" in data:
            if data["approval_status"] == "rejected":
                data["status"] = "rejected"
            elif data["is_qualified"]:
                data["status"] = "qualified"
            else:
                data["status"] = "not_qualified"
        if self._use_redis:
            self._client.set(self._key(company_url), json.dumps(data))
        else:
            self._store[company_url] = data

    def get_company_profile(self, company_url: str) -> dict | None:
        """Retrieve a previously saved company profile by URL."""
        if self._use_redis:
            raw = self._client.get(self._key(company_url))
            return json.loads(raw) if raw else None
        return self._store.get(company_url)

    def get_prospect_intelligence(self, company_url: str) -> dict | None:
        """Convenience method to retrieve only the prospect_intelligence sub-dict."""
        profile = self.get_company_profile(company_url)
        if profile:
            return profile.get("prospect_intelligence")
        return None

    def save_interaction(self, company_url: str, action: str) -> None:
        """Append an interaction event to an existing company profile."""
        profile = self.get_company_profile(company_url) or {}
        interactions = profile.get("interactions", [])
        interactions.append(action)
        profile["interactions"] = interactions
        self.save_company_profile(company_url, profile)

    def save_user_config(self, user_id: str, config_data: dict) -> None:
        """Persist platform configuration for a specific user ID."""
        key = self._user_config_key(user_id)
        if self._use_redis:
            self._client.set(key, json.dumps(config_data))
        else:
            self._store[key] = config_data

    def get_user_config(self, user_id: str) -> dict | None:
        """Retrieve saved platform configuration for a user ID."""
        key = self._user_config_key(user_id)
        if self._use_redis:
            raw = self._client.get(key)
            return json.loads(raw) if raw else None
        return self._store.get(key)

    def get_all_profiles(self) -> dict[str, dict]:
        """Return all company profiles (excluding user config entries)."""
        if self._use_redis:
            keys = self._client.keys("company:*")
            profiles = {}
            for key in keys:
                url = key.replace("company:", "", 1)
                raw = self._client.get(key)
                if raw:
                    profiles[url] = json.loads(raw)
            return profiles
        return {
            k: v for k, v in self._store.items()
            if k.startswith("company:")
        }

    def clear(self) -> None:
        if self._use_redis:
            for key in self._client.keys("company:*"):
                self._client.delete(key)
        else:
            self._store = {
                k: v for k, v in self._store.items()
                if not k.startswith("company:")
            }


_store: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store
