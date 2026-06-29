import requests
from config import settings
from utils.retry import with_retries

@with_retries(max_retries=3, initial_delay=1.0)
def find_emails(domain: str) -> list:
    """Look up contacts for a domain via Hunter.

    Returns:
        list of contact dicts with keys: name, role, email, linkedin, phone, source
    """
    api_key = settings.hunter_api_key
    if not api_key:
        print("[HUNTER API] HUNTER_API_KEY not set — skipping email lookup")
        return []

    print(f"[HUNTER API] Looking up domain: {domain}")
    try:
        url = "https://api.hunter.io/v2/domain-search"
        params = {"domain": domain, "api_key": api_key}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            body = response.json()
            data = body.get("data", {})
            emails = data.get("emails", [])
            print(f"[HUNTER API] Found {len(emails)} contacts for {domain}")
            contacts = []
            for entry in emails:
                first_name = entry.get("first_name") or ""
                last_name = entry.get("last_name") or ""
                name = f"{first_name} {last_name}".strip()
                email = entry.get("value")
                if not name and email:
                    name = email.split("@")[0]
                if not name:
                    continue
                contacts.append({
                    "name": name,
                    "role": entry.get("position") or None,
                    "email": email or None,
                    "linkedin": entry.get("linkedin_url") or None,
                    "phone": None,
                    "source": "Hunter"
                })
            return contacts
        else:
            print(f"[HUNTER API] HTTP {response.status_code} for {domain}: {response.text[:200]}")
    except Exception as e:
        print(f"[HUNTER API ERROR] Failed to fetch data for {domain}: {e}")

    return []
