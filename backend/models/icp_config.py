import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import UUID, JSON
from database import Base

class IcpConfig(Base):
    __tablename__ = "icp_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry = Column(String, nullable=True)
    employee_min = Column(Integer, nullable=True)
    employee_max = Column(Integer, nullable=True)
    target_roles = Column(JSON, nullable=True)
    trigger_types = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
