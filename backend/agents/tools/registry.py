TOOL_REGISTRY: dict[str, str] = {}
"""Global registry mapping tool names to human-readable descriptions."""


def register_tool(name: str, description: str) -> None:
    """Register a tool by name and description for Planner discovery.

    Args:
        name: Unique tool identifier (must match TOOL_HANDLERS key in graph.py).
        description: Natural-language explanation of what the tool does.
    """
    TOOL_REGISTRY[name] = description


def list_available_tools() -> list[dict]:
    """Return all registered tools as a list of {name, description} dicts.

    Used by the Planner agent to decide which enrichment steps to run.
    """
    return [
        {"name": name, "description": desc}
        for name, desc in TOOL_REGISTRY.items()
    ]


register_tool(
    "find_contacts",
    "Find target contacts at the company based on target personas (VP Sales, CTO, etc.)",
)
register_tool(
    "analyze_tech_stack",
    "Scan website content to identify technologies and frameworks used (AWS, Python, React, Kubernetes, etc.)",
)
register_tool(
    "check_sentiment",
    "Determine business sentiment (Positive/Negative/Neutral) from detected growth triggers",
)
register_tool(
    "track_hiring_velocity",
    "Estimate hiring velocity (High/Medium/Low) based on volume of job postings and hiring signals",
)
