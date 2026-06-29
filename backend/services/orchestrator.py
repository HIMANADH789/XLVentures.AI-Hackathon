from sqlalchemy.orm import Session
from datetime import datetime
import os
from services.company_service import enrich_contacts, scrape_employee_count
from models.company import Company
from models.contact import Contact
from models.discovery_log import DiscoveryLog
from utils.normalizer import normalize_trigger_type, normalize_role
from utils.logger import log_discovery_step
from urllib.parse import urlparse
import traceback
import time
from config import settings
from services.news_service import search_news
from services.ai_service import analyze_company_pipeline
from agents.tools.scraper import discover_and_scrape, _scrape_page
from services.pipeline_tracker import (
    start_stage, complete_stage, fail_stage,
    complete_pipeline, fail_pipeline,
)

def _collect_discovery_data(url: str, db=None, pipeline_id: str = None) -> dict:
    """Collect website content, news, and contacts for a given URL.
    
    This is the shared data collection step for both the legacy orchestrator
    and the new LangGraph-based pipeline.
    Accepts optional pipeline_id to track sub-stage timing.
    """
    from datetime import datetime
    from urllib.parse import urlparse
    from services.news_service import search_news
    from agents.tools.scraper import discover_and_scrape, _scrape_page
    from services.pipeline_tracker import start_stage, complete_stage
    import os
    import time

    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path
    if domain.startswith("www."):
        domain = domain[4:]
    name_query = resolve_company_name(url)

    collected = {
        "website_content": "",
        "news_data": [],
        "contacts_data": [],
        "firecrawl_used": False,
        "news_used": False,
        "news_headlines": None,
        "domain": domain,
        "name_query": name_query,
    }

    # 1. Firecrawl / HTTP scrape
    if pipeline_id:
        start_stage(pipeline_id, "scraping")
    try:
        fc_key = settings.firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        website_content = discover_and_scrape(url)
        if fc_key:
            collected["firecrawl_used"] = True
        collected["website_content"] = website_content
    except Exception:
        try:
            collected["website_content"] = _scrape_page(None, url)
        except Exception:
            collected["website_content"] = ""
    if pipeline_id:
        complete_stage(pipeline_id, "scraping", f"Scraped {domain}")

    # 2. NewsAPI search
    if pipeline_id:
        start_stage(pipeline_id, "news_search")
    news_count = 0
    try:
        news_data = search_news(name_query)
        collected["news_data"] = news_data
        news_count = len(news_data)
        collected["news_used"] = news_count > 0
        headlines = [art.get("title") for art in news_data if art.get("title")]
        collected["news_headlines"] = " | ".join(headlines[:5]) if headlines else None
    except Exception:
        news_data = []
        collected["news_data"] = []
    if pipeline_id:
        complete_stage(pipeline_id, "news_search", f"Found {news_count} news articles")

    # 3. Hunter contact enrichment
    if pipeline_id:
        start_stage(pipeline_id, "contact_finding")
    contact_count = 0
    try:
        contacts_data = enrich_contacts(domain)
        collected["contacts_data"] = contacts_data
        contact_count = len(contacts_data)
    except Exception:
        contacts_data = []
        collected["contacts_data"] = []
    if pipeline_id:
        source = contacts_data[0].get("source", "Hunter") if contacts_data else "Hunter"
        complete_stage(pipeline_id, "contact_finding", f"Found {contact_count} contacts via {source}")

    # 4. bs4-based employee count scrape
    emp_count = scrape_employee_count(url)
    if emp_count:
        collected["employee_count"] = emp_count

    return collected


