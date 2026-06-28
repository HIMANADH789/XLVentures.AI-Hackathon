import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import AgentState
from app.tools.registry import list_available_tools
from app.utils.formatters import extract_json


def plan_next_steps(state: AgentState) -> dict:
    """Generate an execution plan using ChatGroq based on available tools and triggers.

    Only runs when approval_status == 'approved'. Queries the tool registry
    for available tools, then asks Groq to select the best sequence based on
    detected trigger types. Falls back to sensible defaults if LLM output is empty.

    Returns:
        dict with 'execution_plan' (list of {tool, reason}) and 'current_step_index' (0).
    """
    if state.get("approval_status") != "approved":
        return {"execution_plan": [], "current_step_index": 0}

    available = list_available_tools()
    triggers = state.get("extracted_triggers", [])
    trigger_types = [t.get("trigger_type", "").lower() for t in triggers]
    is_qualified = state.get("is_qualified", False)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    tools_json = json.dumps(available, indent=2)
    triggers_json = json.dumps(trigger_types, indent=2)

    system_prompt = (
        "You are an expert Orchestrator. Given a company profile, detected triggers, "
        "and a goal ('Enrich Prospect'), choose the best sequence of tools from the "
        "available list to achieve the goal.\n\n"
        "Rules:\n"
        "- If the lead is qualified, always include 'find_contacts'.\n"
        "- Only pick tools relevant to the detected trigger types.\n"
        "- 'analyze_tech_stack' if 'tech_stack', 'product', or 'growth' triggers present.\n"
        "- 'check_sentiment' always (provides useful context).\n"
        "- 'track_hiring_velocity' if 'hiring' triggers present.\n"
        "- Return a JSON object with a single key 'steps' that is an array of objects.\n"
        "- Each step object has keys: 'tool' (string matching a tool name) and 'reason' (string)."
    )

    context = (
        f"Available tools:\n{tools_json}\n\n"
        f"Detected trigger types:\n{triggers_json}\n\n"
        f"Is qualified: {is_qualified}\n"
        f"Goal: Enrich Prospect"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    try:
        plan = extract_json(response.content)
        steps = plan.get("steps", [])
    except Exception:
        steps = []

    if not steps:
        steps = []
        if is_qualified:
            steps.append({"tool": "find_contacts", "reason": "Lead is qualified, locate contacts"})
        if any(t in trigger_types for t in {"tech_stack", "product", "growth"}):
            steps.append({"tool": "analyze_tech_stack", "reason": "Tech/growth triggers detected"})
        steps.append({"tool": "check_sentiment", "reason": "Contextual sentiment analysis"})
        if "hiring" in trigger_types:
            steps.append({"tool": "track_hiring_velocity", "reason": "Hiring signals found"})

    return {"execution_plan": steps, "current_step_index": 0}
