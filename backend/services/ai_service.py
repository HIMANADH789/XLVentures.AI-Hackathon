import os
import sys
from datetime import datetime
from config import settings
from utils.retry import with_retries

# Add agents_code to path to import Venu agents
AGENTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../agents_code'))
if AGENTS_PATH not in sys.path:
    sys.path.insert(0, AGENTS_PATH)

# Temporarily remove backend's app module from sys.modules to avoid namespace collision with agents_code/app
backup_app = sys.modules.pop('app', None)
try:
    from app.agents.trigger_agent import extract_triggers
    from app.agents.icp_agent import qualify_lead
    from app.agents.summary_agent import generate_summary
finally:
    if backup_app is not None:
        sys.modules['app'] = backup_app

# Strict Interface Versioning
AI_PIPELINE_VERSION = settings.ai_pipeline_version

_last_metadata = {}

@with_retries(max_retries=3, initial_delay=1.0)
def get_trigger(company_url: str) -> dict:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        raise ValueError("AI Agent initialization failed: Both OPENAI_API_KEY and GROQ_API_KEY are missing from configuration.")

    state = {
        "company_url": company_url,
        "company_name": "",
        "industry": "",
        "extracted_triggers": []
    }
    
    try:
        result = extract_triggers(state)
        triggers = result.get("extracted_triggers", [])
        first_trigger = triggers[0] if triggers else {}
        
        response = {
            "company": result.get("company_name") or "Unknown Company",
            "trigger": first_trigger.get("trigger_type") or "Unknown Trigger",
            "date": datetime.today().strftime('%Y-%m-%d'),
            "confidence": first_trigger.get("confidence") or 0.8
        }
        _last_metadata[company_url] = {
            "industry": result.get("industry") or "",
            "employee_count": result.get("employee_count") or 0
        }
    except Exception as e:
        print(f"[AI SERVICE ERROR] Trigger Agent failed: {e}")
        raise e
        
    assert "company" in response, "Missing company in AI response"
    assert "trigger" in response, "Missing trigger in AI response"
    assert "confidence" in response, "Missing confidence in AI response"
    
    return response

def get_cached_metadata(company_url: str) -> dict:
    return _last_metadata.get(company_url, {"industry": "AI / SaaS", "employee_count": None})

@with_retries(max_retries=3, initial_delay=1.0)
def get_icp_score(company_data: dict) -> dict:
    state = {
        "icp_criteria": {"industry": "Software", "min_employees": 10, "qualification_threshold": 60},
        "extracted_triggers": [{"trigger_type": company_data.get("trigger", "Unknown")}],
        "company_name": company_data.get("company", ""),
        "industry": company_data.get("industry", ""),
        "employee_count": company_data.get("employee_count", 0) or 0,
        "raw_content": ""
    }
    
    try:
        result = qualify_lead(state)
        response = {
            "qualified": result.get("is_qualified", False),
            "score": result.get("qualification_score", 0),
            "reason": [result.get("summary", "")]
        }
    except Exception as e:
        print(f"[AI SERVICE ERROR] ICP Matcher failed: {e}")
        raise e
        
    assert "qualified" in response, "Missing qualified flag in AI response"
    assert "score" in response, "Missing score in AI response"
    
    return response

@with_retries(max_retries=3, initial_delay=1.0)
def get_summary(company_data: dict) -> dict:
    state = {
        "company_name": company_data.get("company", ""),
        "extracted_triggers": [{"trigger_type": company_data.get("trigger", "Unknown")}],
        "is_qualified": company_data.get("qualified", True),
        "industry": company_data.get("industry", "AI / SaaS"),
        "employee_count": company_data.get("employee_count", 50),
        "qualification_score": company_data.get("score", 0),
        "icp_criteria": {"industry": "Software", "min_employees": 10, "qualification_threshold": 60}
    }
    
    try:
        result = generate_summary(state)
        response = {
            "summary": result.get("summary", "Company seems like a good fit.")
        }
    except Exception as e:
        print(f"[AI SERVICE ERROR] Summary Agent failed: {e}")
        raise e
        
    assert "summary" in response, "Missing summary in AI response"
    
    return response

