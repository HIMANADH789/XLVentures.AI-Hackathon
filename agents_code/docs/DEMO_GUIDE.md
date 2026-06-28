# 5-Minute Demo Guide

## Prerequisites

- Environment is set up (`.env` with `OPENAI_API_KEY`, `FIRECRAWL_API_KEY`, `GROQ_API_KEY`)
- `streamlit run agentic-platform/main.py` is running
- **No API keys needed** – the mock scraper and Groq free tier work out of the box

## Step-by-Step

### 1. Show Sidebar Configuration (30s)

Open the app in the browser. Draw attention to the **left sidebar**:

- "Default Industry" – set to `AI / SaaS`
- "Default Min Employees" – set to `10`
- "Default Personas" – `Founder`, `VP Sales`, `Head of Growth` are pre-selected

**Click "Save Configuration"** – this persists the settings to memory so the next session reloads them.

### 2. Run Analysis on a Company (60s)

Paste a URL into the **Company URL** field:

```
https://example.com
```

(The mock scraper will return realistic startup data. With a real Firecrawl API key, any live company URL works.)

**Click "Run Analysis"** – the spinner shows while the graph runs:

1. `check_memory` – no cache found, proceeds
2. `extract_triggers` – scrapes 5 pages (homepage, /careers, /about, /blog, /press)
3. `qualify_lead` – scores against ICP criteria

### 3. Show "Pending Approval" State (30s)

After the spinner stops, the UI shows:

- **Score** – e.g., `60/100`
- **Qualified** – `Yes` or `No`
- **Triggers Found** – count with expandable details
- **Extracted Triggers** – expand to see each trigger type, confidence, and source URL

Point out that the scraper found **Funding**, **Hiring**, **Growth**, **Product**, and **Partnership** triggers.

Three buttons appear: **Approve & Enrich**, **Reject**, **Edit ICP**.

### 4. Click "Approve" to Trigger the Planner (30s)

**Click "Approve & Enrich"** – a second graph invocation runs:

1. `plan_next_steps` – the LLM-based Planner inspects available tools and detected triggers, then emits an execution plan
2. `execute_step` loop – runs each tool in sequence:
   - `find_contacts` – generates contacts for each persona
   - `analyze_tech_stack` – scans content for technologies
   - `check_sentiment` – determines positive/negative/neutral
   - `track_hiring_velocity` – estimates hiring pace
3. `aggregate_intelligence` – LLM writes a Strategic Insight paragraph
4. `generate_summary` – produces an Executive Brief
5. `recommend_action` – generates a Next Best Action with draft message
6. `save_to_memory` – caches everything for future lookups

### 5. Show Dynamic Execution Plan (30s)

After enrichment completes, the **Execution Plan** expander shows the LLM-generated plan with reasoning for each step:

```
1. find_contacts — Lead is qualified, locate contacts
2. analyze_tech_stack — Tech/growth triggers detected
3. check_sentiment — Contextual sentiment analysis
4. track_hiring_velocity — Hiring signals found
```

### 6. Show Final "Next Best Action" (60s)

Scroll down to see:

- **Prospect Intelligence** – three columns: Tech Stack tags (blue-background), Sentiment gauge (🟢 Positive), Hiring Velocity badge (🔴 High)
- **Strategic Insight** – LLM-generated paragraph synthesizing the profile
- **Executive Brief** – full summary of the analysis
- **Next Best Action** – recommended outreach type + reasoning + **draft message** (click to copy)
- **Key Contacts** – generated contact cards with name, role, email, LinkedIn

**Copy the draft email** to demonstrate a concrete takeaway.

### 7. Show History and Memory (60s)

Switch to the **History** tab:

- The company appears with score, status label, timestamp, and sentiment icon
- **Filter by Status** – select "Qualified", "Rejected", or "Not Qualified" to filter the list
- Entries sorted by most recent first

Now switch back to **Analysis**, enter the **same URL** again, and click **Run Analysis**:

- The spinner is much faster this time because `check_memory` returns cached data
- The pending approval screen shows the same results without re-scraping

**Explain**: This is the MemoryStore at work – previously rejected companies are re-analyzed by default, while qualified/not-qualified ones serve from cache instantly.

---

## Troubleshooting During Demo

| Symptom | Fix |
|---------|-----|
| "Analysis failed" error | Check `.env` has `GROQ_API_KEY` set |
| Scraping returns empty | No Firecrawl key? Mock data is used automatically |
| Planner returns empty plan | Ensure `approval_status: "approved"` is set (click Approve) |
| Memory shows stale data | Check the "Force re-analysis" checkbox and re-run |
