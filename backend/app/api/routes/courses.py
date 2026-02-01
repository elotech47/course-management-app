from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import course
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=course.Course)
def create_course(
    course_data: course.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Create course
    db_course = models.Course(**course_data.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # Enroll the creator as instructor
    enrollment = models.CourseEnrollment(
        user_id=current_user.id,
        course_id=db_course.id,
        role=models.UserRole.INSTRUCTOR
    )
    db.add(enrollment)
    db.commit()
    
    return db_course

@router.get("/", response_model=List[course.CourseWithStats])
def get_courses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    # Get courses where user is enrolled
    enrollments = db.query(models.CourseEnrollment).filter(
        models.CourseEnrollment.user_id == current_user.id
    ).all()
    
    course_ids = [e.course_id for e in enrollments]
    courses = db.query(models.Course).filter(
        models.Course.id.in_(course_ids)
    ).offset(skip).limit(limit).all()
    
    # Add stats
    result = []
    for c in courses:
        student_count = db.query(models.Student).filter(
            models.Student.course_id == c.id,
            models.Student.is_active == True
        ).count()
        
        session_count = db.query(models.ClassSession).filter(
            models.ClassSession.course_id == c.id
        ).count()
        
        result.append({
            **c.__dict__,
            "student_count": student_count,
            "session_count": session_count
        })
    
    return result

@router.get("/{course_id}", response_model=course.Course)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check enrollment
    enrollment = db.query(models.CourseEnrollment).filter(
        models.CourseEnrollment.user_id == current_user.id,
        models.CourseEnrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return db_course

@router.put("/{course_id}", response_model=course.Course)
def update_course(
    course_id: int,
    course_data: course.CourseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user is instructor
    enrollment = db.query(models.CourseEnrollment).filter(
        models.CourseEnrollment.user_id == current_user.id,
        models.CourseEnrollment.course_id == course_id,
        models.CourseEnrollment.role == models.UserRole.INSTRUCTOR
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can update course"
        )
    
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update fields
    for field, value in course_data.model_dump(exclude_unset=True).items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    
    return db_course

@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user is instructor
    enrollment = db.query(models.CourseEnrollment).filter(
        models.CourseEnrollment.user_id == current_user.id,
        models.CourseEnrollment.course_id == course_id,
        models.CourseEnrollment.role == models.UserRole.INSTRUCTOR
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can delete course"
        )
    
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Soft delete
    db_course.is_active = False
    db.commit()
    
    return {"message": "Course deleted successfully"}
