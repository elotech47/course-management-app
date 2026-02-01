from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    full_name: str
    email: EmailStr
    student_id: Optional[str] = None

class StudentCreate(StudentBase):
    course_id: int

class StudentBulkImport(BaseModel):
    course_id: int
    students: list[StudentBase]

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    student_id: Optional[str] = None
    is_active: Optional[bool] = None

class Student(StudentBase):
    id: int
    course_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentWithGrades(Student):
    total_grade: float
    graded_sessions: int
    total_sessions: int
