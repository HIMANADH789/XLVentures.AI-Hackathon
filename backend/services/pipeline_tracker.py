"""In-memory pipeline stage tracker for live visualization."""

import time
import uuid
from typing import Optional, Literal


def _now() -> float:
    return time.time()


STAGE_DEFINITIONS = [
    {"id": "scraping", "label": "Website Scrape", "icon": "globe", "phase": 1},
    {"id": "news_search", "label": "News Search", "icon": "newspaper", "phase": 1},
    {"id": "contact_finding", "label": "Contact Finding", "icon": "users", "phase": 1},
    {"id": "trigger_extraction", "label": "Trigger Extraction", "icon": "zap", "phase": 1},
    {"id": "icp_qualification", "label": "ICP Scoring", "icon": "target", "phase": 1},
    {"id": "enrichment", "label": "Enrichment", "icon": "database", "phase": 2},
    {"id": "summary", "label": "Summary", "icon": "file-text", "phase": 2},
    {"id": "action_recommendation", "label": "Action Plan", "icon": "lightbulb", "phase": 2},
    {"id": "saving", "label": "Saving Results", "icon": "save", "phase": 1},
    {"id": "complete", "label": "Complete", "icon": "check", "phase": None},
]

STAGE_ORDER = [s["id"] for s in STAGE_DEFINITIONS]

_pipelines: dict[str, dict] = {}


def create_pipeline(url: str, pipeline_id: str | None = None) -> str:
    pipeline_id = pipeline_id or str(uuid.uuid4())
    _pipelines[pipeline_id] = {
        "id": pipeline_id,
        "url": url,
        "stages": {
            s["id"]: {
                "status": "pending",
                "started_at": None,
                "duration": None,
                "error": None,
            }
            for s in STAGE_DEFINITIONS
        },
        "activities": [],
        "current_stage": None,
        "completed": False,
        "error": None,
        "created_at": _now(),
    }
    return pipeline_id


def add_activity(pipeline_id: str, message: str, status: Literal["running", "completed", "failed"] = "completed"):
    """Append a human-readable activity entry to the pipeline log."""
    p = _pipelines.get(pipeline_id)
    if not p:
        return
    p["activities"].append({
        "message": message,
        "status": status,
        "timestamp": _now(),
    })


def start_stage(pipeline_id: str, stage_id: str):
    p = _pipelines.get(pipeline_id)
    if not p:
        return
    p["current_stage"] = stage_id
    stage = p["stages"].get(stage_id)
    if stage:
        stage["status"] = "running"
        stage["started_at"] = time.time()


def complete_stage(pipeline_id: str, stage_id: str, activity_message: str | None = None):
    p = _pipelines.get(pipeline_id)
    if not p:
        return
    stage = p["stages"].get(stage_id)
    if stage and stage["started_at"]:
        stage["status"] = "completed"
        stage["duration"] = round(time.time() - stage["started_at"], 2)
        label = None
        for sd in STAGE_DEFINITIONS:
            if sd["id"] == stage_id:
                label = sd["label"]
                break
        msg = activity_message or f"Completed: {label or stage_id}"
        add_activity(pipeline_id, msg, "completed")


def fail_stage(pipeline_id: str, stage_id: str, error: str = ""):
    p = _pipelines.get(pipeline_id)
    if not p:
        return
    stage = p["stages"].get(stage_id)
    if stage:
        stage["status"] = "failed"
        stage["error"] = error
        if stage["started_at"]:
            stage["duration"] = round(time.time() - stage["started_at"], 2)


def complete_pipeline(pipeline_id: str):
    p = _pipelines.get(pipeline_id)
    if p:
        p["completed"] = True
        p["current_stage"] = None


def fail_pipeline(pipeline_id: str, error: str = ""):
    p = _pipelines.get(pipeline_id)
    if p:
        p["completed"] = True
        p["error"] = error
        p["current_stage"] = None


def get_pipeline(pipeline_id: str) -> Optional[dict]:
    return _pipelines.get(pipeline_id)


def get_pipeline_stages_list(pipeline_id: str) -> list:
    p = _pipelines.get(pipeline_id)
    if not p:
        return []
    stages = []
    for stage_def in STAGE_DEFINITIONS:
        sid = stage_def["id"]
        stage_info = p["stages"].get(sid, {})
        stages.append({
            "id": stage_def["id"],
            "label": stage_def["label"],
            "icon": stage_def["icon"],
            "phase": stage_def.get("phase"),
            "status": stage_info.get("status", "pending"),
            "duration": stage_info.get("duration"),
            "error": stage_info.get("error"),
        })
    return stages
