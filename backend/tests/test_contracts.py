import pytest
from services.ai_service import get_trigger, get_icp_score, get_summary
from schemas.discover_schema import DiscoverResponse
import json

def test_trigger_contract():
    expected_keys = {"company", "trigger", "date", "confidence"}
    response = get_trigger("https://example.com")
    assert set(response.keys()) == expected_keys, f"Schema drift in Trigger output."
    assert "company" in response
    assert "trigger" in response

def test_icp_contract():
    expected_keys = {"qualified", "score", "reason"}
    response = get_icp_score({})
    assert set(response.keys()) == expected_keys, f"Schema drift in ICP output."
    assert "score" in response

def test_summary_contract():
    expected_keys = {"summary"}
    response = get_summary({})
    assert set(response.keys()) == expected_keys, f"Schema drift in Summary output."
    assert "summary" in response

def test_discover_response_schema():
    # Load sample payload to verify it matches
    with open("sample_payloads/discover_output.json", "r") as f:
        response = json.load(f)
        
    assert "company" in response
    assert "trigger" in response
    assert "score" in response
    assert "summary" in response
    assert "contacts" in response
    assert "status" in response
