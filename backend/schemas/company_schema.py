from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from schemas.contact_schema import ContactResponse
from datetime import datetime

class CompanyBase(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    trigger_type: Optional[str] = None
    trigger_source: Optional[str] = None
    trigger_confidence: Optional[float] = None
    contact_confidence: Optional[float] = None
    summary_confidence: Optional[float] = None
    icp_score: Optional[float] = None
    qualified: Optional[bool] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    firecrawl_used: Optional[bool] = None
    news_used: Optional[bool] = None
    news_headlines: Optional[str] = None
    discovery_timestamp: Optional[datetime] = None

class CompanyResponse(CompanyBase):
    id: UUID
    contacts: Optional[List[ContactResponse]] = []
    model_config = ConfigDict(from_attributes=True)
