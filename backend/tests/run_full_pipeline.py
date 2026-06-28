import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_tests():
    print("--- Starting Full Pipeline Run ---")
    
    # 1. Health Checks
    print("\n1. Testing Health Endpoints...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    print("GET /health OK")
    
    res = requests.get(f"{BASE_URL}/health/db")
    assert res.status_code == 200
    print("GET /health/db OK")
    
    res = requests.get(f"{BASE_URL}/health/services")
    assert res.status_code == 200
    print("GET /health/services OK")
    
    # 2. Discover
    print("\n2. Testing POST /discover...")
    payload = {
        "company_inputs": [
            {
                "url": "https://test-pipeline.ai",
                "source": "automated_test"
            }
        ],
        "force_refresh": True
    }
    res = requests.post(f"{BASE_URL}/discover", json=payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    discover_data = res.json()
    print("POST /discover OK")
    print(f"Discovered: {discover_data.get('company')} with score {discover_data.get('score')}")
    
    # Give DB a tiny moment if async (it's sync but good practice)
    time.sleep(0.5)
    
    # 3. Get Companies
    print("\n3. Testing GET /companies...")
    res = requests.get(f"{BASE_URL}/companies")
    assert res.status_code == 200
    companies = res.json()
    assert len(companies) > 0
    print(f"GET /companies OK ({len(companies)} found)")
    
    # Find the one we just created
    target_company = next((c for c in companies if c.get('website') == "https://test-pipeline.ai"), None)
    if not target_company:
        # Fallback if website wasn't returned in the summary payload (our schema might omit it in the list view depending on schema implementation)
        target_company = companies[-1]
        
    company_id = target_company.get("id")
    
    # 4. Get Company Details
    print(f"\n4. Testing GET /companies/{company_id}...")
    res = requests.get(f"{BASE_URL}/companies/{company_id}")
    assert res.status_code == 200
    details = res.json()
    print("GET /companies/{id} OK")
    print(f"Loaded details for {details.get('name')}")
    
    # 5. Get Contacts Manual
    print("\n5. Testing POST /contacts...")
    res = requests.post(f"{BASE_URL}/contacts", json={"company_domain": "test-pipeline.ai"})
    assert res.status_code == 200
    manual_contacts = res.json()
    print(f"POST /contacts OK ({len(manual_contacts)} returned)")
    
    print("\n--- All tests passed! ---")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] Pipeline test failed: {e}")
        exit(1)
