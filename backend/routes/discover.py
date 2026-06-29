import threading

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.discover_schema import (
    DiscoverRequest,
    ApproveResponse,
    RejectResponse,
    ReScoreRequest,
    ReScoreResponse,
)
from services.orchestrator import process_discovery
from services.graph_service import run_analysis, approve_and_enrich, reject, rescore
from services.pipeline_tracker import (
    create_pipeline, get_pipeline_stages_list, get_pipeline,
    start_stage, complete_stage, complete_pipeline, fail_pipeline,
)
from models.company import Company
from models.contact import Contact
from utils.logger import log_discovery_step
from datetime import datetime
from uuid import UUID
import traceback

router = APIRouter(prefix="/discover", tags=["Discovery"])


def _load_icp_criteria(db) -> dict:
    """Load ICP criteria from the database settings, falling back to defaults."""
    from models.icp_config import IcpConfig
    config = db.query(IcpConfig).order_by(IcpConfig.created_at.desc()).first()
    if config and config.industry:
        return {
            "industry": config.industry,
            "min_employees": config.employee_min or 10,
            "qualification_threshold": 60,
        }
    return {
        "industry": "Software / AI / SaaS / Tech",
        "min_employees": 10,
        "qualification_threshold": 60,
    }


def _run_phase1_background(pipeline_id: str, url: str, source: str, force_refresh: bool):
    """Run Phase 1 discovery in a background thread."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        log_discovery_step(status=f"Analysis started for {url}")

        from services.orchestrator import _collect_discovery_data

        # Data collection phase (sub-stages tracked inside _collect_discovery_data)
        collected = _collect_discovery_data(url, db, pipeline_id=pipeline_id)

        # LLM analysis phase (trigger extraction + ICP scoring)
        start_stage(pipeline_id, "trigger_extraction")
        icp_criteria = _load_icp_criteria(db)
        analysis = run_analysis(
            url=url,
            website_content=collected.get("website_content", ""),
            news_data=collected.get("news_data", []),
            contacts=collected.get("contacts_data", []),
            icp_criteria=icp_criteria,
        )
        company_name = analysis.get("company_name") or url
        trigger_count = len(analysis.get("trigger_events", []))
        score = analysis.get("qualification_score", 0)
        complete_stage(pipeline_id, "trigger_extraction", f"Extracted {trigger_count} triggers, score: {score}/100")
        # ICP scoring happened inside run_analysis — mark completed too
        complete_stage(pipeline_id, "icp_qualification")

        # Map graph result to DB fields
        trigger_events = analysis.get("trigger_events", [])
        first_trigger = trigger_events[0] if trigger_events else {}
        trigger_type = first_trigger.get("trigger_type")
        trigger_source = first_trigger.get("source_url") or source
        trigger_confidence = first_trigger.get("confidence") or 0.8

        start_stage(pipeline_id, "saving")

        contacts_data = collected.get("contacts_data", [])
        employee_count = analysis.get("employee_count") or collected.get("employee_count") or 0
        company = Company(
            name=analysis.get("company_name") or "Unknown",
            website=url,
            industry=analysis.get("industry") or "AI / SaaS",
            employee_count=employee_count,
            trigger_type=trigger_type,
            trigger_source=trigger_source,
            trigger_confidence=trigger_confidence,
            contact_confidence=0.9 if contacts_data else 0.0,
            trigger_score=analysis.get("trigger_score", 0),
            industry_score=analysis.get("industry_score", 0),
            employee_score=analysis.get("employee_score", 0),
            icp_score=float(analysis.get("qualification_score", 0)),
            qualified=analysis.get("is_qualified", False),
            summary=analysis.get("summary", ""),
            status="pending_review",
            approval_status="pending",
            discovery_timestamp=datetime.utcnow(),
            firecrawl_used=collected.get("firecrawl_used", False),
            news_used=collected.get("news_used", False),
            news_headlines=collected.get("news_headlines", ""),
        )
        db.add(company)
        db.flush()

        # Save contacts from Hunter
        for c_data in contacts_data:
            contact = Contact(
                company_id=company.id,
                name=c_data.get("name"),
                role=c_data.get("role"),
                email=c_data.get("email"),
                linkedin=c_data.get("linkedin"),
                phone=c_data.get("phone"),
                source=c_data.get("source") or "Hunter",
            )
            db.add(contact)

        contact_count = len(contacts_data)
        db.commit()

        complete_stage(pipeline_id, "saving", f"Saved {company_name} with {contact_count} contacts")
        complete_pipeline(pipeline_id)
        log_discovery_step(status=f"Analysis completed for {url}")

    except Exception as e:
        db.rollback()
        fail_pipeline(pipeline_id, str(e))
        print(f"[BACKGROUND DISCOVER ERROR] {e}")
        traceback.print_exc()
    finally:
        db.close()


@router.post("")
def discover(request: DiscoverRequest, db: Session = Depends(get_db)):
    if not request.company_inputs:
        raise HTTPException(status_code=400, detail="company_inputs cannot be empty")

    # Legacy path: auto_approve=True runs synchronously (kept for backward compat)
    if request.auto_approve:
        pipeline_id = create_pipeline(request.company_inputs[0].url, request.pipeline_id)
        results = process_discovery(request.company_inputs, request.force_refresh, db, pipeline_id=pipeline_id)
        if len(results) == 1:
            results[0]["_pipeline_id"] = pipeline_id
            return results[0]
        return results

    # New two-phase path: returns immediately, runs in background
    for c_input in request.company_inputs:
        url = c_input.url
        source = c_input.source

        # Duplicate check
        if not request.force_refresh:
            existing = db.query(Company).filter(Company.website == url).first()
            if existing:
                contacts = db.query(Contact).filter(Contact.company_id == existing.id).all()
                return {
                    "company": existing.name,
                    "trigger": existing.trigger_type,
                    "score": existing.icp_score,
                    "summary": existing.summary,
                    "status": existing.status,
                    "approval_status": existing.approval_status or "pending",
                    "trigger_confidence": existing.trigger_confidence,
                    "contact_confidence": existing.contact_confidence,
                    "summary_confidence": existing.summary_confidence,
                    "firecrawl_used": existing.firecrawl_used,
                    "news_used": existing.news_used,
                    "news_headlines": existing.news_headlines,
                    "trigger_source": existing.trigger_source,
                    "company_name": existing.name,
                    "industry": existing.industry,
                    "employee_count": existing.employee_count,
                    "discovery_timestamp": existing.discovery_timestamp.isoformat() if existing.discovery_timestamp else None,
                    "contacts": [
                        {
                            "name": c.name,
                            "role": c.role,
                            "email": c.email,
                            "linkedin": c.linkedin,
                            "phone": c.phone,
                            "source": c.source,
                        } for c in contacts
                    ],
                }

        # Create pipeline and start background thread
        pipeline_id = c_input.pipeline_id or request.pipeline_id or None
        pipeline_id = create_pipeline(url, pipeline_id)

        thread = threading.Thread(
            target=_run_phase1_background,
            args=(pipeline_id, url, source, request.force_refresh),
            daemon=True,
        )
        thread.start()

        return {"_pipeline_id": pipeline_id, "status": "running"}

    return []


@router.post("/{company_id}/approve")
def approve_company(company_id: UUID, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.approval_status == "approved":
        raise HTTPException(status_code=400, detail="Company already approved")

    contacts_data = db.query(Contact).filter(Contact.company_id == company.id).all()
    existing_contacts = [
        {
            "name": c.name,
            "role": c.role,
            "email": c.email,
            "linkedin": c.linkedin,
            "phone": c.phone,
            "source": c.source,
        }
        for c in contacts_data
    ]

    icp_criteria = _load_icp_criteria(db)

    state = {
        "company_url": company.website,
        "company_name": company.name or "",
        "industry": company.industry or "",
        "employee_count": company.employee_count or 0,
        "extracted_triggers": [{
            "trigger_type": company.trigger_type or "Unknown",
            "source_url": company.trigger_source or company.website,
            "confidence": company.trigger_confidence or 0.8,
        }] if company.trigger_type else [],
        "trigger_type": company.trigger_type,
        "qualification_score": int(company.icp_score or 0),
        "trigger_score": company.trigger_score or 0,
        "industry_score": company.industry_score or 0,
        "employee_score": company.employee_score or 0,
        "contacts": existing_contacts,
        "raw_content": "",
        "personas": [],
        "icp_criteria": icp_criteria,
        "news_headlines": company.news_headlines or "",
    }

    try:
        result = approve_and_enrich(state)

        # Merge enrichment results into company
        enriched_contacts = result.get("contacts", [])
        company.summary = result.get("summary", company.summary)
        company.status = "enriched"
        company.approval_status = "approved"

        # Save enrichment data
        company.recommended_action = result.get("recommended_action")
        company.execution_plan = result.get("execution_plan")
        company.prospect_intelligence = result.get("prospect_intelligence")
        company.trigger_score = result.get("trigger_score", company.trigger_score)
        company.industry_score = result.get("industry_score", company.industry_score)
        company.employee_score = result.get("employee_score", company.employee_score)

        # Save new contacts from enrichment
        for c_data in enriched_contacts:
            name = c_data.get("name")
            email = c_data.get("email")
            if not name and not email:
                continue

            existing = None
            if email:
                existing = db.query(Contact).filter(
                    Contact.company_id == company.id,
                    Contact.email == email,
                ).first()
            elif name:
                existing = db.query(Contact).filter(
                    Contact.company_id == company.id,
                    Contact.name == name,
                ).first()

            if not existing:
                contact = Contact(
                    company_id=company.id,
                    name=name,
                    role=c_data.get("role"),
                    email=email,
                    linkedin=c_data.get("linkedin"),
                    phone=c_data.get("phone"),
                    source=c_data.get("source") or "Graph",
                )
                db.add(contact)

        db.commit()

        return {
            "company_name": company.name,
            "industry": company.industry,
            "employee_count": company.employee_count,
            "contacts": enriched_contacts,
            "summary": result.get("summary", ""),
            "qualification_score": result.get("qualification_score", int(company.icp_score or 0)),
            "is_qualified": result.get("is_qualified", company.qualified),
            "recommended_action": result.get("recommended_action", {}),
            "prospect_intelligence": result.get("prospect_intelligence", {}),
            "execution_plan": result.get("execution_plan", []),
            "trigger_score": result.get("trigger_score", company.trigger_score),
            "industry_score": result.get("industry_score", company.industry_score),
            "employee_score": result.get("employee_score", company.employee_score),
            "approval_status": "approved",
        }

    except Exception as e:
        db.rollback()
        print(f"[APPROVE ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{company_id}/reject")
def reject_company(company_id: UUID, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.status = "rejected"
    company.approval_status = "rejected"
    db.commit()

    return {"approval_status": "rejected", "status": "rejected"}


@router.post("/{company_id}/re-score")
def rescore_company(company_id: UUID, request: ReScoreRequest, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    state = {
        "company_url": company.website,
        "extracted_triggers": [],
        "raw_content": "",
        "company_name": company.name or "",
        "industry": company.industry or "",
        "employee_count": company.employee_count or 0,
        "icp_criteria": request.icp_criteria,
    }

    try:
        result = rescore(state, request.icp_criteria)

        company.icp_score = float(result.get("qualification_score", 0))
        company.qualified = result.get("is_qualified", False)
        db.commit()

        return result

    except Exception as e:
        db.rollback()
        print(f"[RESCORE ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/{pipeline_id}")
def get_pipeline_status(pipeline_id: str):
    """Return the current stage-by-stage progress of a pipeline."""
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    stages = get_pipeline_stages_list(pipeline_id)
    return {
        "pipeline_id": pipeline_id,
        "url": pipeline.get("url"),
        "completed": pipeline.get("completed", False),
        "error": pipeline.get("error"),
        "current_stage": pipeline.get("current_stage"),
        "stages": stages,
        "activities": pipeline.get("activities", []),
    }
