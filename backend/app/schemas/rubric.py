from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.models import StudentRole

class RubricTemplateBase(BaseModel):
    role: StudentRole
    name: str
    max_points: int
    criteria: Dict[str, Any]
    deductions: Optional[Dict[str, Any]] = None

class RubricTemplateCreate(RubricTemplateBase):
    pass

class RubricTemplate(RubricTemplateBase):
    id: int
    version: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
