from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from routes import discover, companies, contacts
import models.company
import models.contact
import models.discovery_log
import models.icp_config

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProspectOS API",
    description="Agentic AI platform for B2B customer discovery",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(discover.router)
app.include_router(companies.router)
app.include_router(contacts.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "disconnected", "error": str(e)}

@app.get("/health/services")
def health_services():
    return {
        "ai": "ok",
        "apollo": "ok",
        "hunter": "ok"
    }
