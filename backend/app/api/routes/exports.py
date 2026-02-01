from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime
from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user
from app.api.routes.students import check_course_access
from app.services.pdf_generator import generate_rubric_pdf

router = APIRouter()

@router.get("/course/{course_id}/grades.csv")
def export_course_grades_csv(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    # Get course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    
    # Get all students
    students = db.query(models.Student).filter(
        models.Student.course_id == course_id,
        models.Student.is_active == True
    ).order_by(models.Student.full_name).all()
    
    # Get all sessions
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id
    ).order_by(models.ClassSession.session_date).all()
    
    # Build CSV data matching the Excel format
    csv_rows = []
    
    for student in students:
        # Add student name header
        csv_rows.append([f"STUDENT NAME: {student.full_name.upper()}"])
        csv_rows.append([])  # Empty row
        
        # Add column headers
        csv_rows.append(["DATES", "TT", "TM", "CAMERA", "SMT", "LEAD", "REPORTER", "TOTAL SCORE"])
        
        # Track role totals and counts
        role_totals = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        role_counts = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        role_max_points = {"TT": 40, "TM": 40, "Camera": 40, "SMT": 240, "Lead": 200, "Reporter": 200}
        
        # Add session rows
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
            
            # Create row with date
            row = [session.session_date.strftime('%m/%d/%y'), "-", "-", "-", "-", "-", "-", "-"]
            
            if assignment:
                role = assignment.role.value
                role_counts[role] += 1  # Count how many times they had this role
                
                if grade:
                    score = round(grade.final_score)
                    role_totals[role] += score
                    
                    # Put score in the appropriate column
                    if role == "TT":
                        row[1] = score
                    elif role == "TM":
                        row[2] = score
                    elif role == "Camera":
                        row[3] = score
                    elif role == "SMT":
                        row[4] = score
                    elif role == "Lead":
                        row[5] = score
                    elif role == "Reporter":
                        row[6] = score
                    
                    row[7] = score  # Total score for this session
            
            csv_rows.append(row)
        
        # Calculate maximum possible scores (count × max_points)
        role_max_totals = {role: role_counts[role] * role_max_points[role] for role in role_totals.keys()}
        total_max = sum(role_max_totals.values())
        total_obtained = sum(role_totals.values())
        
        # Add Total Score row (maximum possible)
        csv_rows.append([
            "Total Score",
            role_max_totals["TT"],
            role_max_totals["TM"],
            role_max_totals["Camera"],
            role_max_totals["SMT"],
            role_max_totals["Lead"],
            role_max_totals["Reporter"],
            total_max
        ])
        
        # Add Obtained Score row (actual earned)
        csv_rows.append([
            "Obtained Score",
            role_totals["TT"],
            role_totals["TM"],
            role_totals["Camera"],
            role_totals["SMT"],
            role_totals["Lead"],
            role_totals["Reporter"],
            total_obtained
        ])
        
        # Add spacing between students
        csv_rows.append([])
        csv_rows.append([])
    
    # Convert to CSV
    output = io.StringIO()
    import csv
    writer = csv.writer(output)
    writer.writerows(csv_rows)
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={course.code}_grades_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

@router.get("/course/{course_id}/grades.xlsx")
def export_course_grades_excel(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    # Check access
    check_course_access(course_id, current_user.id, db)
    
    # Get course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    
    # Get all students
    students = db.query(models.Student).filter(
        models.Student.course_id == course_id,
        models.Student.is_active == True
    ).order_by(models.Student.full_name).all()
    
    # Get all sessions
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id
    ).order_by(models.ClassSession.session_date).all()
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Grades"
    
    # Define styles
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    total_fill = PatternFill(start_color="FFE4E1", end_color="FFE4E1", fill_type="solid")
    total_font = Font(bold=True, color="FF0000")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    current_row = 1
    
    for student in students:
        # Student name header
        cell = ws.cell(row=current_row, column=1)
        cell.value = f"STUDENT NAME: {student.full_name.upper()}"
        cell.font = Font(bold=True, size=12)
        current_row += 2
        
        # Column headers
        headers = ["DATES", "TT", "TM", "CAMERA", "SMT", "LEAD", "REPORTER", "TOTAL SCORE"]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=current_row, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = border
        current_row += 1
        
        # Track role totals and counts
        role_totals = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        role_counts = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        role_max_points = {"TT": 40, "TM": 40, "Camera": 40, "SMT": 240, "Lead": 200, "Reporter": 200}
        
        # Session rows
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
            
            # Date column
            ws.cell(row=current_row, column=1).value = session.session_date.strftime('%m/%d/%y')
            
            # Initialize all role columns with "-"
            for col in range(2, 8):
                cell = ws.cell(row=current_row, column=col)
                cell.value = "-"
                cell.alignment = center_align
                cell.border = border
            
            if assignment:
                role = assignment.role.value
                role_counts[role] += 1  # Count how many times they had this role
                
                if grade:
                    score = round(grade.final_score)
                    role_totals[role] += score
                    
                    # Put score in the appropriate column
                    col_map = {"TT": 2, "TM": 3, "Camera": 4, "SMT": 5, "Lead": 6, "Reporter": 7}
                    if role in col_map:
                        cell = ws.cell(row=current_row, column=col_map[role])
                        cell.value = score
                        cell.alignment = center_align
                        cell.border = border
                    
                    # Total score
                    cell = ws.cell(row=current_row, column=8)
                    cell.value = score
                    cell.alignment = center_align
                    cell.border = border
            
            ws.cell(row=current_row, column=1).border = border
            current_row += 1
        
        # Calculate maximum possible scores (count × max_points)
        role_max_totals = {role: role_counts[role] * role_max_points[role] for role in role_totals.keys()}
        total_max = sum(role_max_totals.values())
        total_obtained = sum(role_totals.values())
        
        # Total Score row (maximum possible)
        cell = ws.cell(row=current_row, column=1)
        cell.value = "Total Score"
        cell.font = total_font
        cell.fill = total_fill
        cell.border = border
        
        for col, role in enumerate(["TT", "TM", "Camera", "SMT", "Lead", "Reporter"], start=2):
            cell = ws.cell(row=current_row, column=col)
            cell.value = role_max_totals[role]
            cell.font = total_font
            cell.fill = total_fill
            cell.alignment = center_align
            cell.border = border
        
        cell = ws.cell(row=current_row, column=8)
        cell.value = total_max
        cell.font = total_font
        cell.fill = total_fill
        cell.alignment = center_align
        cell.border = border
        current_row += 1
        
        # Obtained Score row (actual earned)
        cell = ws.cell(row=current_row, column=1)
        cell.value = "Obtained Score"
        cell.border = border
        
        for col, role in enumerate(["TT", "TM", "Camera", "SMT", "Lead", "Reporter"], start=2):
            cell = ws.cell(row=current_row, column=col)
            cell.value = role_totals[role]
            cell.alignment = center_align
            cell.border = border
        
        cell = ws.cell(row=current_row, column=8)
        cell.value = total_obtained
        cell.alignment = center_align
        cell.border = border
        current_row += 3  # Add spacing between students
    
    # Auto-size columns
    for col in range(1, 9):
        ws.column_dimensions[chr(64 + col)].width = 15
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={course.code}_grades_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )

