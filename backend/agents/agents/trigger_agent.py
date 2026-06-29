import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from ..state import AgentState
from ..tools.scraper import discover_and_scrape, extract_company_data
from ..utils.formatters import extract_json


MAX_LLM_CHARS = 8000


def extract_triggers(state: AgentState) -> dict:
    """Scrape company website and extract business triggers + metadata using ChatGroq.

    Two-phase extraction:
      1. Structured metadata (company_name, employee_count, industry) is obtained
         via Firecrawl's ``extract`` endpoint (with regex/LLM fallback).
      2. The scraped raw content is sent to Groq to extract explicit and implicit
         business triggers (Funding, Hiring, Tech Stack, Growth, etc.).

    If ``employee_count`` is still 0 after scraping, attempts to infer it from
    the raw content via regex patterns (e.g. "Team of 50+", "100-200 employees").

    Returns:
        dict with keys: raw_content, extracted_triggers, company_name, industry,
        employee_count.
    """
    url = state["company_url"]

    metadata = extract_company_data(url)
    raw_content = metadata["raw_content"]
    company_name = metadata["company_name"] or state.get("company_name", "")
    industry = metadata["industry"] or state.get("industry", "")
    employee_count = metadata["employee_count"] or 0

    if not employee_count:
        employee_count = _infer_employee_count(raw_content)

    content_for_llm = raw_content[:MAX_LLM_CHARS]

    # Append news headlines if available
    news_headlines = state.get("news_headlines", "")
    if news_headlines:
        content_for_llm += f"\n\n--- RECENT NEWS HEADLINES ---\n{news_headlines}"

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    system_prompt = (
        "Extract business triggers and metadata from the following company pages and recent news headlines.\n\n"
        "## CRITICAL — URL FILTERING RULES:\n"
        "- IGNORE individual product/category/shopping pages (URLs containing /product/, /pn/, /shop/, /buy/, /item/, /category/, /deal/). These are NOT business signals.\n"
        "- FOCUS on business-relevant pages: /about, /careers, /blog, /press, /news, /investors, /company, /team.\n"
        "- IF news headlines mention partnerships, funding, expansion, regulatory actions, or market moves related to this company, treat those as valid triggers.\n"
        "- If NO business-relevant content is available, return empty triggers list rather than inventing signals from product pages.\n\n"
        "## Triggers to detect (both explicit and implicit):\n"
        '- "Funding" — investment rounds, fundraising announcements, "raised $X", IPO filings, DRHP\n'
        '- "Hiring" — job listings, "Join our team", "We are growing our team", recruiting drives, "hiring across"\n'
        '- "Tech Stack" — specific technologies mentioned (AWS, Azure, Python, React, etc.)\n'
        '- "Growth" — expansion to new regions, new offices, "expanding to new markets", scaling operations\n'
        '- "Product Launch" — new product launches, beta releases, new features, "launched new"\n'
        '- "Partnership" — strategic alliances, integrations with partners, "partnered with", coalitions\n'
        '- "Acquisition" — companies acquired, "acquired"\n\n'
        "## Implicit trigger examples:\n"
        '- Phrases like "growing our team", "expanding to new markets", "launched new AI features",\n'
        '  "scaling our operations", "opening new offices", "entering new regions"\n'
        "- Even if not explicitly called 'funding', mentions of Series A/B/C or investment indicate Funding.\n\n"
        "## Industry classification (choose the best match):\n"
        '- "AI / SaaS" — software, artificial intelligence, machine learning, cloud services\n'
        '- "E-commerce" — online shopping, marketplace, retail platform\n'
        '- "Food Delivery" — restaurant delivery, grocery delivery, meal kits\n'
        '- "Quick Commerce" — instant delivery, 10-30 minute delivery, q-commerce\n'
        '- "Fintech" — payments, banking, financial services, insurance\n'
        '- "Logistics" — shipping, freight, supply chain, delivery network\n'
        '- "Healthcare" — medical, health tech, biotech, hospital\n'
        '- "Supply Chain" — warehouse, inventory, procurement, manufacturing\n\n'
        "Return a JSON object with these keys:\n"
        '- "triggers": a list of objects with keys: "trigger_type", "description", "confidence" (0-1), "source_url"\n'
        '  The "source_url" should be the URL of the page or the news article where the trigger was found.\n'
        '- "company_name": string (inferred company name, empty string if unsure)\n'
        '- "industry": string (inferred industry from the list above, empty string if unsure)\n'
        '- "employee_count": integer (inferred number of employees if mentioned or estimated, or null if completely unknown)'
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=content_for_llm),
    ]

    response = llm.invoke(messages)

    triggers = []
    try:
        parsed = extract_json(response.content)
        triggers = parsed.get("triggers", [])
        llm_name = parsed.get("company_name", "")
        llm_industry = parsed.get("industry", "")
        llm_employee_count = parsed.get("employee_count", None)
        company_name = llm_name or company_name
        industry = llm_industry or industry
        if llm_employee_count is not None:
            try:
                employee_count = int(llm_employee_count)
            except (ValueError, TypeError):
                pass
    except (json.JSONDecodeError, TypeError):
        triggers = []

    return {
        "raw_content": raw_content,
        "extracted_triggers": triggers,
        "company_name": company_name,
        "industry": industry,
        "employee_count": employee_count,
    }


def _infer_employee_count(text: str) -> int:
    """Infer employee count from text patterns like 'Team of 50+', '100-200 employees'."""
    import re

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
    return 0
