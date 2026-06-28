import requests
from config import settings
from utils.retry import with_retries

@with_retries(max_retries=3, initial_delay=1.0)
def find_emails(domain: str) -> list:
    api_key = settings.hunter_api_key
    if not api_key:
        return []

    try:
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain,
            "api_key": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", {})
            emails = data.get("emails", [])
            results = []
            for entry in emails:
                first_name = entry.get("first_name") or ""
                last_name = entry.get("last_name") or ""
                name = f"{first_name} {last_name}".strip() or None
                if not name:
                    continue
                results.append({
                    "name": name,
                    "role": entry.get("position") or None,
                    "email": entry.get("value") or None,
                    "linkedin": entry.get("linkedin_url") or None,
                    "phone": None,
                    "source": "Hunter"
                })
            return results
    except Exception as e:
        print(f"[HUNTER API ERROR] Failed to fetch emails for {domain}: {e}")
        
    return []
