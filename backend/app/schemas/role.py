from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import StudentRole

class RoleAssignmentBase(BaseModel):
    student_id: int
    session_id: int
    role: StudentRole

class RoleAssignmentCreate(RoleAssignmentBase):
    pass

class RoleAssignmentBulk(BaseModel):
    session_id: int
    assignments: list[dict]  # [{"student_id": 1, "role": "TT"}, ...]

class RoleAssignment(RoleAssignmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleAssignmentWithDetails(RoleAssignment):
    student_name: str
    student_email: str
    session_date: datetime
    session_title: Optional[str] = None
