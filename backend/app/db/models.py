from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

class UserRole(str, enum.Enum):
    INSTRUCTOR = "instructor"
    TA = "ta"

class StudentRole(str, enum.Enum):
    TT = "TT"  # Table Topic
    TM = "TM"  # Toastmaster
    CAMERA = "Camera"  # Camera Assistant
    SMT = "SMT"  # Six Minute Talk
    LEAD = "Lead"  # Group Lead
    REPORTER = "Reporter"  # Group Reporter

class GradingStatus(str, enum.Enum):
    NOT_GRADED = "not_graded"
    IN_PROGRESS = "in_progress"
    GRADED = "graded"
    SENT = "sent"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TA)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course_enrollments = relationship("CourseEnrollment", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)  # e.g., "ME 4611"
    section = Column(String)
    semester = Column(String)  # e.g., "Fall 2025"
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = relationship("CourseEnrollment", back_populates="course")
    students = relationship("Student", back_populates="course")
    sessions = relationship("ClassSession", back_populates="course")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TA)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="course_enrollments")
    course = relationship("Course", back_populates="enrollments")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    student_id = Column(String)  # University ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="students")
    role_assignments = relationship("RoleAssignment", back_populates="student")
    grade_records = relationship("GradeRecord", back_populates="student")

class ClassSession(Base):
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_number = Column(Integer, nullable=False)  # Week/Class number
    session_date = Column(DateTime, nullable=False)
    title = Column(String)  # e.g., "Practice", "Exp 1", "Exp 2"
    experiment_title = Column(String)  # e.g., "Time Constant", "Clapeyron"
    description = Column(Text)
    is_lab_day = Column(Boolean, default=True)  # False for "Labor Day", "Practice"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="sessions")
    role_assignments = relationship("RoleAssignment", back_populates="session")
    grade_records = relationship("GradeRecord", back_populates="session")

class RoleAssignment(Base):
    __tablename__ = "role_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    role = Column(SQLEnum(StudentRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="role_assignments")
    session = relationship("ClassSession", back_populates="role_assignments")

class RubricTemplate(Base):
    __tablename__ = "rubric_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(SQLEnum(StudentRole), unique=True, nullable=False)
    name = Column(String, nullable=False)
    max_points = Column(Integer, nullable=False)
    criteria = Column(JSON, nullable=False)  # Structured criteria data
    deductions = Column(JSON)  # Possible deductions
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grade_records = relationship("GradeRecord", back_populates="rubric_template")

class GradeRecord(Base):
    __tablename__ = "grade_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    rubric_template_id = Column(Integer, ForeignKey("rubric_templates.id"), nullable=False)
    
    # Scores
    criterion_scores = Column(JSON, nullable=False)  # {"criterion_id": score}
    deductions = Column(JSON)  # Applied deductions
    feedback_names = Column(JSON)  # {"criterion_id": "student_name"} for feedback fields
    comments = Column(Text)
    
    # Calculated totals
    raw_score = Column(Float, nullable=False)
    deduction_total = Column(Float, default=0)
    final_score = Column(Float, nullable=False)
    
    # Status and metadata
    status = Column(SQLEnum(GradingStatus), default=GradingStatus.NOT_GRADED)
    graded_by_id = Column(Integer, ForeignKey("users.id"))
    graded_at = Column(DateTime)
    
    # Snapshot for historical record
    rubric_snapshot = Column(JSON)  # Complete rubric at time of grading
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="grade_records")
    session = relationship("ClassSession", back_populates="grade_records")
    rubric_template = relationship("RubricTemplate", back_populates="grade_records")
    graded_by = relationship("User")
    email_logs = relationship("EmailLog", back_populates="grade_record")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    grade_record_id = Column(Integer, ForeignKey("grade_records.id"), nullable=False)
    recipient_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="sent")  # sent, failed, pending
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    grade_record = relationship("GradeRecord", back_populates="email_logs")
