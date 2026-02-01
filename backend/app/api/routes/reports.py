from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from app.db.database import get_db
from app.db import models
from app.schemas import grade
from app.core.security import get_current_user
from app.api.routes.students import check_course_access

router = APIRouter()

@router.get("/course/{course_id}/summary", response_model=List[grade.GradingSummary])
def get_course_grading_summary(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    # Get all students in course
    students = db.query(models.Student).filter(
        models.Student.course_id == course_id,
        models.Student.is_active == True
    ).all()
    
    result = []
    
    for student in students:
        # Get all grades
        grades = db.query(models.GradeRecord).filter(
            models.GradeRecord.student_id == student.id,
            models.GradeRecord.status == models.GradingStatus.GRADED
        ).all()
        
        total_score = sum(g.final_score for g in grades)
        graded_sessions = len(grades)
        
        # Breakdown by role
        role_breakdown = {}
        for grade_record in grades:
            # Get role assignment
            assignment = db.query(models.RoleAssignment).filter(
                models.RoleAssignment.student_id == student.id,
                models.RoleAssignment.session_id == grade_record.session_id
            ).first()
            
            if assignment:
                role = assignment.role.value
                if role not in role_breakdown:
                    role_breakdown[role] = 0
                role_breakdown[role] += grade_record.final_score
        
        result.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "total_score": total_score,
            "graded_sessions": graded_sessions,
            "role_breakdown": role_breakdown
        })
    
    # Sort by total score descending
    result.sort(key=lambda x: x["total_score"], reverse=True)
    
    return result

