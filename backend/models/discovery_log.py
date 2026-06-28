import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy import UUID
from database import Base

class DiscoveryLog(Base):
    __tablename__ = "discovery_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_source = Column(String, nullable=True)
    status = Column(String, nullable=True)
    companies_found = Column(Integer, nullable=True)
    
    # Execution Timing
    trigger_time = Column(Float, nullable=True)
    icp_time = Column(Float, nullable=True)
    summary_time = Column(Float, nullable=True)
    contacts_time = Column(Float, nullable=True)
    total_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
