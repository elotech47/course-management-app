from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.db import models
from app.schemas import grade
from app.core.security import get_current_user
from app.api.routes.students import check_course_access
from app.services.email_service import send_graded_rubric_email

router = APIRouter()

def calculate_grade(criterion_scores: dict, deductions: dict = None, role: str = None) -> tuple:
    """Calculate raw score, deduction total, and final score
    
    For TT and TM roles, the rubric subsections total 60 points but max score is 40.
    Apply scaling: (score / 60) * 40
    """
    raw_score = sum(criterion_scores.values())
    
    # Apply scaling for TT and TM, and Camera roles (60 points -> 40 points)
    if role in ["TT", "TM", "Camera"]:
        raw_score = (raw_score / 60.0) * 40.0
    
    deduction_total = sum(deductions.values()) if deductions else 0
    final_score = max(0, raw_score - deduction_total)
    
    return raw_score, deduction_total, final_score

@router.post("/", response_model=grade.GradeRecord)
def create_grade_record(
    grade_data: grade.GradeRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get student and check course access
    student = db.query(models.Student).filter(
        models.Student.id == grade_data.student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Get session
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == grade_data.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get rubric template
    rubric = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.id == grade_data.rubric_template_id
    ).first()
    
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric template not found"
        )
    
    # Verify role assignment exists for this student and session
    role_assignment = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.student_id == grade_data.student_id,
        models.RoleAssignment.session_id == grade_data.session_id
    ).first()
    
    if not role_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No role assigned for this student in this session. Please assign a role first."
        )
    
    # Check if grade already exists
    existing = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == grade_data.student_id,
        models.GradeRecord.session_id == grade_data.session_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade record already exists for this student and session"
        )
    
    # Calculate scores with role-based scaling
    raw_score, deduction_total, final_score = calculate_grade(
        grade_data.criterion_scores,
        grade_data.deductions,
        role=rubric.role.value
    )
    
    # Create rubric snapshot
    rubric_snapshot = {
        "role": rubric.role.value,
        "name": rubric.name,
        "max_points": rubric.max_points,
        "criteria": rubric.criteria,
        "deductions": rubric.deductions,
        "version": rubric.version
    }
    
    # Create grade record
    db_grade = models.GradeRecord(
        student_id=grade_data.student_id,
        session_id=grade_data.session_id,
        rubric_template_id=grade_data.rubric_template_id,
        criterion_scores=grade_data.criterion_scores,
        deductions=grade_data.deductions,
        feedback_names=grade_data.feedback_names,
        comments=grade_data.comments,
        raw_score=raw_score,
        deduction_total=deduction_total,
        final_score=final_score,
        status=models.GradingStatus.GRADED,
        graded_by_id=current_user.id,
        graded_at=datetime.utcnow(),
        rubric_snapshot=rubric_snapshot
    )
    
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    
    return db_grade

@router.get("/session/{session_id}", response_model=List[grade.GradeRecordWithDetails])
def get_session_grades(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get session and check access
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    check_course_access(session.course_id, current_user.id, db)
    
    # Get all grades for this session
    grades = db.query(models.GradeRecord).filter(
        models.GradeRecord.session_id == session_id
    ).all()
    
    result = []
    for g in grades:
        student = db.query(models.Student).filter(
            models.Student.id == g.student_id
        ).first()
        
        rubric = db.query(models.RubricTemplate).filter(
            models.RubricTemplate.id == g.rubric_template_id
        ).first()
        
        # Get role assignment
        assignment = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.student_id == g.student_id,
            models.RoleAssignment.session_id == session_id
        ).first()
        
        result.append({
            **g.__dict__,
            "student_name": student.full_name if student else "",
            "student_email": student.email if student else "",
            "session_date": session.session_date,
            "session_title": session.title,
            "role": assignment.role.value if assignment else "",
            "rubric_name": rubric.name if rubric else ""
        })
    
    return result

