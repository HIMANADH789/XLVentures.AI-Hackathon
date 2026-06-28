import requests
from config import settings
from utils.retry import with_retries

@with_retries(max_retries=3, initial_delay=1.0)
def find_contacts(domain: str) -> list:
    api_key = settings.apollo_api_key
    if not api_key:
        return []

    try:
        url = "https://api.apollo.io/api/v1/mixed_people/search"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        payload = {
            "api_key": api_key,
            "organization_domains": [domain],
            "per_page": 5
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            contacts = data.get("contacts", [])
            results = []
            for c in contacts:
                first_name = c.get("first_name") or ""
                last_name = c.get("last_name") or ""
                name = c.get("name") or f"{first_name} {last_name}".strip() or None
                if not name:
                    continue
                results.append({
                    "name": name,
                    "role": c.get("title") or None,
                    "email": c.get("email") or None,
                    "linkedin": c.get("linkedin_url") or None,
                    "phone": None,
                    "source": "Apollo"
                })
            return results
    except Exception as e:
        print(f"[APOLLO API ERROR] Failed to fetch contacts for {domain}: {e}")
        
    return []
