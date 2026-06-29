import os

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from ..state import AgentState
from ..utils.formatters import extract_json


def _infer_industry(content: str, company_name: str) -> str | None:
    """Use ChatGroq to infer the company's industry from scraped content."""
    if not content:
        return None
    try:
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
    """Score a lead 0-100 against ICP criteria using the LLM.

    The LLM evaluates the company holistically — industry fit, trigger events,
    employee count, target personas, and any other contextual signals —
    then returns a numerical score and qualification decision.

    Returns:
        dict with 'qualification_score', 'is_qualified', 'summary',
        'trigger_score', 'industry_score', 'employee_score',
        and 'industry' (inferred if missing).
    """
    icp = state["icp_criteria"]
    triggers = state["extracted_triggers"]
    raw_content = state.get("raw_content", "")
    company_name = state.get("company_name", "")

    # --- Infer industry from content if not provided ---
    industry = state.get("industry", "").strip()
    if not industry and raw_content:
        guessed = _infer_industry(raw_content, company_name)
        if guessed:
            industry = guessed.strip()

    # --- Build a concise prompt for the LLM ---
    trigger_lines = "\n".join(
        f"- {t.get('trigger_type', 'Unknown')}: {t.get('description', '')}"
        for t in triggers
    ) or "None detected"

    prompt = f"""You are a B2B prospecting qualification agent. Evaluate the lead below against the ICP criteria.

## ICP Criteria
- Target Industry: {icp.get('industry', 'Any')}
- Min Employees: {icp.get('min_employees', 0)}
- Max Employees: {icp.get('max_employees', 0) or 'No limit'}
- Qualification Threshold: {icp.get('qualification_threshold', 60)}/100
- Target Personas: {', '.join(icp.get('target_personas', [])) or 'Any'}

## Lead
- Company: {company_name}
- Industry: {industry or 'Unknown'}
- Employee Count: {state.get('employee_count', 0)}
- Trigger Events: {trigger_lines}
- Website Content (first 1500 chars): {(raw_content or '')[:1500]}

## Instructions
Score each dimension separately:
1. **Industry fit** (0-30 pts) — How closely does the company's industry match the target?
2. **Trigger relevance** (0-50 pts) — Are there strong buying signals (funding, hiring, expansion, partnership, tech_stack, product_launch)?
3. **Company size** (0-20 pts) — Does employee count fit within the range?

Return ONLY valid JSON with these keys:
- "trigger_score": int (0-50)
- "industry_score": int (0-30)
- "employee_score": int (0-20)
- "is_qualified": bool
- "summary": str (1-2 sentence explanation)"""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = extract_json(response.content)
    except Exception:
        result = {}

    trigger_score = result.get("trigger_score", 0)
    industry_score = result.get("industry_score", 0)
    employee_score = result.get("employee_score", 0)
    total = trigger_score + industry_score + employee_score
    is_qualified = result.get("is_qualified", total >= icp.get("qualification_threshold", 60))

    return {
        "qualification_score": total,
        "is_qualified": is_qualified,
        "summary": result.get("summary", "Qualification evaluation failed"),
        "trigger_score": trigger_score,
        "industry_score": industry_score,
        "employee_score": employee_score,
        "industry": industry,
    }
