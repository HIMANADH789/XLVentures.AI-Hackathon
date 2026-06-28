from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models.company import Company
from models.contact import Contact
from schemas.company_schema import CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies

@router.get("/{company_id}")
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    contacts = db.query(Contact).filter(Contact.company_id == company.id).all()
    
    company_dict = {c.name: getattr(company, c.name) for c in company.__table__.columns}
    contacts_list = [{c.name: getattr(contact, c.name) for c in contact.__table__.columns} for contact in contacts]
    
    return {
        **company_dict,
        "contacts": contacts_list
    }