@with_retries(max_retries=3, initial_delay=1.0)
def analyze_company_pipeline(company_url: str, website_content: str, news: list, contacts: list) -> dict:
    """Analyze company using website content, news, and contact list via dynamic LLM."""
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        raise ValueError("AI Agent initialization failed: Both OPENAI_API_KEY and GROQ_API_KEY are missing from configuration.")

    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0
        )
    else:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0
        )

    print("[PIPELINE] LLM model initialized")
    
    # Format inputs
    news_text = ""
    for idx, art in enumerate(news[:5]):
        news_text += f"- Title: {art.get('title')}\n  Description: {art.get('description')}\n  URL: {art.get('url')}\n\n"
    if not news_text:
        news_text = "No recent news found."

    contacts_text = ""
    for c in contacts:
        contacts_text += f"- Name: {c.get('name')}, Role: {c.get('role')}, Email: {c.get('email')}, Linkedin: {c.get('linkedin')}, Source: {c.get('source')}\n"
    if not contacts_text:
        contacts_text = "No verified contacts found."

    system_prompt = (
        "You are a sales intelligence AI. Analyze the company website content, recent news articles, and contacts provided below.\n\n"
        "## ICP CRITERIA:\n"
        "- Target Industry: Software / AI / SaaS / Tech\n"
        "- Minimum Employees: 10\n"
        "- Qualification Threshold: 60\n\n"
        "## PROMPT RULES (STRICT):\n"
        "1. You must ONLY use the provided website content, news articles, and contact details. Do NOT hallucinate, fabricate, or invent facts. If any information is missing or not provided, state 'Information unavailable'. Remove all speculation.\n"
        "2. If employee count is unknown or not mentioned, return null. Do not guess or fabricate employee counts.\n"
        "3. Compute the ICP score dynamically:\n"
        "   - Trigger Match (Hiring, Funding, Layoffs, Expansion, Acquisition, Partnership, Product Launch, Leadership Change, IPO): 50 pts if a relevant trigger event is present in the website content or news. Otherwise 0 pts.\n"
        "   - Industry Match: 30 pts if the company belongs to Software, AI, SaaS, or Technology. Otherwise 0 pts.\n"
        "   - Employee Match: 20 pts if the company has 10 or more employees. Otherwise 0 pts.\n"
        "   - Calculate the total ICP score as sum of these (0 to 100). Set qualified = true if score >= 60, else false.\n"
        "4. Output clean plain text summary. Do NOT use markdown bold styling (such as **bold** or __bold__). Format it nicely with paragraph breaks.\n"
        "5. The Trigger Event in the summary and trigger_event field must match exactly. Never return trigger_event='None' or trigger_event='other' while the summary says the company is hiring, launching a product, etc. The trigger_event must be one of: Hiring, Funding, Layoffs, Expansion, Acquisition, Partnership, Product Launch, Leadership Change, IPO, or None.\n"
        "6. The ICP Score in the summary and icp_score field must match exactly.\n"
        "7. For the 'contacts' array, map all input contacts and enrich them if possible. You may also extract new contacts from the website content:\n"
        "   - Preserve all input contacts. Do NOT fabricate or invent names, emails, or LinkedIn links.\n"
        "   - Set the 'source' for each contact: 'Hunter' if they were in the input list, 'Firecrawl' if they were found in the website content, and 'AI Inference' if they were found in news articles.\n"
        "   - Never fabricate roles. If the role cannot be determined, set it to 'Role unavailable' or null. Do not use 'Unknown' as a role.\n\n"
        "Return a JSON object with these EXACT keys (return ONLY JSON, no other text or markdown wrapping):\n"
        "{\n"
        "  \"company_name\": \"string (inferred company name)\",\n"
        "  \"industry\": \"string (inferred industry, e.g. AI / SaaS)\",\n"
        "  \"employee_estimate\": \"integer or null (estimated employee count)\",\n"
        "  \"trigger_event\": \"string (exactly: Hiring, Funding, Layoffs, Expansion, Acquisition, Partnership, Product Launch, Leadership Change, IPO, or None)\",\n"
        "  \"trigger_source\": \"string ('news' if the trigger event was identified from the recent news articles, 'website' if it was identified from the website content, or 'unknown' if no trigger event is found)\",\n"
        "  \"trigger_confidence\": \"float (confidence score 0.0 to 1.0)\",\n"
        "  \"icp_score\": \"integer (calculated ICP score 0 to 100)\",\n"
        "  \"qualified\": \"boolean\",\n"
        "  \"summary\": \"string (plain text brief containing Company Name, Trigger Event, ICP Score, ICP Fit Reason, and Recommended Next Best Action. Avoid markdown bold ** syntax)\",\n"
        "  \"recommended_action\": \"string (recommended next action)\",\n"
        "  \"contacts\": [\n"
        "    {\n"
        "      \"name\": \"string\",\n"
        "      \"role\": \"string or null\",\n"
        "      \"email\": \"string or null\",\n"
        "      \"linkedin\": \"string or null\",\n"
        "      \"source\": \"string (Hunter, Firecrawl, or AI Inference)\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    context = f"""
Company URL: {company_url}

Website Content:
{website_content[:6000]}

Recent News:
{news_text}

Contacts:
{contacts_text}
"""

    from langchain_core.messages import SystemMessage, HumanMessage
    from app.utils.formatters import extract_json

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    try:
        result = extract_json(response.content)
    except Exception as e:
        print(f"[AI SERVICE ERROR] Failed to parse JSON from LLM: {response.content}")
        raise e

    # Ensure keys are present or fallback
    assert "company_name" in result
    assert "trigger_event" in result
    assert "icp_score" in result
    assert "summary" in result
    assert "contacts" in result
    
    return result
