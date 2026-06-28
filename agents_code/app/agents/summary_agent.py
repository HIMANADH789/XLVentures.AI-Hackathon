import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import AgentState


def generate_summary(state: AgentState) -> dict:
    """Generate an Executive Brief using ChatGroq from full analysis state.

    Synthesises company info, triggers, ICP fit, contacts, and recommended
    action into a readable markdown brief.

    Returns:
        dict with 'summary' (markdown string).
    """
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
        "You are an AI B2B Prospecting assistant. Generate a highly accurate, professional executive brief "
        "strictly grounded on the provided structured data. Do NOT invent or hallucinate any details "
        "(such as funding amounts, employee counts, or contact names) if they are not explicitly present. "
        "If any information is missing or not provided, state 'Information unavailable'.\n\n"
        "CRITICAL FORMATTING INSTRUCTION: Do NOT use markdown bold syntax (such as **bold** or __bold__) in your response. "
        "Instead, write clean formatted plain text. For headers, use CAPITAL letters or simple spacing.\n\n"
        "Your summary must strictly match and mention the following fields:\n"
        "- Company Name\n"
        "- Trigger Event\n"
        "- Qualification Score (you MUST state the actual numeric Qualification Score provided in the data)\n"
        "- ICP Fit Reason (explain how the company matches the target industry and employee threshold)\n"
        "- Recommended Next Best Action"
    )

    context = f"""
Company Name: {state.get('company_name', 'N/A')}
Industry: {state.get('industry', 'N/A')}
Employee Count: {state.get('employee_count', 'N/A')}
Trigger: {state.get('extracted_triggers', [{}])[0].get('trigger_type', 'Unknown')}
Qualification Score: {state.get('qualification_score', 0)}
ICP Target Industry: {state.get('icp_criteria', {}).get('industry', 'Software')}
ICP Min Employees: {state.get('icp_criteria', {}).get('min_employees', 10)}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    return {"summary": response.content}
