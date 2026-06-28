# ProspectIQ

> AI-powered B2B prospecting platform that discovers, enriches, and qualifies companies in real time.

ProspectIQ automates the sales intelligence workflow: paste a company URL, and the system crawls the website, searches recent news, finds decision-maker contacts, and returns a fully scored prospect profile — all powered by LLM analysis.

---

## Architecture

```
Frontend (Next.js 15)
       │
       ▼
   Axios Client
       │
       ▼
  FastAPI Backend
       │
       ├── POST /discover ──► Orchestrator
       │                         │
       │                 ┌───────┼───────┬──────────┐
       │                 ▼       ▼       ▼          ▼
       │            Firecrawl  NewsAPI  Hunter    Apollo
       │            (Website)  (News)  (Emails)  (Contacts)
       │                 │       │       │          │
       │                 └───────┴───────┴──────────┘
       │                         │
       │                    LLM Analysis
       │                  (Groq / OpenAI)
       │                         │
       │                    ┌────┴────┐
       │                    ▼         ▼
       │               Company    Contacts
       │              (SQLite)   (SQLite)
       │                    │
       ├── GET /companies ◄─┘
       └── GET /companies/:id
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS 4, Framer Motion |
| Backend | FastAPI, Python 3.13, SQLAlchemy, Pydantic |
| AI / LLM | LangChain, LangGraph, Groq (llama-3.3-70b), OpenAI (gpt-4o-mini) |
| Data Sources | Firecrawl (website crawling), NewsAPI (news search), Hunter.io (email finder), Apollo (contact search) |
| Database | SQLite (development) / PostgreSQL (production) |

---

## Project Structure

```
final_ver/
├── backend/                  # FastAPI backend
│   ├── app.py                # Application entry point
│   ├── config.py             # Settings (pydantic-settings)
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── company.py        # Company model
│   │   ├── contact.py        # Contact model
│   │   ├── discovery_log.py  # Discovery audit log
│   │   └── icp_config.py     # ICP configuration
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── company_schema.py
│   │   ├── contact_schema.py
│   │   └── discover_schema.py
│   ├── routes/               # API route handlers
│   │   ├── discover.py       # POST /discover
│   │   ├── companies.py      # GET /companies, GET /companies/:id
│   │   └── contacts.py       # POST /contacts
│   ├── services/             # Business logic layer
│   │   ├── orchestrator.py   # Discovery pipeline orchestrator
│   │   ├── ai_service.py     # LLM analysis (Groq/OpenAI)
│   │   ├── news_service.py   # NewsAPI integration
│   │   ├── hunter_service.py # Hunter.io email finder
│   │   ├── apollo_service.py # Apollo contact search
│   │   └── company_service.py# Contact merging logic
│   ├── utils/                # Shared utilities
│   │   ├── normalizer.py     # Trigger & role normalization
│   │   ├── logger.py         # Discovery audit logger
│   │   └── retry.py          # Retry decorator
│   ├── tests/                # Test suite
│   ├── .env                  # Environment variables
│   └── requirements.txt      # Python dependencies
│
├── hack_v2/                  # Next.js frontend
│   ├── app/
│   │   ├── page.tsx          # Main dashboard page
│   │   ├── layout.tsx        # Root layout
│   │   ├── loading.tsx       # Loading skeleton
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── company/          # Company drawer detail view
│   │   ├── dashboard/        # Dashboard stats cards
│   │   ├── table/            # Lead table with sorting/filtering
│   │   ├── layout/           # Sidebar, header
│   │   └── ui/               # Shared UI primitives (badge, button, etc.)
│   ├── services/
│   │   └── api.ts            # Axios API client
│   ├── hooks/
│   │   └── use-companies.ts  # React hook for company state
│   ├── types/
│   │   └── company.ts        # TypeScript interfaces
│   └── .env                  # Frontend environment variables
│
└── agents_code/              # LangGraph AI agent pipeline
    └── app/
        ├── agents/           # Individual AI agents
        │   ├── trigger_agent.py    # Trigger event extraction
        │   ├── icp_agent.py        # ICP qualification scoring
        │   ├── summary_agent.py    # Executive summary generation
        │   ├── planner_agent.py    # Pipeline planning
        │   └── action_agent.py     # Action recommendation
        ├── tools/            # Agent tools
        │   ├── scraper.py    # Firecrawl + HTTP scraping
        │   ├── contact_finder.py   # Contact discovery
        │   └── memory.py    # Conversation memory
        ├── graph.py          # LangGraph workflow definition
        └── state.py          # Agent state schema
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository

```bash
git clone <repository-url>
cd final_ver
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys (see Environment Variables below)
```

