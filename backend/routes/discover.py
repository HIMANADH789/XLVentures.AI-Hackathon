from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.discover_schema import DiscoverRequest
from services.orchestrator import process_discovery

router = APIRouter(prefix="/discover", tags=["Discovery"])

@router.post("")
def discover(request: DiscoverRequest, db: Session = Depends(get_db)):
    if not request.company_inputs:
        raise HTTPException(status_code=400, detail="company_inputs cannot be empty")
        
    results = process_discovery(request.company_inputs, request.force_refresh, db)
    if len(results) == 1:
        return results[0]
    return results
