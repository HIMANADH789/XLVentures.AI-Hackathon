from fastapi import APIRouter
from schemas.contact_schema import ContactEnrichmentRequest
from services.company_service import enrich_contacts
from utils.normalizer import normalize_role

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("")
def get_contacts(request: ContactEnrichmentRequest):
    contacts = enrich_contacts(request.company_domain)
    for c in contacts:
        c["role"] = normalize_role(c.get("role"))
    return contacts