@router.get("/student/{student_id}/grades.xlsx")
def export_student_grades_excel(
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
    
    # Get all sessions for the course
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == student.course_id
    ).order_by(models.ClassSession.session_date).all()
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Build data rows
        excel_rows = []
        
        # Add student name header
        excel_rows.append([f"STUDENT NAME: {student.full_name.upper()}"])
        excel_rows.append([])  # Empty row
        
        # Add column headers
        excel_rows.append(["DATES", "TT", "TM", "CAMERA", "SMT", "LEAD", "REPORTER", "TOTAL SCORE"])
        
        # Track role totals and counts
        role_totals = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        role_counts = {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0}
        
        # Add session rows
        for session in sessions:
            assignment = db.query(models.RoleAssignment).filter(
                models.RoleAssignment.student_id == student_id,
                models.RoleAssignment.session_id == session.id
            ).first()
            
            grade = db.query(models.GradeRecord).filter(
                models.GradeRecord.student_id == student_id,
                models.GradeRecord.session_id == session.id,
                models.GradeRecord.status == models.GradingStatus.GRADED
            ).first()
            
            row = [session.session_date.strftime('%m/%d/%y')]
            
            # Add scores for each role column
            for role in ["TT", "TM", "Camera", "SMT", "Lead", "Reporter"]:
                if assignment and assignment.role.value == role and grade:
                    score = int(round(grade.final_score))
                    row.append(score)
                    role_totals[role] += grade.final_score
                    role_counts[role] += 1
                else:
                    row.append("-")
            
            # Session total score
            session_score = int(round(grade.final_score)) if grade else "-"
            row.append(session_score)
            excel_rows.append(row)
        
        # Role max points
        role_max_points = {
            "TT": 40,
            "TM": 40,
            "Camera": 40,
            "SMT": 480,
            "Lead": 400,
            "Reporter": 400
        }
        
        # Calculate total possible and obtained scores
        total_possible = sum(role_counts[role] * role_max_points[role] for role in role_max_points)
        total_obtained = sum(role_totals.values())
        
        # Add Total Score row (max possible per role)
        total_score_row = ["Total Score"]
        for role in ["TT", "TM", "Camera", "SMT", "Lead", "Reporter"]:
            total_score_row.append(role_counts[role] * role_max_points[role])
        total_score_row.append(int(round(total_possible)))
        excel_rows.append(total_score_row)
        
        # Add Obtained Score row
        obtained_score_row = ["Obtained Score"]
        for role in ["TT", "TM", "Camera", "SMT", "Lead", "Reporter"]:
            obtained_score_row.append(int(round(role_totals[role])))
        obtained_score_row.append(int(round(total_obtained)))
        excel_rows.append(obtained_score_row)
        
        # Create DataFrame
        df = pd.DataFrame(excel_rows)
        df.to_excel(writer, sheet_name='Grades', index=False, header=False)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={student.full_name.replace(' ', '_')}_Grades_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )

@router.get("/student/{student_id}/session/{session_id}/rubric.pdf")
def export_student_session_rubric_pdf(
    student_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a PDF of the graded rubric for a specific student and session
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
    
    # Get session
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get grade record
    grade = db.query(models.GradeRecord).filter(
        models.GradeRecord.student_id == student_id,
        models.GradeRecord.session_id == session_id,
        models.GradeRecord.status == models.GradingStatus.GRADED
    ).first()
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found for this student and session"
        )
    
    # Get role assignment
    assignment = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.student_id == student_id,
        models.RoleAssignment.session_id == session_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    # Generate PDF
    pdf_buffer = generate_rubric_pdf(
        student_name=student.full_name,
        session_title=session.title or f"Session {session.session_number}",
        session_date=session.session_date.strftime('%m/%d/%Y'),
        role=assignment.role.value,
        rubric_snapshot=grade.rubric_snapshot,
        criterion_scores=grade.criterion_scores,
        deductions=grade.deductions or {},
        feedback_names=grade.feedback_names or {},
        raw_score=grade.raw_score,
        deduction_total=grade.deduction_total,
        final_score=grade.final_score
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={student.full_name.replace(' ', '_')}_Session{session.session_number}_{assignment.role.value}_Rubric.pdf"
        }
    )

