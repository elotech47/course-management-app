from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.models import GradingStatus

class GradeRecordBase(BaseModel):
    student_id: int
    session_id: int
    rubric_template_id: int
    criterion_scores: Dict[str, float]
    deductions: Optional[Dict[str, float]] = None
    feedback_names: Optional[Dict[str, str]] = None
    comments: Optional[str] = None

class GradeRecordCreate(GradeRecordBase):
    pass

class GradeRecordUpdate(BaseModel):
    criterion_scores: Optional[Dict[str, float]] = None
    deductions: Optional[Dict[str, float]] = None
    feedback_names: Optional[Dict[str, str]] = None
    comments: Optional[str] = None
    status: Optional[GradingStatus] = None

class GradeRecord(GradeRecordBase):
    id: int
    raw_score: float
    deduction_total: float
    final_score: float
    status: GradingStatus
    graded_by_id: Optional[int] = None
    graded_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class GradeRecordWithDetails(GradeRecord):
    student_name: str
    student_email: str
    session_date: datetime
    session_title: Optional[str] = None
    role: str
    rubric_name: str
    rubric_snapshot: Optional[Dict[str, Any]] = None

class GradingSummary(BaseModel):
    student_id: int
    student_name: str
    total_score: float
    graded_sessions: int
    role_breakdown: Dict[str, float]
