import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy import UUID
from database import Base

from sqlalchemy.orm import relationship

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
    
    # Content
    summary = Column(String, nullable=True)
    
    # Pipeline State
    status = Column(String, nullable=True, default="discovered")
    
    # Firecrawl & News API integration fields
    firecrawl_used = Column(Boolean, nullable=True, default=False)
    news_used = Column(Boolean, nullable=True, default=False)
    news_headlines = Column(String, nullable=True)
    discovery_timestamp = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan", lazy="joined")
