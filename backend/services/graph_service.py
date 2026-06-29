"""LangGraph two-phase pipeline integration for the discovery API.

Phase 1 (analyze):
  - Receives pre-collected data (website content, news, contacts)
  - Runs extract_triggers (LLM trigger detection) + qualify_lead (ICP scoring)
  - Returns triggers, score, qualification verdict

Phase 2 (enrich):
  - Takes the state from Phase 1 plus human approval
  - Runs planner → execute enrichment → aggregate → generate summary → recommend action
  - Returns enriched contacts, summary, prospect intelligence, recommended action
"""

import os
from datetime import datetime
from typing import Any

from agents.agents.trigger_agent import extract_triggers
from agents.agents.icp_agent import qualify_lead
from agents.agents.planner_agent import plan_next_steps
from agents.agents.specialized_agents import (
    analyze_tech_stack,
    check_sentiment,
    track_hiring_velocity,
)
from agents.agents.summary_agent import generate_summary
from agents.agents.action_agent import recommend_action
from agents.agents.intelligence_engine import aggregate_intelligence
from agents.tools.contact_finder import find_contacts as find_contacts_tool
from agents.tools.registry import TOOL_REGISTRY
from agents.state import AgentState
from urllib.parse import urlparse

TOOL_HANDLERS = {
    "find_contacts": lambda state, domain: {
        "contacts": find_contacts_tool(domain, state.get("personas", []))
    },
    "analyze_tech_stack": lambda state, _: analyze_tech_stack(state),
    "check_sentiment": lambda state, _: check_sentiment(state),
    "track_hiring_velocity": lambda state, _: track_hiring_velocity(state),
}


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.netloc or parsed.path.split("/")[0]).replace("www.", "")


def _build_state(url: str, website_content: str = "", news_data: list | None = None, contacts: list | None = None, icp_criteria: dict | None = None) -> dict:
    news_text = ""
    if news_data:
        headlines = [art.get("title") for art in news_data if art.get("title")]
        news_text = " | ".join(headlines[:5])
    
    return {
        "company_url": url,
        "icp_criteria": icp_criteria or {
            "industry": "Software / AI / SaaS / Tech",
            "min_employees": 10,
            "qualification_threshold": 60,
        },
        "raw_content": website_content,
        "news_headlines": news_text,
        "extracted_triggers": [],
        "qualification_score": 0,
        "is_qualified": False,
        "summary": "",
        "company_name": "",
        "industry": "",
        "employee_count": 0,
        "next_actions": [],
        "contacts": contacts or [],
        "personas": [],
        "from_memory": False,
        "human_feedback": "",
        "edited_icp": {},
        "approval_status": "pending",
        "recommended_action": {},
        "execution_plan": [],
        "current_step_index": 0,
        "prospect_intelligence": {},
        "user_id": "api",
        "force_refresh": False,
        "messages": [],
        "trigger_score": 0,
        "industry_score": 0,
        "employee_score": 0,
    }


def run_analysis(url: str, website_content: str = "", news_data: list | None = None, contacts: list | None = None, icp_criteria: dict | None = None) -> dict:
    """Phase 1: Run trigger extraction and ICP qualification on pre-collected data.
    
    Args:
        url: Company website URL
        website_content: Pre-scraped website content (Firecrawl/HTTP)
        news_data: NewsAPI results
        contacts: Hunter/Apollo contact results
        icp_criteria: ICP configuration (industry, min_employees, threshold)
    
    Returns:
        dict with company metadata, triggers, score, qualification
    """
    state = _build_state(url, website_content, news_data, contacts, icp_criteria)
    
    # Phase 1a: Extract triggers from content
    trigger_result = extract_triggers(state)
    state.update(trigger_result)
    
    # Phase 1b: Qualify lead
    icp_result = qualify_lead(state)
    state.update(icp_result)
    
    return {
        "company_name": state.get("company_name", ""),
        "industry": state.get("industry", ""),
        "employee_count": state.get("employee_count", 0),
        "trigger_events": state.get("extracted_triggers", []),
        "trigger_score": state.get("trigger_score", 0),
        "industry_score": state.get("industry_score", 0),
        "employee_score": state.get("employee_score", 0),
        "qualification_score": state.get("qualification_score", 0),
        "is_qualified": state.get("is_qualified", False),
        "summary": state.get("summary", ""),
        "approval_status": "pending",
        "raw_content": state.get("raw_content", ""),
    }


def approve_and_enrich(state: dict, personas: list | None = None) -> dict:
    """Phase 2: Run enrichment pipeline after human approval.
    
    Args:
        state: The full state dict returned from run_analysis
        personas: Target personas for contact finding
    
    Returns:
        dict with enriched contacts, summary, prospect_intelligence, recommended_action
    """
    state["approval_status"] = "approved"
    if personas:
        state["personas"] = personas
    
    domain = _domain_from_url(state.get("company_url", ""))
    
    # Run planner
    plan_result = plan_next_steps(state)
    state.update(plan_result)
    
    # Execute each step in the plan
    execution_plan = state.get("execution_plan", [])
    for step in execution_plan:
        tool_name = step["tool"]
        handler = TOOL_HANDLERS.get(tool_name)
        if handler:
            result = handler(state, domain)
            state.update(result)
    
    # Aggregate intelligence (strategic insight)
    agg_result = aggregate_intelligence(state)
    state.update(agg_result)
    
    # Generate executive summary
    summary_result = generate_summary(state)
    state.update(summary_result)
    
    # Recommend next action
    action_result = recommend_action(state)
    state.update(action_result)
    
    return {
        "contacts": state.get("contacts", []),
        "summary": state.get("summary", ""),
        "prospect_intelligence": state.get("prospect_intelligence", {}),
        "recommended_action": state.get("recommended_action", {}),
        "execution_plan": execution_plan,
        "qualification_score": state.get("qualification_score", 0),
        "is_qualified": state.get("is_qualified", False),
        "trigger_score": state.get("trigger_score", 0),
        "industry_score": state.get("industry_score", 0),
        "employee_score": state.get("employee_score", 0),
        "company_name": state.get("company_name", ""),
        "industry": state.get("industry", ""),
        "employee_count": state.get("employee_count", 0),
        "trigger_events": state.get("extracted_triggers", []),
    }


def reject(state: dict) -> dict:
    """Mark a company as rejected."""
    return {
        "approval_status": "rejected",
        "status": "rejected",
    }


def rescore(state: dict, new_icp: dict) -> dict:
    """Re-qualify a company with edited ICP criteria."""
    state["icp_criteria"] = new_icp
    icp_result = qualify_lead(state)
    state.update(icp_result)
    
    return {
        "qualification_score": state.get("qualification_score", 0),
        "is_qualified": state.get("is_qualified", False),
        "trigger_score": state.get("trigger_score", 0),
        "industry_score": state.get("industry_score", 0),
        "employee_score": state.get("employee_score", 0),
        "summary": state.get("summary", ""),
    }
