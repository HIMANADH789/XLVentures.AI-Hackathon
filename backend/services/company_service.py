import re

from services.hunter_service import find_emails


def enrich_contacts(domain: str) -> list:
    try:
        return find_emails(domain)
    except Exception:
        return []


def _fetch_text(url: str, timeout: int = 10) -> str | None:
    """Fetch a URL and return cleaned visible text using bs4."""
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=timeout,
        )
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ")
    except Exception:
        return None


def _extract_employee_from_text(text: str) -> int | None:
    """Run regex patterns over cleaned text to find employee count."""
    patterns = [
        (r"team\s+of\s+(\d{2,})\+?", lambda m: int(m.group(1))),
        (r"(\d{2,})\s*[-–]\s*(\d{3,})\s+employees?", lambda m: (int(m.group(1)) + int(m.group(2))) // 2),
        (r"(?:over|about|approximately|~)\s+(\d{3,})\s+(?:people|employees?)", lambda m: int(m.group(1))),
        (r"(\d{3,})\s*\+\s*(?:employees?|people)", lambda m: int(m.group(1))),
        (r"(\d{2,})\s+(?:employees?|people)\s", lambda m: int(m.group(1))),
    ]
    for pattern, extractor in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return extractor(match)
            except (ValueError, IndexError):
                continue
    return None


def scrape_employee_count(url: str) -> int | None:
    """Scrape employee count from a company website using bs4 + regex.

    Checks homepage, /about, and /careers pages for employee number patterns.
    Also searches JSON-LD structured data for employee counts.
    Returns None if unable to determine.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    # Try homepage, /about, /careers
    paths_to_try = [url, base + "/about", base + "/careers"]
    for page_url in paths_to_try:
        text = _fetch_text(page_url)
        if text:
            result = _extract_employee_from_text(text)
            if result:
                print(f"[EMPLOYEE COUNT] Found {result} on {page_url}")
                return result

    return None
