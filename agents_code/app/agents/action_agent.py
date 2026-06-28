import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import AgentState
from app.utils.formatters import extract_json


def recommend_action(state: AgentState) -> dict:
    """Recommend the single best next outreach action using ChatGroq.

    Uses company triggers, target personas, and qualification score to
    generate a JSON response with action_type, reasoning, and draft_message.

    Returns:
        dict with 'recommended_action' ({action_type, reasoning, draft_message}).
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    system_prompt = (
        "You are a sales development assistant. Based on the company triggers and "
        "target personas, recommend the single best next action for outreach.\n\n"
        "Return a JSON object with these keys:\n"
        '- action_type: one of "Email", "LinkedIn Connect", "Call"\n'
        "- reasoning: 1-2 sentence explanation of why this action fits the trigger/persona\n"
        "- draft_message: a short (2-3 sentence) personalized opening line for the outreach"
    )

    context = (
        f"Company: {state.get('company_name', 'N/A')}\n"
        f"Industry: {state.get('industry', 'N/A')}\n"
        f"Key Triggers: {json.dumps(state.get('extracted_triggers', []), indent=2)}\n"
        f"Target Personas: {state.get('personas', [])}\n"
        f"Qualification Score: {state.get('qualification_score', 0)}/100"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)

    try:
        action = extract_json(response.content)
    except (json.JSONDecodeError, TypeError):
        action = {
            "action_type": "Email",
            "reasoning": "Unable to parse LLM response, defaulting to email outreach.",
            "draft_message": response.content[:500],
        }

    return {"recommended_action": action}
