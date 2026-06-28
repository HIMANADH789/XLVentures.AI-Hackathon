import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models.company import Company
from models.contact import Contact
import uuid
import json

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Company).count() > 0:
        print("Data already seeded.")
        return
        
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_dataset", "10_companies.json")
    
    with open(dataset_path, "r") as f:
        companies = json.load(f)

    for c_data in companies:
        company = Company(**c_data)
        db.add(company)
        db.flush()
        
        if company.qualified:
            contact = Contact(
                company_id=company.id,
                name=f"Admin {company.name.split()[0]}",
                role="Sales Leader",
                email=f"admin@{company.website.split('//')[1]}",
                linkedin="linkedin.com/in/admin",
                phone="555-1234"
            )
            db.add(contact)
            
    db.commit()
    db.close()
    print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed_data()
