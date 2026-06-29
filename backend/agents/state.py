from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


def merge_prospect_intelligence(current: dict, update: dict) -> dict:
    """Reducer for prospect_intelligence: shallow-merges incoming keys.

    Each specialized agent returns a single key (tech_stack, sentiment, etc.)
    under prospect_intelligence. This reducer accumulates them into one dict
    without overwriting unrelated keys.
    """
    merged = dict(current)
    merged.update(update)
    return merged


class AgentState(TypedDict):
    company_url: str
    icp_criteria: dict
    raw_content: str
    extracted_triggers: list[dict]
    qualification_score: int
    is_qualified: bool
    summary: str
    company_name: str
    industry: str
    employee_count: int
    next_actions: list[str]
    contacts: list[dict]
    personas: list[str]
    from_memory: bool
    human_feedback: str
    edited_icp: dict
    approval_status: str
    recommended_action: dict
    execution_plan: list[dict]
    current_step_index: int
    prospect_intelligence: Annotated[dict, merge_prospect_intelligence]
    user_id: str
    force_refresh: bool
    messages: Annotated[list, add_messages]
    trigger_score: int
    industry_score: int
    employee_score: int
