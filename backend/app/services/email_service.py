from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings
from app.services.email_template import generate_rubric_html
import logging

logger = logging.getLogger(__name__)

def send_graded_rubric_email(
    recipient_email: str,
    recipient_name: str,
    course_name: str,
    session_info: dict,
    role: str,
    rubric_data: dict,
    criterion_scores: dict,
    deductions: Optional[dict],
    comments: Optional[str],
    final_score: float
) -> bool:
    """
    Send graded rubric email to student
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    if not settings.SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured. Email not sent.")
        # In development, just return True and log
        logger.info(f"Would send email to {recipient_email}")
        logger.info(f"Subject: Your Grade for {session_info.get('title', 'Session')}")
        return True
    
    try:
        # Generate HTML content
        html_content = generate_rubric_html(
            student_name=recipient_name,
            course_name=course_name,
            session_info=session_info,
            role=role,
            rubric_data=rubric_data,
            criterion_scores=criterion_scores,
            deductions=deductions,
            comments=comments,
            final_score=final_score
        )
        
        # Create email
        message = Mail(
            from_email=Email(settings.FROM_EMAIL, settings.FROM_NAME),
            to_emails=To(recipient_email),
            subject=f"Your Grade for {course_name} - {session_info.get('title', 'Session')}",
            html_content=Content("text/html", html_content)
        )
        
        # Send email
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Email sent to {recipient_email}. Status: {response.status_code}")
        
        return response.status_code in [200, 201, 202]
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False

def send_bulk_graded_rubrics(grade_records: list) -> dict:
    """
    Send multiple graded rubric emails
    
    Returns:
        dict: Summary of sent emails
    """
    results = {
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    for record in grade_records:
        try:
            success = send_graded_rubric_email(
                recipient_email=record["student_email"],
                recipient_name=record["student_name"],
                course_name=record["course_name"],
                session_info=record["session_info"],
                role=record["role"],
                rubric_data=record["rubric_data"],
                criterion_scores=record["criterion_scores"],
                deductions=record["deductions"],
                comments=record["comments"],
                final_score=record["final_score"]
            )
            
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "email": record["student_email"],
                    "error": "Failed to send"
                })
                
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "email": record.get("student_email", "unknown"),
                "error": str(e)
            })
    
    return results
