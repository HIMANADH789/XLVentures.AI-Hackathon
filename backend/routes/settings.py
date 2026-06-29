from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.settings_schema import IcpSettings, PersonaSettings, SettingsResponse
from models.icp_config import IcpConfig

router = APIRouter(prefix="/settings", tags=["Settings"])


DEFAULT_ICP = IcpSettings()
DEFAULT_PERSONAS = PersonaSettings()


@router.get("/icp", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    config = db.query(IcpConfig).order_by(IcpConfig.created_at.desc()).first()

    if config:
        icp = IcpSettings(
            industry=config.industry or DEFAULT_ICP.industry,
            min_employees=config.employee_min or DEFAULT_ICP.min_employees,
            max_employees=config.employee_max or DEFAULT_ICP.max_employees,
            qualification_threshold=60,
        )
        personas = PersonaSettings(
            default=config.target_roles or DEFAULT_PERSONAS.default,
            options=DEFAULT_PERSONAS.options,
        )
        return SettingsResponse(icp=icp, personas=personas)

    return SettingsResponse(icp=DEFAULT_ICP, personas=DEFAULT_PERSONAS)


@router.put("/icp", response_model=SettingsResponse)
def update_icp(icp: IcpSettings, db: Session = Depends(get_db)):
    config = db.query(IcpConfig).order_by(IcpConfig.created_at.desc()).first()
    if config:
        config.industry = icp.industry
        config.employee_min = icp.min_employees
        config.employee_max = icp.max_employees
    else:
        config = IcpConfig(
            industry=icp.industry,
            employee_min=icp.min_employees,
            employee_max=icp.max_employees,
        )
        db.add(config)

    db.commit()

    return SettingsResponse(icp=icp, personas=DEFAULT_PERSONAS)


@router.put("/personas", response_model=SettingsResponse)
def update_personas(personas: PersonaSettings, db: Session = Depends(get_db)):
    config = db.query(IcpConfig).order_by(IcpConfig.created_at.desc()).first()
    if config:
        config.target_roles = personas.default
    else:
        config = IcpConfig(target_roles=personas.default)
        db.add(config)

    db.commit()

    icp = IcpSettings()
    if config and config.industry:
        icp = IcpSettings(
            industry=config.industry,
            min_employees=config.employee_min or DEFAULT_ICP.min_employees,
            max_employees=config.employee_max or DEFAULT_ICP.max_employees,
            qualification_threshold=60,
        )

    return SettingsResponse(icp=icp, personas=personas)
