import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, TypeDecorator
from sqlalchemy import UUID
from database import Base

from sqlalchemy.orm import relationship


class JSONColumn(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    website = Column(String, unique=True, nullable=True)
    industry = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    
    # Trigger Info
    trigger_type = Column(String, nullable=True)
    trigger_source = Column(String, nullable=True)
    trigger_confidence = Column(Float, nullable=True)
    contact_confidence = Column(Float, nullable=True)
    summary_confidence = Column(Float, nullable=True)
    
    # ICP Info
    icp_score = Column(Float, nullable=True)
    qualified = Column(Boolean, nullable=True)
    
    # Score breakdown (from LLM analysis)
    trigger_score = Column(Float, nullable=True)
    industry_score = Column(Float, nullable=True)
    employee_score = Column(Float, nullable=True)
    
    # Enrichment results (stored as JSON)
    recommended_action = Column(JSONColumn, nullable=True)
    execution_plan = Column(JSONColumn, nullable=True)
    prospect_intelligence = Column(JSONColumn, nullable=True)
    
    # Content
    summary = Column(String, nullable=True)
    
    # Pipeline State
    status = Column(String, nullable=True, default="discovered")
    approval_status = Column(String, nullable=True, default="pending")
    
    # Firecrawl & News API integration fields
    firecrawl_used = Column(Boolean, nullable=True, default=False)
    news_used = Column(Boolean, nullable=True, default=False)
    news_headlines = Column(String, nullable=True)
    discovery_timestamp = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan", lazy="joined")
