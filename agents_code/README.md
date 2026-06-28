# Agentic AI Platform - Hackathon Project

A LangGraph-powered Streamlit app for company lead qualification, enrichment, and outreach recommendation.

## Setup

### Prerequisites

- Python 3.11+
- Virtual environment (provided at `venv/`)

### Environment Variables

Create a `.env` file in the project root with the following keys:

```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=...
GROQ_API_KEY=gsk_...
```

| Variable          | Required | Purpose                              |
|-------------------|----------|--------------------------------------|
| `GROQ_API_KEY`    | Yes      | LLM inference (llama-3.3-70b)        |
| `FIRECRAWL_API_KEY` | No    | Website scraping (falls back to mock) |
| `OPENAI_API_KEY`  | No       | Reserved for future use              |

### Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\Activate

# Install packages
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run main.py
```

## Demo Guide

### Sidebar Configuration

The sidebar contains a "Platform Configuration" section where you can set global defaults for:

- **Default Industry** – Pre-fills the target industry field in the Analysis tab.
- **Default Min Employees** – Pre-fills the employee count threshold.
- **Default Personas** – Pre-fills the target personas multiselect.

These defaults can be overridden per-session in the Analysis tab inputs.

### Approval Workflow

1. Enter a company URL and click **Run Analysis**.
2. The system scrapes the URL, extracts triggers, and scores the lead against ICP criteria.
3. Review the results in the **Pending Approval** box.
4. Choose an action:
   - **Approve & Enrich** – Generates contacts, executive summary, and a recommended next action with a draft message.
   - **Reject** – Saves the result to memory without enrichment.
   - **Edit ICP** – Adjusts industry, min/max employees and re-runs qualification locally.
5. Approved results display the **Next Best Action** card with a copy-friendly draft message.

### History Tab

Shows all previously analyzed companies. Each entry displays the URL, score, and qualification status. Use **Clear Memory** to reset the cache.

## Dashboard

![Dashboard Screenshot](docs/screenshot.png)
