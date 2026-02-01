from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClassSessionBase(BaseModel):
    course_id: int
    session_number: int
    session_date: datetime
    title: Optional[str] = None
    experiment_title: Optional[str] = None
    description: Optional[str] = None
    is_lab_day: bool = True

class ClassSessionCreate(ClassSessionBase):
    pass

class ClassSessionUpdate(BaseModel):
    session_number: Optional[int] = None
    session_date: Optional[datetime] = None
    title: Optional[str] = None
    experiment_title: Optional[str] = None
    description: Optional[str] = None
    is_lab_day: Optional[bool] = None

class ClassSession(ClassSessionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassSessionWithAssignments(ClassSession):
    assignment_count: int
    graded_count: int
