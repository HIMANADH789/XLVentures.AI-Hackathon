import os
import re
import socket
from urllib.parse import urlparse

from firecrawl import V1FirecrawlApp

MOCK_PAGES = {
    "/": (
        "Company ABC is a Series B startup in the AI space. They recently raised $10M "
        "and are hiring 5 engineers for their expansion into the European market."
    ),
    "/careers": (
        "Join our team! We are hiring software engineers, data scientists, and sales "
        "representatives. Remote-friendly culture with competitive compensation."
    ),
    "/about": (
        "Founded in 2021, Company ABC is on a mission to revolutionize supply chain "
        "management using AI. We have offices in San Francisco and London."
    ),
    "/blog": (
        "Announcing our Series B funding round of $10M led by Accel. Read about our "
        "new product launch: AI-powered inventory forecasting."
    ),
    "/press": (
        "Company ABC named to Forbes AI 50 list. Expanding to APAC markets in 2026. "
        "New partnership with DHL for integrated logistics."
    ),
}

MOCK_METADATA = {
    "company_name": "Company ABC",
    "employee_count": 50,
    "industry": "AI / Supply Chain",
}

COMMON_PATHS = ["/careers", "/about", "/blog", "/press"]

MAX_TOTAL = 8000
MAX_PAGES = 5

SKIP_URL_PATTERNS = [
    "/product/", "/pn/", "/products/", "/shop/", "/buy/",
    "/item/", "/category/", "/deal/", "/cart", "/checkout",
    "/wishlist", "/account/orders", "/search?",
]


def _scrape_page(app: V1FirecrawlApp | None, url: str) -> str:
    """Scrape a single page via Firecrawl, falling back to HTTP request, then mock data."""
    if app is not None:
        try:
            result = app.scrape_url(url, formats=["markdown"])
            if hasattr(result, "markdown") and result.markdown:
                return result.markdown
            if hasattr(result, "data") and result.data:
                return (result.data or {}).get("markdown", "")
            return str(result)
        except Exception as e:
            print(f"[FIRECRAWL ERROR] Failed to scrape {url}: {e}. Falling back to HTTP request.")

    # HTTP Fallback
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=8)
        if resp.status_code == 200:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n")
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
                if cleaned_text:
                    return cleaned_text
            except Exception:
                return resp.text[:4000]
    except Exception as e:
        print(f"[HTTP SCRAPER ERROR] Failed to fetch {url}: {e}")

    # Final Mock Fallback
    path = urlparse(url).path or "/"
    return MOCK_PAGES.get(path, MOCK_PAGES["/"])


def _discover_pages(app: V1FirecrawlApp | None, base_url: str) -> list[str]:
    """Discover relevant pages using Firecrawl map_url or fall back to common paths."""
    try:
        result = app.map_url(base_url, limit=10)
        if result.success and result.links:
            links = result.links[:10]
            # Filter out e-commerce product/category URLs
            filtered = [
                lnk for lnk in links
                if not any(p in lnk.lower() for p in SKIP_URL_PATTERNS)
            ]
            return filtered[:MAX_PAGES] if filtered else [base_url + p for p in COMMON_PATHS]
    except Exception:
        pass
    return [base_url + p for p in COMMON_PATHS]


