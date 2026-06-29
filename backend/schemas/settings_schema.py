from pydantic import BaseModel
from typing import Optional


class IcpSettings(BaseModel):
    industry: str = "Software / AI / SaaS / Tech"
    min_employees: int = 10
    max_employees: int = 0
    qualification_threshold: int = 60


class PersonaSettings(BaseModel):
    default: list[str] = ["Founder", "VP Sales", "Head of Growth"]
    options: list[str] = [
        "Founder",
        "VP Sales",
        "Head of Growth",
        "CEO",
        "CTO",
        "VP Engineering",
        "Chief Revenue Officer",
        "SVP Sales",
        "Director of Sales",
    ]


class SettingsResponse(BaseModel):
    icp: IcpSettings
    personas: PersonaSettings
