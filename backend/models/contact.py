import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy import UUID
from database import Base

from sqlalchemy.orm import relationship

class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint('company_id', 'email', name='uix_company_email'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True, default="Manual")
    
    company = relationship("Company", back_populates="contacts")
