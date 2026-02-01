from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import student
from app.core.security import get_current_user

router = APIRouter()

def check_course_access(course_id: int, user_id: int, db: Session):
    """Helper to check if user has access to course"""
    enrollment = db.query(models.CourseEnrollment).filter(
        models.CourseEnrollment.user_id == user_id,
        models.CourseEnrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    return enrollment

@router.post("/", response_model=student.Student)
def create_student(
    student_data: student.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(student_data.course_id, current_user.id, db)
    
    # Check if student already exists
    existing = db.query(models.Student).filter(
        models.Student.course_id == student_data.course_id,
        models.Student.email == student_data.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists in the course"
        )
    
    # Create student
    db_student = models.Student(**student_data.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    return db_student

@router.post("/bulk", response_model=List[student.Student])
def bulk_import_students(
    import_data: student.StudentBulkImport,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(import_data.course_id, current_user.id, db)
    
    created_students = []
    
    for student_data in import_data.students:
        # Skip if already exists
        existing = db.query(models.Student).filter(
            models.Student.course_id == import_data.course_id,
            models.Student.email == student_data.email
        ).first()
        
        if existing:
            continue
        
        db_student = models.Student(
            course_id=import_data.course_id,
            **student_data.model_dump()
        )
        db.add(db_student)
        created_students.append(db_student)
    
    db.commit()
    
    for s in created_students:
        db.refresh(s)
    
    return created_students

@router.get("/course/{course_id}", response_model=List[student.Student])
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    include_inactive: bool = False
):
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    query = db.query(models.Student).filter(models.Student.course_id == course_id)
    
    if not include_inactive:
        query = query.filter(models.Student.is_active == True)
    
    return query.all()

@router.get("/{student_id}", response_model=student.StudentWithGrades)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    check_course_access(db_student.course_id, current_user.id, db)
    
    # Calculate grades
    grades = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == student_id,
        models.GradeRecord.status == models.GradingStatus.GRADED
    ).all()
    
    total_grade = sum(g.final_score for g in grades)
    graded_sessions = len(grades)
    
    total_sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == db_student.course_id,
        models.ClassSession.is_lab_day == True
    ).count()
    
    return {
        **db_student.__dict__,
        "total_grade": total_grade,
        "graded_sessions": graded_sessions,
        "total_sessions": total_sessions
    }

@router.put("/{student_id}", response_model=student.Student)
def update_student(
    student_id: int,
    student_data: student.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    check_course_access(db_student.course_id, current_user.id, db)
    
    # Update fields
    for field, value in student_data.model_dump(exclude_unset=True).items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    
    return db_student

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    check_course_access(db_student.course_id, current_user.id, db)
    
    # Soft delete
    db_student.is_active = False
    db.commit()
    
    return {"message": "Student deleted successfully"}
