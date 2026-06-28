from sqlalchemy.orm import Session
from models.discovery_log import DiscoveryLog
from database import SessionLocal

def log_discovery_step(status: str, input_source: str = "manual", companies_found: int = 0):
    print(f"[DISCOVERY LOG] {status}")
    db: Session = SessionLocal()
    try:
        log_entry = DiscoveryLog(
            input_source=input_source,
            status=status,
            companies_found=companies_found
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"[DISCOVERY LOG ERROR] Failed to save log: {e}")
        db.rollback()
    finally:
        db.close()