@router.get("/student/{student_id}", response_model=List[grade.GradeRecordWithDetails])
def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get student and check access
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Get all grades for this student
    grades = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == student_id
    ).order_by(models.GradeRecord.graded_at.desc()).all()
    
    result = []
    for g in grades:
        session = db.query(models.ClassSession).filter(
            models.ClassSession.id == g.session_id
        ).first()
        
        rubric = db.query(models.RubricTemplate).filter(
            models.RubricTemplate.id == g.rubric_template_id
        ).first()
        
        # Get role assignment
        assignment = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.student_id == student_id,
            models.RoleAssignment.session_id == g.session_id
        ).first()
        
        result.append({
            **g.__dict__,
            "student_name": student.full_name,
            "student_email": student.email,
            "session_date": session.session_date if session else None,
            "session_title": session.title if session else "",
            "role": assignment.role.value if assignment else "",
            "rubric_name": rubric.name if rubric else ""
        })
    
    return result

@router.get("/student/{student_id}/session/{session_id}", response_model=grade.GradeRecord)
def get_student_session_grade(
    student_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific grade for a student in a session"""
    # Get student and check access
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Get the grade
    grade_record = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == student_id,
        models.GradeRecord.session_id == session_id
    ).first()
    
    if not grade_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found for this student and session"
        )
    
    return grade_record

@router.get("/{grade_id}", response_model=grade.GradeRecordWithDetails)
def get_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_grade = db.query(models.GradeRecord).filter(
        models.GradeRecord.id == grade_id
    ).first()
    
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    # Check access
    student = db.query(models.Student).filter(
        models.Student.id == db_grade.student_id
    ).first()
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Get related data
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == db_grade.session_id
    ).first()
    
    rubric = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.id == db_grade.rubric_template_id
    ).first()
    
    assignment = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.student_id == db_grade.student_id,
        models.RoleAssignment.session_id == db_grade.session_id
    ).first()
    
    return {
        **db_grade.__dict__,
        "student_name": student.full_name,
        "student_email": student.email,
        "session_date": session.session_date if session else None,
        "session_title": session.title if session else "",
        "role": assignment.role.value if assignment else "",
        "rubric_name": rubric.name if rubric else ""
    }

@router.put("/{grade_id}", response_model=grade.GradeRecord)
def update_grade(
    grade_id: int,
    grade_data: grade.GradeRecordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_grade = db.query(models.GradeRecord).filter(
        models.GradeRecord.id == grade_id
    ).first()
    
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    # Check access
    student = db.query(models.Student).filter(
        models.Student.id == db_grade.student_id
    ).first()
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Update scores if provided
    if grade_data.criterion_scores:
        db_grade.criterion_scores = grade_data.criterion_scores
    
    if grade_data.deductions is not None:
        db_grade.deductions = grade_data.deductions
    
    # Recalculate if scores changed
    if grade_data.criterion_scores or grade_data.deductions is not None:
        # Get rubric to determine role for scaling
        rubric = db.query(models.RubricTemplate).filter(
            models.RubricTemplate.id == db_grade.rubric_template_id
        ).first()
        
        raw_score, deduction_total, final_score = calculate_grade(
            db_grade.criterion_scores,
            db_grade.deductions,
            role=rubric.role.value if rubric else None
        )
        db_grade.raw_score = raw_score
        db_grade.deduction_total = deduction_total
        db_grade.final_score = final_score
    
    # Update other fields
    if grade_data.comments is not None:
        db_grade.comments = grade_data.comments
    
    if grade_data.feedback_names is not None:
        db_grade.feedback_names = grade_data.feedback_names
    
    if grade_data.status:
        db_grade.status = grade_data.status
    
    db_grade.graded_by_id = current_user.id
    db_grade.graded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_grade)
    
    return db_grade

@router.delete("/{grade_id}")
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_grade = db.query(models.GradeRecord).filter(
        models.GradeRecord.id == grade_id
    ).first()
    
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    # Check access
    student = db.query(models.Student).filter(
        models.Student.id == db_grade.student_id
    ).first()
    
    check_course_access(student.course_id, current_user.id, db)
    
    db.delete(db_grade)
    db.commit()
    
    return {"message": "Grade deleted successfully"}

@router.post("/{grade_id}/send-email")
def send_grade_email(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Send graded rubric email to student"""
    
    db_grade = db.query(models.GradeRecord).filter(
        models.GradeRecord.id == grade_id
    ).first()
    
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    # Check access
    student = db.query(models.Student).filter(
        models.Student.id == db_grade.student_id
    ).first()
    
    check_course_access(student.course_id, current_user.id, db)
    
    # Get related data
    course = db.query(models.Course).filter(
        models.Course.id == student.course_id
    ).first()
    
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == db_grade.session_id
    ).first()
    
    rubric = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.id == db_grade.rubric_template_id
    ).first()
    
    assignment = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.student_id == db_grade.student_id,
        models.RoleAssignment.session_id == db_grade.session_id
    ).first()
    
    # Send email
    try:
        success = send_graded_rubric_email(
            recipient_email=student.email,
            recipient_name=student.full_name,
            course_name=f"{course.code} - {course.name}",
            session_info={
                "title": session.title or f"Class {session.session_number}",
                "date": session.session_date.strftime("%B %d, %Y")
            },
            role=assignment.role.value if assignment else "Unknown",
            rubric_data=db_grade.rubric_snapshot or rubric.__dict__,
            criterion_scores=db_grade.criterion_scores,
            deductions=db_grade.deductions,
            comments=db_grade.comments,
            final_score=db_grade.final_score
        )
        
        if success:
            # Log email
            email_log = models.EmailLog(
                grade_record_id=grade_id,
                recipient_email=student.email,
                subject=f"Your Grade for {course.code} - {session.title or 'Session'}",
                status="sent"
            )
            db.add(email_log)
            
            # Update grade status
            db_grade.status = models.GradingStatus.SENT
            
            db.commit()
            
            return {"message": "Email sent successfully", "recipient": student.email}
        else:
            # Log failure
            email_log = models.EmailLog(
                grade_record_id=grade_id,
                recipient_email=student.email,
                subject=f"Your Grade for {course.code} - {session.title or 'Session'}",
                status="failed",
                error_message="Failed to send email"
            )
            db.add(email_log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        # Log error
        email_log = models.EmailLog(
            grade_record_id=grade_id,
            recipient_email=student.email,
            subject=f"Your Grade for {course.code}",
            status="failed",
            error_message=str(e)
        )
        db.add(email_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )

@router.post("/session/{session_id}/send-all-emails")
def send_all_session_emails(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Send graded rubric emails to all students in a session"""
    
    # Get session and check access
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    check_course_access(session.course_id, current_user.id, db)
    
    # Get all graded records for this session
    grades = db.query(models.GradeRecord).filter(
        models.GradeRecord.session_id == session_id,
        models.GradeRecord.status == models.GradingStatus.GRADED
    ).all()
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    for db_grade in grades:
        try:
            # Get student
            student = db.query(models.Student).filter(
                models.Student.id == db_grade.student_id
            ).first()
            
            # Get course
            course = db.query(models.Course).filter(
                models.Course.id == student.course_id
            ).first()
            
            # Get rubric
            rubric = db.query(models.RubricTemplate).filter(
                models.RubricTemplate.id == db_grade.rubric_template_id
            ).first()
            
            # Get assignment
            assignment = db.query(models.RoleAssignment).filter(
                models.RoleAssignment.student_id == db_grade.student_id,
                models.RoleAssignment.session_id == session_id
            ).first()
            
            # Send email
            success = send_graded_rubric_email(
                recipient_email=student.email,
                recipient_name=student.full_name,
                course_name=f"{course.code} - {course.name}",
                session_info={
                    "title": session.title or f"Class {session.session_number}",
                    "date": session.session_date.strftime("%B %d, %Y")
                },
                role=assignment.role.value if assignment else "Unknown",
                rubric_data=db_grade.rubric_snapshot or rubric.__dict__,
                criterion_scores=db_grade.criterion_scores,
                deductions=db_grade.deductions,
                comments=db_grade.comments,
                final_score=db_grade.final_score
            )
            
            # Log result
            email_log = models.EmailLog(
                grade_record_id=db_grade.id,
                recipient_email=student.email,
                subject=f"Your Grade for {course.code} - {session.title or 'Session'}",
                status="sent" if success else "failed"
            )
            db.add(email_log)
            
            if success:
                db_grade.status = models.GradingStatus.SENT
                sent_count += 1
            else:
                failed_count += 1
                errors.append({"student": student.full_name, "error": "Failed to send"})
                
        except Exception as e:
            failed_count += 1
            errors.append({"student": student.full_name if student else "Unknown", "error": str(e)})
    
    db.commit()
    
    return {
        "message": f"Sent {sent_count} emails, {failed_count} failed",
        "sent": sent_count,
        "failed": failed_count,
        "errors": errors
    }
