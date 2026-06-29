import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from ..state import AgentState
from ..utils.formatters import extract_json


def analyze_tech_stack(state: AgentState) -> dict:
    """Use ChatGroq to extract technology names from raw website content.

    Scans raw_content for mentions of frameworks, platforms, and tools
    (AWS, Python, React, Kubernetes, etc.) and returns them as a list.

    Returns:
        dict with prospect_intelligence.tech_stack (list of strings).
    """
    raw_content = state.get("raw_content", "")
    if not raw_content:
        return {"prospect_intelligence": {"tech_stack": []}}

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    system_prompt = (
        "From the website content below, extract all technologies, frameworks, "
        "and platforms explicitly mentioned (e.g. AWS, Python, React, Kubernetes, etc.). "
        "Return a JSON object with a single key 'tech_stack' containing an array of strings."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=raw_content[:4000]),
    ]

    response = llm.invoke(messages)
    try:
        result = extract_json(response.content)
        return {"prospect_intelligence": {"tech_stack": result.get("tech_stack", [])}}
    except Exception:
        return {"prospect_intelligence": {"tech_stack": []}}


def check_sentiment(state: AgentState) -> dict:
    """Determine business sentiment from detected trigger types.

    Positive triggers: funding, product_launch, partnership, acquisition, expansion.
    Negative triggers: layoffs, restructuring, lawsuit.

    Returns:
        dict with prospect_intelligence.sentiment ("Positive"/"Negative"/"Neutral").
    """
    triggers = state.get("extracted_triggers", [])
    positive_types = {"funding", "product_launch", "partnership", "acquisition", "expansion"}
    negative_types = {"layoffs", "restructuring", "lawsuit"}

    has_positive = any(
        t.get("trigger_type", "").lower() in positive_types for t in triggers
    )
    has_negative = any(
        t.get("trigger_type", "").lower() in negative_types for t in triggers
    )

    if has_positive and not has_negative:
        sentiment = "Positive"
    elif has_negative and not has_positive:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {"prospect_intelligence": {"sentiment": sentiment}}


def track_hiring_velocity(state: AgentState) -> dict:
    """Estimate hiring velocity based on number of 'hiring' triggers.

    Thresholds: >5 = High, >0 = Medium, 0 = Low.

    Returns:
        dict with prospect_intelligence.hiring_velocity ("High"/"Medium"/"Low").
    """
    triggers = state.get("extracted_triggers", [])
    hiring_count = sum(
        1 for t in triggers if t.get("trigger_type", "").lower() == "hiring"
    )

    if hiring_count > 5:
        velocity = "High"
    elif hiring_count > 0:
        velocity = "Medium"
    else:
        velocity = "Low"

    return {"prospect_intelligence": {"hiring_velocity": velocity}}
