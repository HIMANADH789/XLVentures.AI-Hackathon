from pydantic import BaseModel
from typing import List, Optional
from schemas.contact_schema import ContactBase
from datetime import datetime
from uuid import UUID


class CompanyInput(BaseModel):
    url: str
    source: Optional[str] = "manual"
    pipeline_id: Optional[str] = None


class DiscoverRequest(BaseModel):
    company_inputs: List[CompanyInput]
    force_refresh: Optional[bool] = False
    auto_approve: Optional[bool] = False
    pipeline_id: Optional[str] = None


class DiscoverResponse(BaseModel):
    company: Optional[str] = None
    trigger: Optional[str] = None
    score: Optional[int] = None
    summary: Optional[str] = None
    contacts: List[ContactBase] = []
    status: Optional[str] = None


class AnalysisResult(BaseModel):
    company_name: str = ""
    industry: str = ""
    employee_count: int = 0
    trigger_events: list = []
    trigger_score: int = 0
    industry_score: int = 0
    employee_score: int = 0
    qualification_score: int = 0
    is_qualified: bool = False
    summary: str = ""
    approval_status: str = "pending"


class ApproveRequest(BaseModel):
    company_id: UUID
    personas: Optional[List[str]] = None


class ApproveResponse(BaseModel):
    company_name: str = ""
    industry: str = ""
    employee_count: int = 0
    contacts: list = []
    summary: str = ""
    qualification_score: int = 0
    is_qualified: bool = False
    recommended_action: dict = {}
    prospect_intelligence: dict = {}
    execution_plan: list = []
    approval_status: str = "approved"


class RejectRequest(BaseModel):
    company_id: UUID


class RejectResponse(BaseModel):
    approval_status: str = "rejected"
    status: str = "rejected"


class ReScoreRequest(BaseModel):
    company_id: UUID
    icp_criteria: dict


class ReScoreResponse(BaseModel):
    qualification_score: int = 0
    is_qualified: bool = False
    trigger_score: int = 0
    industry_score: int = 0
    employee_score: int = 0
    summary: str = ""
