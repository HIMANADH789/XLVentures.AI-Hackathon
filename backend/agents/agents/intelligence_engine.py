import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from ..state import AgentState


def aggregate_intelligence(state: AgentState) -> dict:
    """Synthesise prospect intelligence data into a Strategic Insight paragraph.

    Runs after all execution plan steps are complete. Uses ChatGroq to
    produce a 2-3 sentence actionable summary from the collected
    tech_stack, sentiment, hiring_velocity, and company profile data.

    Returns:
        dict with prospect_intelligence.strategic_insight (markdown string).
    """
    pi = state.get("prospect_intelligence", {})
    if not pi:
        return {"prospect_intelligence": {"strategic_insight": ""}}

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    system_prompt = (
        "Based on the prospect intelligence data and company profile below, "
        "write a single 'Strategic Insight' paragraph (2-3 sentences) that "
        "synthesizes everything into actionable business context. "
        "Focus on what makes this prospect worth pursuing."
    )

    context = (
        f"Company: {state.get('company_name', 'N/A')}\n"
        f"Industry: {state.get('industry', 'N/A')}\n"
        f"Qualification Score: {state.get('qualification_score', 0)}/100\n"
        f"Prospect Intelligence:\n{json.dumps(pi, indent=2)}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    return {"prospect_intelligence": {"strategic_insight": response.content}}