@router.get("/course/{course_id}/grade-sheet")
def get_course_grade_sheet(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns grade data formatted like the Excel sheet with sessions as columns
    """
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    # Get all students and sessions
    students = db.query(models.Student).filter(
        models.Student.course_id == course_id,
        models.Student.is_active == True
    ).order_by(models.Student.full_name).all()
    
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id
    ).order_by(models.ClassSession.session_date).all()
    
    # Build session headers with dates
    session_headers = []
    for session in sessions:
        session_headers.append({
            "id": session.id,
            "date": session.session_date.strftime('%m/%d/%y'),
            "session_number": session.session_number,
            "title": session.title or ""
        })
    
    # Build student rows
    student_data = []
    for student in students:
        row = {
            "student_id": student.id,
            "student_name": student.full_name,
            "student_number": student.student_id or "",
            "sessions": [],
            "role_totals": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
            "role_counts": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
            "total_score": 0
        }
        
        # Get grades for each session
        for session in sessions:
            assignment = db.query(models.RoleAssignment).filter(
                models.RoleAssignment.student_id == student.id,
                models.RoleAssignment.session_id == session.id
            ).first()
            
            grade = db.query(models.GradeRecord).filter(
                models.GradeRecord.student_id == student.id,
                models.GradeRecord.session_id == session.id,
                models.GradeRecord.status == models.GradingStatus.GRADED
            ).first()
            
            role_value = assignment.role.value if assignment else None
            score_value = grade.final_score if grade else None
            
            row["sessions"].append({
                "session_id": session.id,
                "role": role_value,
                "score": score_value
            })
            
            # Accumulate role totals (obtained scores) and counts
            if grade and assignment:
                role = assignment.role.value
                row["role_totals"][role] += grade.final_score
                row["role_counts"][role] += 1
                row["total_score"] += grade.final_score
        
        student_data.append(row)
    
    return {
        "session_headers": session_headers,
        "students": student_data
    }

@router.get("/student/{student_id}/summary")
def get_student_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get student
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    check_course_access(student.course_id, current_user.id, db)
    
    # Get all grades
    grades = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == student_id,
        models.GradeRecord.status == models.GradingStatus.GRADED
    ).all()
    
    # Get all sessions
    total_sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == student.course_id,
        models.ClassSession.is_lab_day == True
    ).count()
    
    # Build detailed breakdown
    grade_details = []
    role_totals = {}
    
    for grade_record in grades:
        session = db.query(models.ClassSession).filter(
            models.ClassSession.id == grade_record.session_id
        ).first()
        
        assignment = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.student_id == student_id,
            models.RoleAssignment.session_id == grade_record.session_id
        ).first()
        
        role = assignment.role.value if assignment else "Unknown"
        
        grade_details.append({
            "session_number": session.session_number if session else 0,
            "session_date": session.session_date if session else None,
            "session_title": session.title if session else "",
            "session_id": grade_record.session_id,
            "role": role,
            "score": grade_record.final_score,
            "max_points": grade_record.rubric_snapshot.get("max_points", 0) if grade_record.rubric_snapshot else 0
        })
        
        # Aggregate by role
        if role not in role_totals:
            role_totals[role] = {"count": 0, "total": 0, "max": 0}
        
        role_totals[role]["count"] += 1
        role_totals[role]["total"] += grade_record.final_score
        if grade_record.rubric_snapshot:
            role_totals[role]["max"] += grade_record.rubric_snapshot.get("max_points", 0)
    
    # Calculate overall stats
    total_score = sum(g.final_score for g in grades)
    graded_sessions = len(grades)
    
    return {
        "student": {
            "id": student.id,
            "name": student.full_name,
            "email": student.email,
            "student_id": student.student_id,
            "course_id": student.course_id
        },
        "summary": {
            "total_score": total_score,
            "graded_sessions": graded_sessions,
            "total_sessions": total_sessions,
            "completion_rate": (graded_sessions / total_sessions * 100) if total_sessions > 0 else 0
        },
        "role_breakdown": role_totals,
        "grade_details": sorted(grade_details, key=lambda x: x["session_number"])
    }

@router.get("/student/{student_id}/grade-sheet")
def get_student_grade_sheet(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns grade data for a single student formatted like the Excel sheet
    """
    # Get student
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    check_course_access(student.course_id, current_user.id, db)
    
    # Get all sessions for the course
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == student.course_id
    ).order_by(models.ClassSession.session_date).all()
    
    # Build session headers with dates
    session_headers = []
    for session in sessions:
        session_headers.append({
            "id": session.id,
            "date": session.session_date.strftime('%m/%d/%y'),
            "session_number": session.session_number,
            "title": session.title or ""
        })
    
    # Build student row
    student_row = {
        "student_id": student.id,
        "student_name": student.full_name,
        "student_number": student.student_id or "",
        "sessions": [],
        "role_totals": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
        "role_counts": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
        "total_score": 0
    }
    
    # Get grades for each session
    for session in sessions:
        assignment = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.student_id == student.id,
            models.RoleAssignment.session_id == session.id
        ).first()
        
        grade = db.query(models.GradeRecord).filter(
            models.GradeRecord.student_id == student.id,
            models.GradeRecord.session_id == session.id,
            models.GradeRecord.status == models.GradingStatus.GRADED
        ).first()
        
        role_value = assignment.role.value if assignment else None
        score_value = grade.final_score if grade else None
        
        student_row["sessions"].append({
            "session_id": session.id,
            "role": role_value,
            "score": score_value
        })
        
        # Accumulate role totals (obtained scores) and counts
        if grade and assignment:
            role = assignment.role.value
            student_row["role_totals"][role] += grade.final_score
            student_row["role_counts"][role] += 1
            student_row["total_score"] += grade.final_score
    
    return {
        "student_id": student_row["student_id"],
        "student_name": student_row["student_name"],
        "student_number": student_row["student_number"],
        "sessions": student_row["sessions"],
        "role_totals": student_row["role_totals"],
        "role_counts": student_row["role_counts"],
        "total_score": student_row["total_score"],
        "session_headers": session_headers
    }

@router.get("/course/{course_id}/role-stats")
def get_role_statistics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    # Get all grade records for the course
    grades = db.query(models.GradeRecord).join(
        models.Student
    ).filter(
        models.Student.course_id == course_id,
        models.GradeRecord.status == models.GradingStatus.GRADED
    ).all()
    
    role_stats = {}
    
    for grade_record in grades:
        # Get role
        assignment = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.student_id == grade_record.student_id,
            models.RoleAssignment.session_id == grade_record.session_id
        ).first()
        
        if not assignment:
            continue
        
        role = assignment.role.value
        
        if role not in role_stats:
            role_stats[role] = {
                "count": 0,
                "total_score": 0,
                "scores": [],
                "max_points": grade_record.rubric_snapshot.get("max_points", 0) if grade_record.rubric_snapshot else 0
            }
        
        role_stats[role]["count"] += 1
        role_stats[role]["total_score"] += grade_record.final_score
        role_stats[role]["scores"].append(grade_record.final_score)
    
    # Calculate statistics
    result = {}
    for role, data in role_stats.items():
        scores = data["scores"]
        result[role] = {
            "count": data["count"],
            "total_score": data["total_score"],
            "max_points": data["max_points"],
            "average": data["total_score"] / data["count"] if data["count"] > 0 else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0
        }
    
    return result
