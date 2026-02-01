from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import session
from app.core.security import get_current_user
from app.api.routes.students import check_course_access

router = APIRouter()

@router.post("/", response_model=session.ClassSession)
def create_session(
    session_data: session.ClassSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(session_data.course_id, current_user.id, db)
    
    # Create session
    db_session = models.ClassSession(**session_data.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/course/{course_id}", response_model=List[session.ClassSessionWithAssignments])
def get_course_sessions(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id
    ).order_by(models.ClassSession.session_date).all()
    
    result = []
    for s in sessions:
        assignment_count = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.session_id == s.id
        ).count()
        
        graded_count = db.query(models.GradeRecord).filter(
            models.GradeRecord.session_id == s.id,
            models.GradeRecord.status == models.GradingStatus.GRADED
        ).count()
        
        result.append({
            **s.__dict__,
            "assignment_count": assignment_count,
            "graded_count": graded_count
        })
    
    return result

@router.get("/{session_id}", response_model=session.ClassSession)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access
    check_course_access(db_session.course_id, current_user.id, db)
    
    return db_session

@router.put("/{session_id}", response_model=session.ClassSession)
def update_session(
    session_id: int,
    session_data: session.ClassSessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access
    check_course_access(db_session.course_id, current_user.id, db)
    
    # Update fields
    for field, value in session_data.model_dump(exclude_unset=True).items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access
    check_course_access(db_session.course_id, current_user.id, db)
    
    # Delete all related data
    # Delete grade records first (they reference role assignments)
    db.query(models.GradeRecord).filter(
        models.GradeRecord.session_id == session_id
    ).delete()
    
    # Delete role assignments
    db.query(models.RoleAssignment).filter(
        models.RoleAssignment.session_id == session_id
    ).delete()
    
    # Delete the session itself
    db.delete(db_session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

# Role assignment endpoints
@router.post("/{session_id}/assignments", response_model=List[dict])
def assign_roles(
    session_id: int,
    assignments: List[dict],  # [{"student_id": 1, "role": "TT"}, ...]
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access
    check_course_access(db_session.course_id, current_user.id, db)
    
    # For each assignment, update if exists or create new
    created = []
    for assignment in assignments:
        # Check if assignment already exists for this student and session
        existing = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.session_id == session_id,
            models.RoleAssignment.student_id == assignment["student_id"]
        ).first()
        
        if existing:
            # Update existing assignment
            existing.role = models.StudentRole(assignment["role"])
        else:
            # Create new assignment
            db_assignment = models.RoleAssignment(
                session_id=session_id,
                student_id=assignment["student_id"],
                role=models.StudentRole(assignment["role"])
            )
            db.add(db_assignment)
        
        created.append(assignment)
    
    db.commit()
    
    return created

@router.get("/{session_id}/assignments", response_model=List[dict])
def get_session_assignments(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access
    check_course_access(db_session.course_id, current_user.id, db)
    
    assignments = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.session_id == session_id
    ).all()
    
    result = []
    for assignment in assignments:
        student = db.query(models.Student).filter(
            models.Student.id == assignment.student_id
        ).first()
        
        result.append({
            "id": assignment.id,
            "student_id": assignment.student_id,
            "student_name": student.full_name if student else "",
            "role": assignment.role.value
        })
    
    return result