def discover_and_scrape(url: str) -> str:
    """Discover up to 5 pages for a company URL and scrape their markdown content.

    Distributes an 8000-character budget evenly across all pages.
    Returns concatenated content with ``--- PAGE: URL ---`` markers.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = V1FirecrawlApp(api_key=api_key) if api_key else None

    if app is None:
        pages = [url + p for p in COMMON_PATHS]
    else:
        pages = _discover_pages(app, url)

    pages = pages[:MAX_PAGES]
    budget_per_page = MAX_TOTAL // max(len(pages), 1)

    parts = []
    for page_url in pages:
        text = _scrape_page(app, page_url)
        trimmed = text[:budget_per_page]
        parts.append(f"\n\n--- PAGE: {page_url} ---\n\n{trimmed}")

    return "".join(parts)[:MAX_TOTAL]


def extract_company_data(url: str) -> dict:
    """Extract structured company metadata via Firecrawl extract + regex fallback.

    Phase 1 — tries Firecrawl's structured ``extract`` endpoint with a JSON
    schema (company_name, employee_count, industry).  A 10-second socket
    timeout prevents hanging when the endpoint is slow.
    Phase 2 — falls back to regex heuristics on raw scraped content.
    The LLM in ``trigger_agent`` provides a third pass.

    Returns:
        dict with keys: raw_content, company_name, employee_count, industry.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")

    result = {
        "raw_content": "",
        "company_name": "",
        "employee_count": 0,
        "industry": "",
    }

    # Phase 1 — Firecrawl extract (with short timeout)
    if api_key:
        try:
            from firecrawl import FirecrawlApp

            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)
            try:
                app_v4 = FirecrawlApp(api_key=api_key)
                schema = {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "employee_count": {"type": "number"},
                        "industry": {"type": "string"},
                    },
                    "required": ["company_name"],
                }
                extract_result = app_v4.extract(
                    urls=[url],
                    prompt="Extract the company name, total employee count, and primary industry from the website.",
                    schema=schema,
                )
                if getattr(extract_result, "success", False) and getattr(extract_result, "data", None):
                    data = extract_result.data
                    result["company_name"] = data.get("company_name", "")
                    result["employee_count"] = data.get("employee_count", 0) or 0
                    result["industry"] = data.get("industry", "")
            finally:
                socket.setdefaulttimeout(old_timeout)
        except Exception:
            pass

    # Phase 2 — scrape raw content and apply regex heuristics
    raw = discover_and_scrape(url)
    result["raw_content"] = raw

    if not result["company_name"]:
        name = _infer_company_name(raw)
        if name:
            result["company_name"] = name

    if not result["employee_count"]:
        emp = _infer_employee_count(raw)
        if emp:
            result["employee_count"] = emp

    if not result["industry"]:
        ind = _infer_industry(raw)
        if ind:
            result["industry"] = ind

    return result


def _infer_company_name(text: str) -> str | None:
    """Guess company name from the first few lines of scraped content."""
    lines = text.strip().split("\n")
    for line in lines[:20]:
        line = line.strip().strip("#").strip("*").strip()
        if line and len(line) < 80 and not line.startswith("---"):
            return line.strip()
    return None


def _infer_employee_count(text: str) -> int | None:
    """Extract employee count from text using regex patterns."""
    patterns = [
        (r"team\s+of\s+(\d+)\+?", lambda m: int(m.group(1))),
        (r"(\d+)\s*[-–]\s*(\d+)\s+employees?", lambda m: (int(m.group(1)) + int(m.group(2))) // 2),
        (r"(?:over|about|approximately|~)\s+(\d+)\s+(?:people|employees?)", lambda m: int(m.group(1))),
        (r"(\d+)\s*\+\s*(?:employees?|people)", lambda m: int(m.group(1))),
        (r"(\d+)\s+employees?", lambda m: int(m.group(1))),
    ]
    for pattern, extractor in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return extractor(match)
            except (ValueError, IndexError):
                continue
    return None


def _infer_industry(text: str) -> str | None:
    """Guess industry by scanning for known keywords in the scraped text."""
    keywords = {
        "Quick Commerce": ["quick commerce", "q-commerce", "30 minute delivery", "10 minute delivery", "instant delivery", "qcomm"],
        "Food Delivery": ["food delivery", "restaurant delivery", "groceries", "grocery delivery", "meal delivery"],
        "E-commerce": ["e-commerce", "ecommerce", "online shopping", "marketplace"],
        "AI / SaaS": ["artificial intelligence", "machine learning", "saas", "ai "],
        "Supply Chain": ["supply chain", "logistics", "warehouse", "inventory"],
        "Logistics": ["logistics", "freight", "shipping", "delivery"],
        "Fintech": ["fintech", "payments", "banking", "financial"],
        "Healthcare": ["healthcare", "health", "medical", "biotech"],
    }
    lower = text.lower()
    for industry, kws in keywords.items():
        if any(kw in lower for kw in kws):
            return industry
    return None
