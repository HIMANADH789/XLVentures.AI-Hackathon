from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class ContactBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "Manual"

class ContactResponse(ContactBase):
    id: UUID
    company_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ContactEnrichmentRequest(BaseModel):
    company_domain: str
