from langgraph.graph import END, StateGraph

from app.agents.action_agent import recommend_action
from app.agents.icp_agent import qualify_lead as qualify_lead_fn
from app.agents.intelligence_engine import aggregate_intelligence
from app.agents.planner_agent import plan_next_steps
from app.agents.specialized_agents import (
    analyze_tech_stack,
    check_sentiment,
    track_hiring_velocity,
)
from app.agents.summary_agent import generate_summary
from app.agents.trigger_agent import extract_triggers
from app.state import AgentState
from urllib.parse import urlparse

from app.tools.contact_finder import find_contacts as find_contacts_tool
from app.tools.memory import get_memory_store


def check_memory(state: AgentState) -> dict:
    """Look up a cached company profile. Skip if force_refresh or previously rejected.

    Returns:
        Full cached data with from_memory=True, or from_memory=False to trigger re-analysis.
    """
    if state.get("force_refresh"):
        return {"from_memory": False}

    store = get_memory_store()
    profile = store.get_company_profile(state["company_url"])
    if profile is None:
        return {"from_memory": False}

    if profile.get("status") == "rejected":
        return {"from_memory": False}

    result = {
        "company_name": profile.get("company_name", ""),
        "industry": profile.get("industry", ""),
        "employee_count": profile.get("employee_count", 0),
        "raw_content": profile.get("raw_content", ""),
        "extracted_triggers": profile.get("extracted_triggers", []),
        "qualification_score": profile.get("qualification_score", 0),
        "is_qualified": profile.get("is_qualified", False),
        "summary": profile.get("summary", ""),
        "contacts": profile.get("contacts", []),
        "next_actions": profile.get("next_actions", []),
        "recommended_action": profile.get("recommended_action", {}),
        "prospect_intelligence": profile.get("prospect_intelligence", {}),
        "from_memory": True,
    }

    re_ql = qualify_lead_fn({
        "icp_criteria": state.get("icp_criteria", {}),
        "extracted_triggers": profile.get("extracted_triggers", []),
        "raw_content": profile.get("raw_content", ""),
        "industry": profile.get("industry", ""),
        "employee_count": profile.get("employee_count", 0),
        "company_name": profile.get("company_name", ""),
    })
    result.update(re_ql)
    result["trigger_score"] = re_ql.get("trigger_score", 0)
    result["industry_score"] = re_ql.get("industry_score", 0)
    result["employee_score"] = re_ql.get("employee_score", 0)

    return result


def human_review(state: AgentState) -> dict:
    """Human-in-the-loop pause. Actual approval logic is in route_after_review."""
    return {}


def save_to_memory(state: AgentState) -> dict:
    store = get_memory_store()
    store.save_company_profile(state["company_url"], {
        "company_name": state.get("company_name", ""),
        "industry": state.get("industry", ""),
        "employee_count": state.get("employee_count", 0),
        "raw_content": state.get("raw_content", ""),
        "extracted_triggers": state.get("extracted_triggers", []),
        "qualification_score": state.get("qualification_score", 0),
        "is_qualified": state.get("is_qualified", False),
        "summary": state.get("summary", ""),
        "contacts": state.get("contacts", []),
        "next_actions": state.get("next_actions", []),
        "recommended_action": state.get("recommended_action", {}),
        "approval_status": state.get("approval_status", "pending"),
        "execution_plan": state.get("execution_plan", []),
        "prospect_intelligence": state.get("prospect_intelligence", {}),
        "trigger_score": state.get("trigger_score", 0),
        "industry_score": state.get("industry_score", 0),
        "employee_score": state.get("employee_score", 0),
        "user_id": state.get("user_id", ""),
    })
    store.save_interaction(state["company_url"], "analysis_complete")
    return {}


def route_from_memory(state: AgentState) -> str:
    """Route to human_review if cached data was loaded, else scrape."""

    if state.get("from_memory"):
        return "human_review"
    return "extract_triggers"


def route_after_review(state: AgentState) -> str:
    """Branch based on human approval: approved → plan, rejected → save, pending → wait."""

    status = state.get("approval_status", "pending")
    if status == "approved":
        return "plan_next_steps"
    elif status == "rejected":
        return "save_to_memory"
    return END


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.netloc or parsed.path.split("/")[0]).replace("www.", "")


TOOL_HANDLERS = {
    "find_contacts": lambda s: {
        "contacts": find_contacts_tool(
            _domain_from_url(s["company_url"]),
            s.get("personas", []),
        )
    },
    "analyze_tech_stack": analyze_tech_stack,
    "check_sentiment": check_sentiment,
    "track_hiring_velocity": track_hiring_velocity,
}


def execute_step(state: AgentState) -> dict:
    """Execute the current step from the execution plan and advance the index.

    Dispatches to the appropriate handler via TOOL_HANDLERS mapping.
    """
    plan = state.get("execution_plan", [])
    idx = state.get("current_step_index", 0)
    if idx >= len(plan):
        return {"current_step_index": idx}

    step = plan[idx]
    tool_name = step["tool"]
    handler = TOOL_HANDLERS.get(tool_name)

    result = handler(state) if handler else {}
    result["current_step_index"] = idx + 1
    return result


def route_after_plan(state: AgentState) -> str:
    """Route to execute_step if plan has items, otherwise aggregate."""

    plan = state.get("execution_plan", [])
    idx = state.get("current_step_index", 0)
    if idx < len(plan):
        return "execute_step"
    return "aggregate_intelligence"


def route_after_execute(state: AgentState) -> str:
    """Loop back to execute_step while steps remain, then aggregate."""

    plan = state.get("execution_plan", [])
    idx = state.get("current_step_index", 0)
    if idx < len(plan):
        return "execute_step"
    return "aggregate_intelligence"


builder = StateGraph(AgentState)
builder.add_node("check_memory", check_memory)
builder.add_node("extract_triggers", extract_triggers)
builder.add_node("qualify_lead", qualify_lead_fn)
builder.add_node("human_review", human_review)
builder.add_node("plan_next_steps", plan_next_steps)
builder.add_node("execute_step", execute_step)
builder.add_node("aggregate_intelligence", aggregate_intelligence)
builder.add_node("generate_summary", generate_summary)
builder.add_node("recommend_action", recommend_action)
builder.add_node("save_to_memory", save_to_memory)

builder.set_entry_point("check_memory")
builder.add_conditional_edges(
    "check_memory",
    route_from_memory,
    {"extract_triggers": "extract_triggers", "human_review": "human_review"},
)
builder.add_edge("extract_triggers", "qualify_lead")
builder.add_edge("qualify_lead", "human_review")
builder.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "plan_next_steps": "plan_next_steps",
        "save_to_memory": "save_to_memory",
        END: END,
    },
)
builder.add_conditional_edges(
    "plan_next_steps",
    route_after_plan,
    {"execute_step": "execute_step", "aggregate_intelligence": "aggregate_intelligence"},
)
builder.add_conditional_edges(
    "execute_step",
    route_after_execute,
    {"execute_step": "execute_step", "aggregate_intelligence": "aggregate_intelligence"},
)
builder.add_edge("aggregate_intelligence", "generate_summary")
builder.add_edge("generate_summary", "recommend_action")
builder.add_edge("recommend_action", "save_to_memory")
builder.add_edge("save_to_memory", END)

app = builder.compile()