### 3. Frontend Setup

```bash
cd hack_v2

# Install dependencies
npm install
```

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
PYTHONPATH=. uvicorn app:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd hack_v2
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string. Default: `sqlite:///./prospectos.db` |
| `LLM_PROVIDER` | Yes | LLM provider to use: `openai` or `groq` |
| `GROQ_API_KEY` | Yes* | Groq API key (free at [console.groq.com](https://console.groq.com)) |
| `OPENAI_API_KEY` | Yes* | OpenAI API key (if using `openai` provider) |
| `FIRECRAWL_API_KEY` | Recommended | Firecrawl API key for website crawling ([firecrawl.dev](https://firecrawl.dev)) |
| `NEWS_API_KEY` | Recommended | NewsAPI key for news search ([newsapi.org](https://newsapi.org)) |
| `HUNTER_API_KEY` | Recommended | Hunter.io API key for email finding ([hunter.io](https://hunter.io)) |
| `APOLLO_API_KEY` | Optional | Apollo API key for contact enrichment |
| `SERPAPI_KEY` | Optional | SerpAPI key (unused in current pipeline) |

> *At least one of `GROQ_API_KEY` or `OPENAI_API_KEY` must be set.

### Frontend (`hack_v2/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL. Default: `http://127.0.0.1:8000` |

---

## API Reference

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health check |
| `GET` | `/health/db` | Database connectivity check |
| `GET` | `/health/services` | External service status |

### Discovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/discover` | Run AI discovery pipeline on a company URL |

**Request body:**
```json
{
  "company_inputs": [
    {
      "url": "https://openai.com",
      "source": "manual"
    }
  ],
  "force_refresh": true
}
```

**Response:**
```json
{
  "company": "OpenAI",
  "trigger": "hiring",
  "score": 80,
  "summary": "OpenAI is an AI research company...",
  "status": "new",
  "firecrawl_used": true,
  "news_used": true,
  "news_headlines": "OpenAI raises $6B...",
  "trigger_source": "news",
  "trigger_confidence": 0.9,
  "contact_confidence": 0.9,
  "summary_confidence": 0.85,
  "discovery_timestamp": "2026-06-28T08:44:50.101258",
  "contacts": [
    {
      "name": "Sam Altman",
      "role": "Founder/CEO",
      "email": "sam@openai.com",
      "linkedin": null,
      "source": "Hunter"
    }
  ]
}
```

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/companies` | List all discovered companies |
| `GET` | `/companies/:id` | Get company details with contacts |

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/contacts` | Enrich contacts for a domain |

**Request body:**
```json
{
  "company_domain": "openai.com"
}
```

---

## Discovery Pipeline

When you submit a company URL to `POST /discover`, the following pipeline executes:

1. **Firecrawl** — Crawls the company website (homepage, about, careers, blog) to extract text content.
2. **NewsAPI** — Searches for recent news articles (last 28 days) mentioning the company.
3. **Hunter.io** — Finds decision-maker email addresses and roles at the company domain.
4. **Apollo** — (Optional) Enriches contacts with additional data from Apollo's database.
5. **LLM Analysis** — Sends all gathered data to a Groq or OpenAI model that produces:
   - Company name and industry classification
   - Trigger event identification (Hiring, Funding, Product Launch, Expansion, etc.)
   - Dynamic ICP score (0–100) based on trigger match, industry fit, and employee count
   - Qualification decision (score ≥ 60 = qualified)
   - Plain-text executive summary
   - Enriched contacts with source attribution
6. **Database** — Saves the company profile, contacts, and discovery metadata to SQLite.

### ICP Scoring Formula

| Component | Points | Criteria |
|-----------|--------|----------|
| Trigger Match | 50 | Relevant trigger event detected (Hiring, Funding, etc.) |
| Industry Match | 30 | Company is in Software / AI / SaaS / Tech |
| Employee Match | 20 | Company has 10+ employees |
| **Total** | **100** | Qualified if score ≥ 60 |

### Graceful Degradation

The pipeline never fails completely. If an API key is missing or a service is unavailable:

- **No Firecrawl key** → Falls back to raw HTTP scraping
- **No NewsAPI key** → Skips news search, sets `news_used: false`
- **No Hunter key** → Returns empty contacts list
- **LLM failure** → Retries up to 3 times with exponential backoff

---

## Development

### Running Tests

```bash
cd backend
PYTHONPATH=. python -m pytest tests/ -v
```

### Full Pipeline Test

```bash
cd backend
PYTHONPATH=. python tests/run_full_pipeline.py
```

### Production Build (Frontend)

```bash
cd hack_v2
npm run build
npm start
```

---

## License

This project was built for a hackathon demonstration.
