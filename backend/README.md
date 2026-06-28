# ProspectOS Phase 1 Backend

This is the fully integrated backend for ProspectOS Phase 1. It serves as the integration spine between the AI agents (Trigger, ICP, Summary) and the Frontend dashboard.

## 🚀 Quickstart

### 1. Prerequisites
- Docker (for PostgreSQL database)
- Python 3.10+

### 2. Environment Setup
Copy the example environment file and fill in the required values:
```bash
cp .env.example .env
```

### 3. Start Database
Spin up the local PostgreSQL instance using Docker Compose:
```bash
docker-compose up -d
```
*Note: This starts Postgres 15 on port 5432 with volume persistence.*

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Server
The FastAPI application uses synchronous SQLAlchemy (psycopg2) and automatically handles DB table creation upon startup.
```bash
uvicorn backend.app:app --reload
```
Access the Swagger UI at: `http://localhost:8000/docs`

### 6. Seed the Database
To populate the dashboard with realistic mock data (without needing to run discoveries):
```bash
python backend/scripts/seed.py
```
This inserts a diverse dataset (funding, hiring, M&A triggers) directly into the database.

### 7. Run Pipeline Tests
Validate the entire end-to-end flow:
```bash
python backend/tests/run_full_pipeline.py
```

## 🤝 Team Handoff Assets

### For the AI Team (Person 1)
- Refer to `backend/response_contracts.md` and `backend/integration_manifest.json` for strict API payload structures.
- Use `backend/tests/test_contracts.py` to ensure your agent outputs match the expected schemas exactly.
- Expected mock payloads are available in `backend/sample_payloads/`.

### For the Frontend Team (Person 3)
- Import `backend/postman_collection.json` to view and trigger all API routes.
- You can build the dashboard entirely offline using the JSON examples in `backend/sample_payloads/`.
- Use the `GET /companies` and `GET /companies/{id}` routes for the main table and detail drawers. Field names are strictly locked.