def resolve_company_name(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path
    if domain.startswith("www."):
        domain = domain[4:]
    parts = domain.split(".")
    if len(parts) >= 2:
        if parts[-2].lower() in ["co", "com", "net", "org", "edu", "gov"] and len(parts) >= 3:
            return parts[-3].capitalize()
        return parts[-2].capitalize()
    return parts[0].capitalize()

def process_discovery(company_inputs: list, force_refresh: bool, db: Session, pipeline_id: str = None) -> list:
    log_discovery_step(status="Discovery started", companies_found=len(company_inputs))
    results = []
    
    for c_input in company_inputs:
        url = c_input.url
        source = c_input.source
        
        try:
            total_start = time.time()
            
            if pipeline_id:
                start_stage(pipeline_id, "scraping")
            
            # Extract domain and name query
            parsed_url = urlparse(url)
            domain = parsed_url.netloc or parsed_url.path
            if domain.startswith("www."):
                domain = domain[4:]
            name_query = resolve_company_name(url)
            
            # Duplicate check
            if not force_refresh:
                existing_company = db.query(Company).filter(Company.website == url).first()
                if existing_company:
                    # Fetch existing contacts
                    existing_contacts = db.query(Contact).filter(Contact.company_id == existing_company.id).all()
                    results.append({
                        "company": existing_company.name,
                        "trigger": existing_company.trigger_type,
                        "score": existing_company.icp_score,
                        "summary": existing_company.summary,
                        "status": "existing",
                        "trigger_confidence": existing_company.trigger_confidence,
                        "contact_confidence": existing_company.contact_confidence,
                        "summary_confidence": existing_company.summary_confidence,
                        "firecrawl_used": existing_company.firecrawl_used,
                        "news_used": existing_company.news_used,
                        "news_headlines": existing_company.news_headlines,
                        "trigger_source": existing_company.trigger_source,
                        "discovery_timestamp": existing_company.discovery_timestamp.isoformat() if existing_company.discovery_timestamp else None,
                        "contacts": [
                            {
                                "name": c.name,
                                "role": c.role,
                                "email": c.email,
                                "linkedin": c.linkedin,
                                "phone": c.phone,
                                "source": c.source
                            } for c in existing_contacts
                        ]
                    })
                    continue
            
            # 1. Firecrawl Scrape Website Content
            t_fc_start = time.time()
            print(f"[PIPELINE] Firecrawl started for {url}")
            firecrawl_used = False
            try:
                fc_key = settings.firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
                website_content = discover_and_scrape(url)
                if fc_key:
                    firecrawl_used = True
            except Exception as e:
                print(f"[PIPELINE ERROR] Firecrawl failed: {e}. Falling back to raw HTTP scrape.")
                try:
                    website_content = _scrape_page(None, url)
                except Exception:
                    website_content = ""
            
            fc_duration = time.time() - t_fc_start
            print(f"[PIPELINE] Firecrawl completed in {fc_duration:.2f}s")
            log_discovery_step(status="Firecrawl completed")
            if pipeline_id:
                complete_stage(pipeline_id, "scraping")
                start_stage(pipeline_id, "news_search")
            
            # 2. NewsAPI Search Recent Articles
            t_news_start = time.time()
            print(f"[PIPELINE] News search started for query: {name_query}")
            news_used = False
            news_data = []
            try:
                news_data = search_news(name_query)
                news_used = len(news_data) > 0
            except Exception as e:
                print(f"[PIPELINE ERROR] News search failed: {e}")
                news_data = []
                
            news_duration = time.time() - t_news_start
            print(f"[PIPELINE] News search completed in {news_duration:.2f}s")
            log_discovery_step(status="News search completed")
            if pipeline_id:
                complete_stage(pipeline_id, "news_search")
                start_stage(pipeline_id, "contact_finding")
            
            headlines_list = [art.get("title") for art in news_data if art.get("title")]
            news_headlines_str = " | ".join(headlines_list[:5]) if headlines_list else None
            
            # 3. Hunter Contact Enrichment
            t_hunter_start = time.time()
            contacts_data = []
            try:
                contacts_data = enrich_contacts(domain)
            except Exception as e:
                print(f"[PIPELINE ERROR] Hunter enrichment failed: {e}")
                contacts_data = []
                
            hunter_duration = time.time() - t_hunter_start
            print(f"[PIPELINE] Hunter completed in {hunter_duration:.2f}s")
            if pipeline_id:
                complete_stage(pipeline_id, "contact_finding")
                start_stage(pipeline_id, "trigger_extraction")

            # bs4-based employee count scrape
            bs4_employee_count = scrape_employee_count(url)
            
            # 4. Groq Unified LLM Analysis
            t_groq_start = time.time()
            try:
                analysis = analyze_company_pipeline(url, website_content, news_data, contacts_data)
            except Exception as e:
                print(f"[PIPELINE ERROR] Groq analysis failed: {e}")
                raise e
                
            groq_duration = time.time() - t_groq_start
            print("[PIPELINE] Groq prompt generated")
            if pipeline_id:
                complete_stage(pipeline_id, "trigger_extraction")
                start_stage(pipeline_id, "icp_qualification")
            
            # 5. Save/Update Company
            is_new = True
            existing_company = db.query(Company).filter(Company.website == url).first()
            
            # Use LLM-generated contacts or fallback
            contacts_to_save = analysis.get("contacts") or contacts_data
            
            contact_conf = 0.9 if contacts_to_save else 0.0
            summary_conf = 0.85 if analysis.get("summary") else 0.0
            
            # Cast qualified to bool safely
            is_qualified_val = analysis.get("qualified")
            if isinstance(is_qualified_val, str):
                is_qualified = is_qualified_val.lower() == "true"
            else:
                is_qualified = bool(is_qualified_val)
                
            trigger_src = analysis.get("trigger_source") or source
            
            if existing_company:
                is_new = False
                company = existing_company
                company.name = analysis.get("company_name")
                company.trigger_type = normalize_trigger_type(analysis.get("trigger_event"))
                company.trigger_source = trigger_src
                company.trigger_confidence = analysis.get("trigger_confidence") or 0.8
                company.contact_confidence = contact_conf
                company.summary_confidence = summary_conf
                company.icp_score = float(analysis.get("icp_score") or 0)
                company.qualified = is_qualified
                company.summary = analysis.get("summary")
                company.status = "updated"
                company.industry = analysis.get("industry") or company.industry or "AI / SaaS"
                company.employee_count = analysis.get("employee_estimate") or bs4_employee_count or company.employee_count
                company.firecrawl_used = firecrawl_used
                company.news_used = news_used
                company.news_headlines = news_headlines_str
                company.discovery_timestamp = datetime.utcnow()
            else:
                company = Company(
                    name=analysis.get("company_name"),
                    website=url,
                    trigger_type=normalize_trigger_type(analysis.get("trigger_event")),
                    trigger_source=trigger_src,
                    trigger_confidence=analysis.get("trigger_confidence") or 0.8,
                    contact_confidence=contact_conf,
                    summary_confidence=summary_conf,
                    icp_score=float(analysis.get("icp_score") or 0),
                    qualified=is_qualified,
                    summary=analysis.get("summary"),
                    status="new",
                    industry=analysis.get("industry") or "AI / SaaS",
                    employee_count=analysis.get("employee_estimate") or bs4_employee_count,
                    firecrawl_used=firecrawl_used,
                    news_used=news_used,
                    news_headlines=news_headlines_str,
                    discovery_timestamp=datetime.utcnow()
                )
                db.add(company)
            
            if pipeline_id:
                complete_stage(pipeline_id, "icp_qualification")
                start_stage(pipeline_id, "saving")
            
            db.flush() # To get company.id or apply updates
            log_discovery_step(status="Company saved")
            
            # 6. Save Contacts
            saved_contacts = []
            for c_data in contacts_to_save:
                existing_contact = None
                if c_data.get("email"):
                    existing_contact = db.query(Contact).filter(
                        Contact.company_id == company.id,
                        Contact.email == c_data.get("email")
                    ).first()
                elif c_data.get("name"):
                    existing_contact = db.query(Contact).filter(
                        Contact.company_id == company.id,
                        Contact.name == c_data.get("name")
                    ).first()
                
                role_val = normalize_role(c_data.get("role"))
                
                # Check for fake/dummy email addresses
                email_val = c_data.get("email")
                if email_val and ("dummy" in email_val.lower() or "example" in email_val.lower() or "placeholder" in email_val.lower()):
                    email_val = None
                
                if existing_contact:
                    existing_contact.role = role_val
                    if c_data.get("linkedin"):
                        existing_contact.linkedin = c_data.get("linkedin")
                    if c_data.get("phone"):
                        existing_contact.phone = c_data.get("phone")
                    if c_data.get("source"):
                        existing_contact.source = c_data.get("source")
                    saved_contacts.append(existing_contact)
                    continue
                        
                contact = Contact(
                    company_id=company.id,
                    name=c_data.get("name"),
                    role=role_val,
                    email=email_val,
                    linkedin=c_data.get("linkedin"),
                    phone=c_data.get("phone"),
                    source=c_data.get("source") or "Manual"
                )
                db.add(contact)
                saved_contacts.append(contact)
            
            # Log execution timing
            total_time = time.time() - total_start
            print(f"[PIPELINE] Discovery finished in {total_time:.2f}s")
            
            log_entry = DiscoveryLog(
                input_source=source,
                status="completed",
                companies_found=1,
                trigger_time=fc_duration,
                icp_time=news_duration,
                summary_time=groq_duration,
                contacts_time=hunter_duration,
                total_time=total_time
            )
            db.add(log_entry)
            
            if pipeline_id:
                complete_stage(pipeline_id, "saving")
                complete_pipeline(pipeline_id)
            
            db.commit()
            log_discovery_step(status="Contacts saved")
            
            results.append({
                "company": company.name,
                "trigger": company.trigger_type,
                "score": company.icp_score,
                "summary": company.summary,
                "status": "new" if is_new else "updated",
                "trigger_confidence": company.trigger_confidence,
                "contact_confidence": company.contact_confidence,
                "summary_confidence": company.summary_confidence,
                "firecrawl_used": company.firecrawl_used,
                "news_used": company.news_used,
                "news_headlines": company.news_headlines,
                "trigger_source": company.trigger_source,
                "discovery_timestamp": company.discovery_timestamp.isoformat() if company.discovery_timestamp else None,
                "contacts": [
                    {
                        "name": c.name,
                        "role": c.role,
                        "email": c.email,
                        "linkedin": c.linkedin,
                        "phone": c.phone,
                        "source": c.source
                    } for c in saved_contacts
                ]
            })
            
        except Exception as e:
            db.rollback()
            if pipeline_id:
                fail_pipeline(pipeline_id, str(e))
            print(f"[ORCHESTRATOR ERROR] {e}")
            traceback.print_exc()
            results.append({
                "status": "partial",
                "error": str(e)
            })
            log_discovery_step(status=f"Discovery failed: {e}")
            
    log_discovery_step(status="Discovery completed", companies_found=len(results))
    return results
