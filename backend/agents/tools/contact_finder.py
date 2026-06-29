import os

import requests


def find_contacts(company_domain: str, personas: list[str]) -> list[dict]:
    """Search Hunter.io for real contacts at a company domain, filtered by persona roles.

    Calls the Hunter.io ``/domain-search`` endpoint with the given domain.
    Results are filtered to match the requested persona roles (e.g. "CEO",
    "Founder", "VP").  If no persona match is found, returns the first few
    contacts found by Hunter as a best-effort.

    Fallback:
      - If ``HUNTER_API_KEY`` is not set, returns a single entry indicating
        the API key is missing.
      - If the API responds with 403/429 (rate limit / quota exhausted),
        returns a "Contact Search Limit Reached" message.
      - On network errors, returns an error entry.

    Returns:
        list of dicts with keys: name, role, email, linkedin, source.
    """
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        return [{
            "name": "Hunter API key not set",
            "role": "",
            "email": "",
            "linkedin": "",
            "source": "error",
        }]

    try:
        resp = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": company_domain, "api_key": api_key},
            timeout=10,
        )
    except requests.RequestException:
        return [{
            "name": "Hunter.io request failed",
            "role": "",
            "email": "",
            "linkedin": "",
            "source": "error",
        }]

    if resp.status_code == 200:
        data = resp.json().get("data", {})
        all_emails = data.get("emails", [])

        filtered = []
        for entry in all_emails:
            position = (entry.get("position") or "").lower()
            matched = any(
                p.lower() in position for p in personas
            )
            if matched:
                filtered.append({
                    "name": f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip(),
                    "role": entry.get("position", ""),
                    "email": entry.get("value", ""),
                    "linkedin": entry.get("linkedin_url", "") or "",
                    "source": "hunter",
                })

        if not filtered and all_emails:
            for entry in all_emails[:max(len(personas), 3)]:
                filtered.append({
                    "name": f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip(),
                    "role": entry.get("position", ""),
                    "email": entry.get("value", ""),
                    "linkedin": entry.get("linkedin_url", "") or "",
                    "source": "hunter",
                })

        return filtered

    if resp.status_code in (403, 429):
        return [{
            "name": "Contact Search Limit Reached",
            "role": "",
            "email": "",
            "linkedin": "",
            "source": "limit",
        }]

    return [{
        "name": f"Hunter.io error {resp.status_code}",
        "role": "",
        "email": "",
        "linkedin": "",
        "source": "error",
    }]
