# Response Contracts

This document defines the strict API contracts for the ProspectOS pipeline.

## 1. AI Output Contracts

These are the expected JSON outputs from the AI models. The backend will assert these schemas.

### 1.1 Trigger Agent Output
```json
{
  "company": "string",
  "trigger": "string",
  "date": "string (YYYY-MM-DD)",
  "confidence": "float"
}
```

### 1.2 ICP Matcher Output
```json
{
  "qualified": "boolean",
  "score": "integer",
  "reason": [
    "string"
  ]
}
```

### 1.3 Summary Agent Output
```json
{
  "summary": "string"
}
```

## 2. Frontend Expected Inputs (Backend Outputs)

These are the schemas the backend will serve to the frontend.

### 2.1 POST /discover Response
```json
{
  "company": "Acme AI",
  "trigger": "Raised Series A",
  "score": 91,
  "summary": "High likelihood of buying sales software.",
  "contacts": [
    {
      "name": "John Doe",
      "role": "Founder",
      "email": "john@acme.ai"
    }
  ]
}
```

### 2.2 GET /companies Response
```json
[
  {
    "id": "uuid",
    "name": "Acme AI",
    "trigger_type": "funding",
    "trigger_source": "linkedin",
    "icp_score": 91,
    "status": "enriched"
  }
]
```

## 3. Backend Expected Inputs (Frontend Outputs)

### 3.1 POST /discover Request
```json
{
  "company_inputs": [
    {
      "url": "https://acme.ai",
      "source": "manual"
    }
  ]
}
```

### 3.2 POST /contacts Request
```json
{
  "company_domain": "acme.ai"
}
```
