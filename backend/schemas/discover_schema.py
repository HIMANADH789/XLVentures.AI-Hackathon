from pydantic import BaseModel
from typing import List, Optional
from schemas.contact_schema import ContactBase

class CompanyInput(BaseModel):
    url: str
    source: Optional[str] = "manual"

class DiscoverRequest(BaseModel):
    company_inputs: List[CompanyInput]
    force_refresh: Optional[bool] = False

class DiscoverResponse(BaseModel):
    company: Optional[str] = None
    trigger: Optional[str] = None
    score: Optional[int] = None
    summary: Optional[str] = None
    contacts: List[ContactBase] = []
    status: Optional[str] = None
