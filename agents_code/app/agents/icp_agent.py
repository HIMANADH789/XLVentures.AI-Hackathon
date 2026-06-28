import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import AgentState
from app.utils.formatters import extract_json


MAX_TRIGGER_PTS = 50
MAX_INDUSTRY_PTS = 30
MAX_EMPLOYEE_PTS = 20


def _infer_industry(content: str, company_name: str) -> str | None:
    """Use ChatGroq to infer the company's industry from scraped content."""
    if not content:
        return None
    try:
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        else:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY"),
            )
        system_prompt = (
            "From the website content below, infer the company's primary industry. "
            "Return a JSON object with a single key 'industry' containing a short string "
            "like 'AI / SaaS', 'Supply Chain', 'Logistics', 'Fintech', 'Healthcare', etc."
        )
        context = f"Company: {company_name}\n\nContent:\n{content[:3000]}"
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context),
        ]
        response = llm.invoke(messages)
        result = extract_json(response.content)
        return result.get("industry")
    except Exception:
        return None


def qualify_lead(state: AgentState) -> dict:
    """Score a lead 0-100 against ICP criteria and determine qualification.

    Scoring breakdown:
      - Trigger (Funding/Hiring): 0 or 50 pts
      - Industry match: 0 or 30 pts
      - Employee count match: 0 or 20 pts
    Qualified if score >= 60.

    If industry was not provided by the user, attempts to infer it from the
    raw scraped content via an LLM call.

    Returns:
        dict with 'qualification_score', 'is_qualified', 'summary',
        'trigger_score', 'industry_score', 'employee_score',
        and 'industry' (inferred if missing).
    """
    icp = state["icp_criteria"]
    triggers = state["extracted_triggers"]
    raw_content = state.get("raw_content", "")

    # --- Trigger score: binary check for Funding or Hiring ---
    trigger_triggered = any(
        t.get("trigger_type", "").lower() in {"funding", "hiring"}
        for t in triggers
    )
    trigger_score = MAX_TRIGGER_PTS if trigger_triggered else 0

    # --- Industry: infer from content if not provided ---
    industry = state.get("industry", "").strip()
    if not industry and raw_content:
        guessed = _infer_industry(raw_content, state.get("company_name", ""))
        if guessed:
            industry = guessed.strip()

    target_industry = icp.get("industry", "").strip().lower()
    industry_score = 0
    if target_industry and industry:
        industry_lower = industry.lower()
        is_software_related = "software" in target_industry or "saas" in target_industry or "tech" in target_industry
        tech_keywords = {"software", "saas", "ai", "artificial intelligence", "technology", "tech", "cloud", "internet", "machine learning", "deep learning"}
        
        for kw in target_industry.split(","):
            kw = kw.strip().lower()
            if kw and (kw in industry_lower or (is_software_related and any(tk in industry_lower for tk in tech_keywords))):
                industry_score = MAX_INDUSTRY_PTS
                break

    # --- Employee count ---
    emp_count = state.get("employee_count", 0)
    min_emp = icp.get("min_employees", 0)
    employee_score = MAX_EMPLOYEE_PTS if emp_count >= min_emp else 0

    score = trigger_score + industry_score + employee_score
    threshold = icp.get("qualification_threshold", 60)
    is_qualified = score >= threshold

    summary_parts = []
    if trigger_triggered:
        summary_parts.append(f"Funding/Hiring trigger: {trigger_score}/{MAX_TRIGGER_PTS}")
    if industry_score > 0:
        summary_parts.append(f"Industry match: {industry_score}/{MAX_INDUSTRY_PTS}")
    if employee_score > 0:
        summary_parts.append(f"Employee count: {employee_score}/{MAX_EMPLOYEE_PTS}")
    summary_parts.append(f"Score: {score}/100 (threshold: {threshold})")

    return {
        "qualification_score": score,
        "is_qualified": is_qualified,
        "summary": ", ".join(summary_parts),
        "trigger_score": trigger_score,
        "industry_score": industry_score,
        "employee_score": employee_score,
        "industry": industry,
    }
