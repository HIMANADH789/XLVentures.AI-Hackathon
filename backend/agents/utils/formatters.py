import json
import re
from datetime import datetime


def extract_json(text: str):
    """Parse JSON from LLM output, stripping markdown code fences if present.

    Handles the common case where Groq wraps JSON in ```json ... ``` blocks.
    Falls through to json.loads on the raw text if no fences are found.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def format_score(score: int, max_score: int = 100) -> str:
    return f"{score}/{max_score}"


def format_qualification(is_qualified: bool) -> str:
    return "Qualified" if is_qualified else "Not Qualified"


def format_contact_list(contacts: list[dict]) -> str:
    lines = []
    for c in contacts:
        lines.append(
            f"{c.get('name', 'N/A')} — {c.get('role', 'N/A')} ({c.get('email', 'N/A')})"
        )
    return "\n".join(lines)


def format_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def format_trigger_summary(triggers: list[dict]) -> str:
    if not triggers:
        return "No triggers detected"
    parts = []
    for t in triggers:
        ttype = t.get("trigger_type", "unknown")
        conf = t.get("confidence", 0)
        parts.append(f"{ttype} (confidence: {conf})")
    return ", ".join(parts)
